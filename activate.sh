#!/bin/bash
# Script para ativar o ambiente virtual

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Ambiente virtual não encontrado. Criando..."
    python3 -m venv "$SCRIPT_DIR/.venv"
    
    echo "Instalando dependências..."
    "$SCRIPT_DIR/.venv/bin/pip" install --upgrade pip
    "$SCRIPT_DIR/.venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
fi

echo "Ativando ambiente virtual..."
source "$SCRIPT_DIR/.venv/bin/activate"

echo ""
echo "Ambiente virtual ativado!"
echo "Versão do Ansible: $(ansible --version | head -n 1)"
echo "Versão do Python: $(python --version)"
echo ""
echo "Para desativar, execute: deactivate"
