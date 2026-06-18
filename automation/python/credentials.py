"""
Credential_Generator — geração de credenciais sintéticas criptograficamente seguras.

Usa exclusivamente stdlib Python: secrets, string, uuid.
Nenhuma dependência externa é introduzida.
"""

import secrets
import string
import uuid


def generate_password(length: int = 24, *, include_symbols: bool = True) -> str:
    """Retorna string de exatamente `length` chars, criptograficamente segura.

    Args:
        length: Comprimento da senha. Deve estar entre 8 e 256 (inclusive).
        include_symbols: Se True, inclui `string.punctuation` no alphabet.
                         Se False, usa apenas letras e dígitos.

    Returns:
        String aleatória de exatamente `length` caracteres.

    Raises:
        ValueError: Se `length` < 8 ou `length` > 256.
    """
    if length < 8 or length > 256:
        raise ValueError(f"length deve estar entre 8 e 256, recebido: {length}")

    alphabet = string.ascii_letters + string.digits
    if include_symbols:
        alphabet += string.punctuation

    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_hostile_password(length: int = 24) -> str:
    """Retorna senha que garante por construção a presença dos 5 conjuntos obrigatórios.

    Os cinco conjuntos obrigatórios são:
        - aspas simples: '
        - espaço: (space)
        - ponto-e-vírgula: ;
        - ampersand: &
        - sequência literal: $(

    A sequência `$(` ocupa 2 caracteres, portanto o comprimento mínimo efetivo
    para acomodar todos os conjuntos é 6. O length padrão de 24 é seguro.

    Args:
        length: Comprimento da senha. Deve ser >= 6 para acomodar todos os conjuntos.

    Returns:
        String de exatamente `length` caracteres com todos os 5 conjuntos presentes.
    """
    # Caracteres obrigatórios (a sequência "$(" conta como 2 chars)
    required = ["'", " ", ";", "&", "$("]

    # Alphabet base: letras, dígitos e pontuação, excluindo os chars já garantidos
    # para evitar duplicação acidental durante o preenchimento aleatório
    alphabet = string.ascii_letters + string.digits + string.punctuation + " "

    # Monta lista base com os 5 conjuntos obrigatórios
    base: list[str] = list(required)  # 6 chars no total ("$(" = 2)

    # Calcula quantos chars adicionais são necessários
    # "required" como lista tem 5 strings, mas "$(" tem 2 chars → total fixo = 6
    fixed_char_count = sum(len(r) for r in required)  # 1+1+1+1+2 = 6
    remaining = length - fixed_char_count

    # Preenche o restante aleatoriamente
    for _ in range(max(0, remaining)):
        base.append(secrets.choice(alphabet))

    # Embaralha com SystemRandom (criptograficamente seguro)
    secrets.SystemRandom().shuffle(base)

    return "".join(base)


def generate_synthetic_fqdn() -> str:
    """Retorna FQDN no formato ksc-{hex8}.test.

    O componente `{hex8}` são os primeiros 8 caracteres hexadecimais minúsculos
    de um UUID4, garantindo unicidade probabilística.

    Returns:
        String no formato `ksc-XXXXXXXX.test` onde X é [0-9a-f].
    """
    hex8 = uuid.uuid4().hex[:8]
    return f"ksc-{hex8}.test"


def generate_username(prefix: str = "testuser") -> str:
    """Retorna string no formato {prefix}_{hex6}.

    Args:
        prefix: Prefixo do nome de usuário. Padrão: "testuser".

    Returns:
        String no formato `{prefix}_XXXXXX` onde X é [0-9a-f].
    """
    hex6 = uuid.uuid4().hex[:6]
    return f"{prefix}_{hex6}"


def generate_test_db_name(prefix: str = "ksctest") -> str:
    """Retorna string no formato {prefix}_{hex6}.

    Args:
        prefix: Prefixo do nome do banco de dados. Padrão: "ksctest".

    Returns:
        String no formato `{prefix}_XXXXXX` onde X é [0-9a-f].
    """
    hex6 = uuid.uuid4().hex[:6]
    return f"{prefix}_{hex6}"
