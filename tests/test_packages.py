# -*- coding: utf-8 -*-
"""
Testes unitários para o módulo de pacotes oficiais e verificação de checksums (automation.python.packages).
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from automation.python.credentials import generate_password
from automation.python.packages import (
    DEFAULT_CATALOG_PATH,
    ChecksumVerificationError,
    PackageNotFoundError,
    compute_sha256,
    load_package_catalog,
    verify_directory,
    verify_file_checksum,
)


class TestPackagesCatalog(unittest.TestCase):
    """Valida o catálogo de pacotes e a consistência dos metadados e hashes."""

    def test_catalog_exists_and_loads(self):
        """Verifica se o arquivo packages.json existe e carrega com formato válido."""
        catalog = load_package_catalog()
        self.assertIn("metadata", catalog)
        self.assertIn("packages", catalog)
        self.assertGreaterEqual(len(catalog["packages"]), 10)

    def test_catalog_checksums_format(self):
        """Verifica se todos os hashes SHA-256 no catálogo são válidos (64 caracteres hex)."""
        catalog = load_package_catalog()
        for pkg_id, pkg in catalog["packages"].items():
            sha = pkg.get("sha256")
            self.assertIsNotNone(sha, f"Pacote {pkg_id} não possui sha256.")
            self.assertEqual(len(sha), 64, f"Hash do pacote {pkg_id} não possui 64 caracteres.")
            self.assertTrue(
                all(c in "0123456789abcdef" for c in sha.lower()),
                f"Hash do pacote {pkg_id} contém caracteres não hexadecimais: {sha}",
            )

    def test_catalog_has_required_components(self):
        """Garante a presença dos componentes essenciais de KSC 16.3 e KESL."""
        catalog = load_package_catalog()
        packages = catalog["packages"]

        required_keys = [
            "ksc-server-16.3-pt-BR",
            "ksc-server-16.3-en",
            "ksc-web-console-16.3-pt-BR",
            "ksc-network-agent-16.3-pt-BR",
            "kesl-distributive-12.5",
            "kesl-gui-12.5",
        ]
        for key in required_keys:
            self.assertIn(key, packages, f"Chave obrigatória ausente no catálogo: {key}")
            self.assertTrue(packages[key]["url"].startswith("https://"))
            self.assertTrue(packages[key]["filename"].endswith((".rpm", ".tar.gz")))
            self.assertIn("path", packages[key])

    def test_checksums_sha256_file_consistency(self):
        """Valida que o arquivo configs/ksc/checksums.sha256 reflete o catálogo."""
        checksum_file = Path(DEFAULT_CATALOG_PATH).parent / "checksums.sha256"
        self.assertTrue(checksum_file.is_file(), f"Arquivo não encontrado: {checksum_file}")

        catalog = load_package_catalog()
        catalog_hashes = {pkg["sha256"].lower() for pkg in catalog["packages"].values()}
        file_hashes = set()

        with open(checksum_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    sha = parts[0].lstrip("#").lower()
                    file_hashes.add(sha)
                    self.assertIn(
                        sha,
                        catalog_hashes,
                        f"Hash no checksums.sha256 ({sha}) não encontrado no catálogo.",
                    )
        self.assertEqual(
            file_hashes,
            catalog_hashes,
            "Todos os hashes do catálogo devem estar ativos no checksums.sha256",
        )


class TestChecksumVerification(unittest.TestCase):
    """Testa os cálculos de hash SHA-256 e validação de arquivos."""

    def test_compute_sha256(self):
        """Valida o cálculo do hash contra a biblioteca hashlib nativa."""
        content = b"Kaspersky Security Center 16.3 Test Payload"
        expected_hash = hashlib.sha256(content).hexdigest().lower()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            actual_hash = compute_sha256(tmp_path)
            self.assertEqual(actual_hash, expected_hash)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_verify_file_checksum_success(self):
        """Valida correspondência correta de hash."""
        content = b"Integrity Check Valid"
        valid_hash = hashlib.sha256(content).hexdigest()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            self.assertTrue(verify_file_checksum(tmp_path, valid_hash))
            self.assertTrue(verify_file_checksum(tmp_path, valid_hash.upper()))
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_verify_file_checksum_tampered(self):
        """Garante que adulteração é detectada e lança erro quando solicitado."""
        content = b"Authentic Payload"
        valid_hash = hashlib.sha256(content).hexdigest()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"Tampered or Corrupted Payload")
            tmp_path = tmp.name

        try:
            self.assertFalse(verify_file_checksum(tmp_path, valid_hash))
            with self.assertRaises(ChecksumVerificationError):
                verify_file_checksum(tmp_path, valid_hash, raise_on_error=True)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_verify_directory_categorization(self):
        """Valida a separação de arquivos verificados, corrompidos e não rastreados."""
        catalog = load_package_catalog()
        pkg = catalog["packages"]["ksc-server-16.3-pt-BR"]
        target_filename = pkg["filename"]
        target_sha = pkg["sha256"]

        with tempfile.TemporaryDirectory() as td:
            # 1. Arquivo não rastreado
            untracked_path = os.path.join(td, "extra_script.sh")
            with open(untracked_path, "w") as f:
                f.write("echo untracked")

            # 2. Arquivo corrompido (nome coincide, hash difere)
            corrupt_path = os.path.join(td, target_filename)
            with open(corrupt_path, "w") as f:
                f.write("bad rpm bytes")

            res = verify_directory(td, catalog=catalog)
            self.assertEqual(len(res["verified"]), 0)
            self.assertEqual(len(res["failed"]), 1)
            self.assertEqual(res["failed"][0]["file"], target_filename)
            self.assertEqual(len(res["untracked"]), 1)
            self.assertEqual(res["untracked"][0]["file"], "extra_script.sh")

    def test_verify_directory_nested_subdirectories(self):
        """Valida a verificação recursiva de pacotes em subdiretórios com caminhos relativos."""
        catalog = load_package_catalog()
        pkg = catalog["packages"]["ksc-server-16.3-pt-BR"]
        rel_path = pkg["path"]
        expected_sha = pkg["sha256"]

        with tempfile.TemporaryDirectory() as td:
            full_path = os.path.join(td, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "wb") as f:
                f.write(b"mock ksc payload")

            # Hash simulado
            import hashlib
            actual_sha = hashlib.sha256(b"mock ksc payload").hexdigest()
            catalog_copy = {
                "packages": {
                    "ksc-server-16.3-pt-BR": {
                        **pkg,
                        "sha256": actual_sha,
                    }
                }
            }

            res = verify_directory(td, catalog=catalog_copy)
            self.assertEqual(len(res["verified"]), 1)
            self.assertEqual(res["verified"][0]["file"], rel_path)
            self.assertEqual(res["verified"][0]["package_id"], "ksc-server-16.3-pt-BR")

    def test_download_package_not_found(self):
        """Garante erro explicativo para ID de pacote inexistente."""
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(PackageNotFoundError):
                from automation.python.packages import download_package

                download_package("non-existent-package-id", target_dir=td)

    @patch("automation.python.packages.urllib.request.urlopen")
    def test_download_package_success_and_timeout(self, mock_urlopen):
        """Valida que download_package usa timeout finito e grava arquivo via mkstemp."""
        import io
        from automation.python.packages import download_package

        payload = b"Mock RPM Content"
        mock_resp = io.BytesIO(payload)
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        mock_catalog = {
            "packages": {
                "test-pkg": {
                    "product": "Test Package",
                    "filename": "test-pkg.rpm",
                    "path": "test-sub/test-pkg.rpm",
                    "url": "https://example.com/test-pkg.rpm",
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
            }
        }

        with tempfile.TemporaryDirectory() as td:
            out_file = download_package(
                "test-pkg", target_dir=td, catalog=mock_catalog, verify=True
            )
            self.assertTrue(out_file.is_file())
            self.assertEqual(out_file.read_bytes(), payload)
            self.assertTrue(str(out_file).endswith("test-sub/test-pkg.rpm"))
            mock_urlopen.assert_called_once()
            _, kwargs = mock_urlopen.call_args
            self.assertEqual(kwargs.get("timeout"), 60)

    def test_install_ksc_server_invalid_packages_dir_raises(self):
        """Valida que install_ksc_server falha com SetupError se packages_dir apontar para diretório inexistente."""
        import logging
        from automation.python.config import KscConfig
        from automation.python.setup_steps import SetupError, install_ksc_server

        config = KscConfig(
            db_password=generate_password(),
            ksc_admin_password=generate_password(),
            packages_dir="/non/existent/path/for/ksc/packages",
        )
        logger = logging.getLogger("test")
        with self.assertRaises(SetupError):
            install_ksc_server(config, logger)

    def test_install_ksc_server_missing_packages_dir_raises(self):
        """Valida que install_ksc_server falha com SetupError se packages_dir não for configurado (fail-closed)."""
        import logging
        from automation.python.config import KscConfig
        from automation.python.setup_steps import SetupError, install_ksc_server

        config = KscConfig(
            db_password=generate_password(),
            ksc_admin_password=generate_password(),
            packages_dir=None,
        )
        logger = logging.getLogger("test")
        with self.assertRaises(SetupError):
            install_ksc_server(config, logger)

    def test_install_ksc_server_passes_gate_but_requires_rpms(self):
        """Um diretório vazio passa no gate de integridade e falha por ausência de RPM.

        Antes da desmockagem (R-01) este caso era considerado sucesso; com a
        instalação real, um diretório sem os pacotes oficiais não pode instalar
        coisa alguma.
        """
        import logging
        from automation.python.config import KscConfig
        from automation.python.setup_steps import SetupError, install_ksc_server

        with tempfile.TemporaryDirectory() as td:
            config = KscConfig(
                db_password=generate_password(),
                ksc_admin_password=generate_password(),
                packages_dir=td,
            )
            logger = logging.getLogger("test")
            with self.assertRaisesRegex(SetupError, "não encontrado"):
                install_ksc_server(config, logger)


class TestCliPackagesIntegration(unittest.TestCase):
    """Testa a integração do subcomando packages via kscctl CLI."""

    def run_kscctl(self, args: list) -> subprocess.CompletedProcess:
        cmd = [sys.executable, "-m", "automation.python.kscctl"] + args
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent)
        return subprocess.run(cmd, capture_output=True, text=True, env=env)

    def test_kscctl_packages_help(self):
        """Testa o help do subcomando packages."""
        result = self.run_kscctl(["packages", "--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("--list", result.stdout)
        self.assertIn("--verify-dir", result.stdout)
        self.assertIn("--download", result.stdout)

    def test_kscctl_packages_list(self):
        """Testa listagem de pacotes via CLI."""
        result = self.run_kscctl(["packages", "--list"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("ksc-server-16.3-pt-BR", result.stdout)
        self.assertIn("kesl-distributive-12.5", result.stdout)

    def test_kscctl_packages_verify_dir(self):
        """Testa verificação de diretório via CLI com saída formatada."""
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "notes.txt"), "w") as f:
                f.write("sample")

            result = self.run_kscctl(["packages", "--verify-dir", td])
            self.assertEqual(result.returncode, 0)
            self.assertIn("Verificação de integridade em:", result.stdout)
            self.assertIn("Pacotes verificados com sucesso: 0", result.stdout)
            self.assertIn("notes.txt", result.stdout)


if __name__ == "__main__":
    unittest.main()
