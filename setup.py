import subprocess
import sys
import os

def run_command(command):
    """Executa um comando no terminal e verifica se houve erros."""
    try:
        print(f"--- Executando comando: {' '.join(command)} ---")
        # shell=True é necessário no Windows para que comandos como pip funcionem
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"\n!!! ERRO ao executar o comando: {' '.join(command)} !!!")
        print(f"Código de saída: {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\n!!! ERRO: Comando '{command[0]}' não encontrado.")
        print("Certifique-se de que o Python está instalado e configurado no PATH do sistema.")
        sys.exit(1)

def main():
    """
    Script para instalar dependências globalmente e iniciar o servidor.
    """
    print("--- Iniciando configuração do ambiente UCONNECT (Instalação Global) ---")
    print("AVISO: As dependências serão instaladas no ambiente Python principal do sistema.")

    # 1. Instalar dependências do requirements.txt
    requirements_file = 'requirements.txt'
    if os.path.exists(requirements_file):
        # O argumento '--user' instala os pacotes para o usuário atual,
        # evitando problemas de permissão e conflitos com pacotes do sistema.
        install_command = [sys.executable, '-m', 'pip', 'install', '--user', '-r', requirements_file]
        run_command(install_command)
        print("\n--- Dependências instaladas com sucesso! ---")
    else:
        print(f"\n!!! ERRO: Arquivo '{requirements_file}' não encontrado.")
        print("Certifique-se de que este script está na pasta raiz do projeto.")
        sys.exit(1)

    # 2. Iniciar o servidor Uvicorn
    print("\n--- Iniciando o servidor FastAPI com Uvicorn ---")
    print("O servidor será executado em http://127.0.0.1:8000")
    print("Pressione CTRL+C para parar o servidor.")
    
    # Executar uvicorn como um módulo (python -m uvicorn) é mais confiável
    # do que depender do comando estar no PATH do sistema.
    server_command = [sys.executable, '-m', 'uvicorn', 'backend.app.main:app', '--reload']
    run_command(server_command)

if __name__ == "__main__":
    main()

