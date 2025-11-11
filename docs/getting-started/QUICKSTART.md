# Guia de Início Rápido

## 🚀 Setup Inicial

### 1. Pré-requisitos

Certifique-se de ter instalado:
- asdf (gerenciador de versões)
- Plugin Python3 do asdf
- Git

### 2. Clonar o Repositório

```bash
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools
```

### 3. Configurar Python

O projeto já está configurado com Python3 3.11.2 via asdf:

```bash
# Instalar a versão Python3 do .tool-versions
asdf install

# Verificar
python3 --version  # Deve mostrar: Python3 3.11.2
```

### 4. Instalar Dependências

**Opção A: Usando o script (Recomendado)**

```bash
source activate.sh
```

**Opção B: Usando make**

```bash
make install
source .venv/bin/activate
```

**Opção C: Manual**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Verificar Instalação

```bash
# Usando make
make version

# Ou manualmente
ansible --version
ansible-lint --version
molecule --version
```

## 🛠️ Comandos Úteis

### Ativação do Ambiente

```bash
# Sempre que abrir um novo terminal
source .venv/bin/activate

# Ou use o script
source activate.sh
```

### Linting

```bash
# Executar todos os linters
make lint

# Apenas YAML
make lint-yaml

# Apenas Ansible
make lint-ansible
```

### Testes

```bash
# Testes com Molecule
make test

# Testes com pytest
make test-pytest
```

### Limpeza

```bash
# Limpar arquivos temporários
make clean

# Limpar tudo (incluindo venv)
make clean-all
```

## 📚 Estrutura de Arquivos

```text
.
├── .tool-versions       # Versão Python3 (asdf)
├── .python-version      # Versão Python3 alternativa
├── requirements.txt     # Dependências
├── ansible.cfg          # Configuração Ansible
├── .ansible-lint        # Configuração ansible-lint
├── .yamllint            # Configuração yamllint
├── Makefile             # Comandos úteis
├── activate.sh          # Script de ativação
├── inventory.example    # Exemplo de inventário
└── docs/                # Documentação
```

## 🔧 Próximos Passos

1. **Configurar Inventário**: Copie e edite `inventory.example`
   ```bash
   cp inventory.example inventory
   # Edite com seus hosts
   ```

2. **Criar uma Role**: Use o molecule para inicializar
   ```bash
   molecule init role nome-da-role
   ```

3. **Desenvolver**: Crie suas tasks, handlers, templates, etc.

4. **Testar**: Execute os testes
   ```bash
   make lint
   make test
   ```

## 🆘 Troubleshooting

### Ambiente virtual não ativa

```bash
# Remover e recriar
rm -rf .venv
make install
```

### Versão Python3 incorreta

```bash
# Verificar asdf
asdf current python

# Reinstalar
asdf install python3 3.11.2
asdf set python3 3.11.2
```

### Dependências não instalam

```bash
# Atualizar pip primeiro
pip install --upgrade pip

# Depois instalar requirements
pip install -r requirements.txt
```

## 📞 Suporte

Para dúvidas ou problemas, contate o time da Kode3Tech.

---

**Happy Coding! 🚀**
