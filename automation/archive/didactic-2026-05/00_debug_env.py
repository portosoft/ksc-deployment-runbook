#!/usr/bin/env python3
"""
LIÇÃO DIDÁTICA 00: DEPURAÇÃO DE CARREGAMENTO DE AMBIENTE
-------------------------------------------------------
Este script ensina como validar se as variáveis do seu arquivo .env
estão sendo lidas corretamente pelo Python.

Por que isso é importante?
Muitas vezes, ao usar aspas para proteger strings no .env, o interpretador
pode acabar incluindo as aspas no valor final da variável. Isso quebra
senhas e logins sem deixar uma mensagem de erro óbvia. Validar o comprimento
(length) da variável é uma forma segura de depurar sem expor a senha na tela.

Conceitos-chave:
1. python-dotenv: Biblioteca que carrega o .env para as variáveis de sistema.
2. os.getenv: Função padrão do Python para ler variáveis de ambiente.
3. Diagnóstico Silencioso: Verificar o tamanho da string em vez do conteúdo.
"""

import os
from dotenv import load_dotenv

def main():
    # Tenta carregar o arquivo
    env_path = "configs/env/ksc_vars.env"
    if not os.path.exists(env_path):
        print(f"ERRO: Arquivo {env_path} não encontrado!")
        return

    load_dotenv(env_path)

    # Lista de variáveis para testar
    vars_to_test = ["KSC_HOST", "KSC_USER", "KSC_PASS", "KSC_DB_PASS"]

    print(f"--- Relatório de Diagnóstico de Ambiente ---")
    for var in vars_to_test:
        val = os.getenv(var)
        if val:
            # Mostramos apenas o tamanho e os primeiros/últimos caracteres se não for senha
            if "PASS" in var:
                print(f"{var}: Carregado (Tamanho: {len(val)})")
            else:
                print(f"{var}: {val} (Tamanho: {len(val)})")
        else:
            print(f"{var}: NÃO CARREGADO")

if __name__ == "__main__":
    main()
