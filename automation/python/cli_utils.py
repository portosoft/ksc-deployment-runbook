import argparse


def create_base_parser(description: str) -> argparse.ArgumentParser:
    """
    Cria o parser base com as flags de auditoria/setup padronizadas.
    """
    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--check",
        action="store_true",
        help="Executa pré-check (pré-requisitos antes da instalação).",
    )
    # Alguns scripts usam apply ou postcheck. Vamos deixar que o script instancie
    # o parser e adicione argumentos extras se quiser, ou usar um comum aqui.
    return parser
