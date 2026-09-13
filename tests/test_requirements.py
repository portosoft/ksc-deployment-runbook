# -*- coding: utf-8 -*-
"""Guarda contra dependências mortas em requirements.txt (#101).

O arquivo já fixou `python-dotenv` sem que nada o importasse — o projeto tem
seu próprio carregador de `.env` — e fixou `jinja2`, `lxml` e `Pillow`, que são
transitivas do `md2pdf`. Este teste impede que isso volte sem justificativa.
"""

import re
from pathlib import Path

REQUIREMENTS = Path(__file__).resolve().parent.parent / "requirements.txt"
CODE_DIRS = ["automation", "tests", "scripts"]

# Nome na distribuição -> nome usado no import.
IMPORT_NAMES = {
    "pyyaml": "yaml",
    "pillow": "PIL",
    "python-dotenv": "dotenv",
    "md2pdf": "md2pdf",
}

# Ferramentas que não são importadas pelo código de produção, com a razão de
# continuarem fixadas. Qualquer outra dependência precisa ser importada.
TOOLS_NOT_IMPORTED = {
    "pytest": "executor da suíte",
    "pytest-cov": "cobertura publicada no CI — issue #102",
}


def _pinned_packages():
    pacotes = []
    for linha in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        pacotes.append(re.split(r"[=<>!~\[]", linha)[0].strip().lower())
    return pacotes


def _source_files():
    raiz = REQUIREMENTS.parent
    arquivos = []
    for diretorio in CODE_DIRS:
        arquivos.extend((raiz / diretorio).rglob("*.py"))
    return arquivos


def _imported_modules():
    modulos = set()
    padrao = re.compile(r"^\s*(?:from|import)\s+([A-Za-z_][\w.]*)", re.MULTILINE)
    dinamico = re.compile(r"import_module\(\s*[\"']([A-Za-z_][\w.]*)")
    for arquivo in _source_files():
        try:
            conteudo = arquivo.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in padrao.findall(conteudo) + dinamico.findall(conteudo):
            modulos.add(match.split(".")[0].lower())
    return modulos


def test_every_pinned_requirement_is_used():
    """Cada dependência fixada é importada pelo código ou consta como ferramenta."""
    modulos = _imported_modules()
    nao_utilizadas = []

    for pacote in _pinned_packages():
        if pacote in TOOLS_NOT_IMPORTED:
            continue
        alvo = IMPORT_NAMES.get(pacote, pacote.replace("-", "_"))
        if alvo.lower() not in modulos:
            nao_utilizadas.append(pacote)

    assert not nao_utilizadas, (
        f"Dependências fixadas sem uso no código: {nao_utilizadas}. "
        "Remova-as, ou registre a justificativa em TOOLS_NOT_IMPORTED."
    )


def test_removed_dependencies_stay_removed():
    """Quatro dependências foram removidas em #101; nenhuma deve voltar em silêncio."""
    pacotes = _pinned_packages()

    # python-dotenv: automation/python/config.py implementa o próprio leitor.
    assert "python-dotenv" not in pacotes
    # jinja2, lxml e Pillow chegam pelo md2pdf/weasyprint.
    for transitiva in ("jinja2", "lxml", "pillow"):
        assert transitiva not in pacotes, (
            f"'{transitiva}' é transitiva do md2pdf. Fixá-la seletivamente dá a "
            "impressão de um lockfile completo, que requirements.txt não é."
        )


def test_requirements_declares_python_floor():
    """O piso de versão do Python precisa estar visível: no Rocky 9 o padrão é 3.9."""
    conteudo = REQUIREMENTS.read_text(encoding="utf-8")
    assert "3.10" in conteudo
