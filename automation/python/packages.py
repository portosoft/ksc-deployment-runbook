# -*- coding: utf-8 -*-
"""
Módulo de Catálogo e Verificação de Integridade de Pacotes Kaspersky.

Fornece carregamento do catálogo oficial de pacotes (packages.json), cálculo e
verificação de hashes criptográficos SHA-256, download seguro com verificação
em tempo de execução e rotinas para CLI (kscctl packages).
"""

import hashlib
import hmac
import json
import logging
import os
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

DEFAULT_CATALOG_PATH = (
    Path(__file__).resolve().parent.parent.parent / "configs" / "ksc" / "packages.json"
)
CHUNK_SIZE = 65536  # 64 KB

logger = logging.getLogger("ksc.packages")


class PackageError(Exception):
    """Exceção base para erros no gerenciamento de pacotes."""

    pass


class PackageNotFoundError(PackageError):
    """Lançada quando um ID de pacote não é encontrado no catálogo."""

    pass


class ChecksumVerificationError(PackageError):
    """Lançada quando a verificação do checksum SHA-256 falha."""

    pass


def load_package_catalog(
    catalog_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Carrega o catálogo oficial de pacotes a partir do arquivo JSON.

    Args:
        catalog_path: Caminho opcional para o packages.json. Se None, usa o padrão do repositório.

    Returns:
        Dicionário contendo os metadados e pacotes catalogados.

    Raises:
        FileNotFoundError: Se o arquivo do catálogo não existir.
        ValueError: Se o arquivo JSON for inválido ou não contiver a chave 'packages'.
    """
    path = Path(catalog_path) if catalog_path else DEFAULT_CATALOG_PATH
    if not path.is_file():
        raise FileNotFoundError(
            f"Arquivo de catálogo de pacotes não encontrado: {path}"
        )

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict) or "packages" not in data:
        raise ValueError(
            f"Formato de catálogo inválido em {path}: chave 'packages' ausente."
        )

    return data


def compute_sha256(file_path: Union[str, Path], chunk_size: int = CHUNK_SIZE) -> str:
    """Calcula o hash SHA-256 de um arquivo de forma eficiente em memória.

    Args:
        file_path: Caminho do arquivo a ser verificado.
        chunk_size: Tamanho do bloco de leitura em bytes (padrão: 64KB).

    Returns:
        String hexadecimal com o hash SHA-256 em letras minúsculas.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado para cálculo de hash: {path}")

    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest().lower()


def verify_file_checksum(
    file_path: Union[str, Path], expected_sha256: str, raise_on_error: bool = False
) -> bool:
    """Verifica se o arquivo corresponde ao checksum SHA-256 esperado.

    Usa hmac.compare_digest para mitigação de timing attacks.

    Args:
        file_path: Caminho do arquivo a ser verificado.
        expected_sha256: Hash SHA-256 esperado (case-insensitive).
        raise_on_error: Se True, lança ChecksumVerificationError em caso de divergência.

    Returns:
        True se o hash for idêntico, False caso contrário.

    Raises:
        ChecksumVerificationError: Se raise_on_error=True e o hash não coincidir.
    """
    actual_hash = compute_sha256(file_path)
    expected_clean = expected_sha256.strip().lower()

    matches = hmac.compare_digest(actual_hash, expected_clean)
    if not matches and raise_on_error:
        raise ChecksumVerificationError(
            f"Falha de integridade em '{file_path}':\n"
            f"  Esperado: {expected_clean}\n"
            f"  Obtido:   {actual_hash}"
        )
    return matches


def verify_directory(
    directory_path: Union[str, Path], catalog: Optional[Dict[str, Any]] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """Varre um diretório e valida os pacotes encontrados contra o catálogo oficial.

    Args:
        directory_path: Diretório contendo os arquivos baixados (.rpm, .tar.gz).
        catalog: Catálogo opcional carregado. Se None, carrega o padrão.

    Returns:
        Dicionário com categorias:
          - 'verified': Arquivos cujo hash corresponde com o catálogo.
          - 'failed': Arquivos reconhecidos cujo hash divergiu (potencialmente corrompidos/adulterados).
          - 'untracked': Arquivos no diretório não mapeados no catálogo.
    """
    dir_path = Path(directory_path)
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Diretório não encontrado: {dir_path}")

    if catalog is None:
        catalog = load_package_catalog()

    packages_by_filename: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
    for pkg_id, pkg_info in catalog["packages"].items():
        fname = pkg_info["filename"]
        packages_by_filename.setdefault(fname, []).append((pkg_id, pkg_info))

    results: Dict[str, List[Dict[str, Any]]] = {
        "verified": [],
        "failed": [],
        "untracked": [],
    }

    for item in sorted(dir_path.iterdir()):
        if not item.is_file():
            continue

        fname = item.name
        if fname in packages_by_filename:
            actual_sha = compute_sha256(item)
            matched = False
            for pkg_id, pkg_info in packages_by_filename[fname]:
                expected_sha = pkg_info["sha256"].lower()
                if hmac.compare_digest(actual_sha, expected_sha):
                    results["verified"].append(
                        {
                            "file": fname,
                            "path": str(item),
                            "package_id": pkg_id,
                            "product": pkg_info["product"],
                            "version": pkg_info["version"],
                            "sha256": actual_sha,
                        }
                    )
                    matched = True
                    break
            if not matched:
                results["failed"].append(
                    {
                        "file": fname,
                        "path": str(item),
                        "candidates": [pid for pid, _ in packages_by_filename[fname]],
                        "actual_sha256": actual_sha,
                    }
                )
        else:
            results["untracked"].append({"file": fname, "path": str(item)})

    return results


def download_package(
    package_id: str,
    target_dir: Union[str, Path],
    catalog: Optional[Dict[str, Any]] = None,
    verify: bool = True,
) -> Path:
    """Faz o download seguro de um pacote do portal oficial e valida seu hash SHA-256.

    Se a verificação falhar, o arquivo parcial é imediatamente excluído do disco
    para impedir uso acidental de pacotes corrompidos ou adulterados.

    Args:
        package_id: ID do pacote conforme definido no catálogo (ex: 'ksc-server-16.3-pt-BR').
        target_dir: Diretório de destino para salvar o arquivo.
        catalog: Catálogo opcional de pacotes. Se None, carrega o padrão.
        verify: Se True, valida o checksum SHA-256 após o download.

    Returns:
        Path para o arquivo final baixado e validado.

    Raises:
        PackageNotFoundError: Se package_id não existir no catálogo.
        ChecksumVerificationError: Se verify=True e o hash não coincidir.
    """
    if catalog is None:
        catalog = load_package_catalog()

    packages = catalog.get("packages", {})
    if package_id not in packages:
        raise PackageNotFoundError(
            f"Pacote '{package_id}' não encontrado no catálogo. Use 'kscctl packages --list' para listar opções."
        )

    pkg = packages[package_id]
    url = pkg["url"]
    filename = pkg["filename"]
    expected_sha256 = pkg["sha256"]

    out_dir = Path(target_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    final_path = out_dir / filename

    fd, tmp_file_path = tempfile.mkstemp(
        prefix=f"{filename}.", suffix=".download.part", dir=out_dir
    )
    part_path = Path(tmp_file_path)

    logger.info(f"Iniciando download de {pkg['product']} ({package_id})...")
    logger.info(f"URL: {url}")
    logger.info(f"Destino temporário: {part_path}")

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "KSC-Deployment-Runbook/1.0 (+https://github.com/portosoft/ksc-deployment-runbook)"
        },
    )

    try:
        with os.fdopen(fd, "wb") as out_file, urllib.request.urlopen(
            req, timeout=60
        ) as resp:
            shutil.copyfileobj(resp, out_file, length=CHUNK_SIZE)

        if verify:
            logger.info(f"Verificando integridade SHA-256 de {filename}...")
            actual_hash = compute_sha256(part_path)
            if not hmac.compare_digest(actual_hash, expected_sha256.lower()):
                if part_path.exists():
                    part_path.unlink()
                raise ChecksumVerificationError(
                    f"Falha de integridade no pacote '{package_id}' ({filename}):\n"
                    f"  Esperado: {expected_sha256}\n"
                    f"  Obtido:   {actual_hash}\n"
                    f"Arquivo temporário descartado por segurança."
                )

        # Mover atomicamente para o destino final
        part_path.replace(final_path)
        logger.info(f"Download concluído e validado com sucesso: {final_path}")
        return final_path

    except Exception:
        if part_path.exists():
            part_path.unlink(missing_ok=True)
        raise


def print_packages_table(catalog: Optional[Dict[str, Any]] = None) -> None:
    """Exibe na saída padrão a lista tabulada de pacotes oficiais."""
    if catalog is None:
        catalog = load_package_catalog()

    packages = catalog.get("packages", {})
    metadata = catalog.get("metadata", {})

    print("\n" + "=" * 105)
    print(" CATÁLOGO OFICIAL DE PACOTES KASPERSKY - KSC RUNBOOK")
    print(f" Fonte: {metadata.get('source_url')}")
    print(f" Atualizado em: {metadata.get('updated_at')}")
    print("=" * 105)
    print(
        f"{'ID do Pacote':<32} {'Versão':<14} {'Idioma':<8} {'Arquivo':<35} {'SHA-256 (Prefixo)':<16}"
    )
    print("-" * 105)

    for pkg_id, info in sorted(packages.items()):
        sha_prefix = info["sha256"][:12] + "..."
        print(
            f"{pkg_id:<32} {info['version']:<14} {info['language']:<8} {info['filename']:<35} {sha_prefix:<16}"
        )

    print("-" * 105)
    print("Para verificar pacotes locais: kscctl packages --verify-dir <diretorio>")
    print(
        "Para baixar e validar:        kscctl packages --download <id_do_pacote> [--output-dir <dir>]\n"
    )
