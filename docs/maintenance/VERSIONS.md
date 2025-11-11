# Versões Instaladas

## Ambiente
- **Python**: 3.11.2 (gerenciado via asdf)
- **Shell**: zsh
- **OS**: macOS

## Ferramentas Ansible

| Ferramenta | Versão |
|-----------|--------|
| Ansible | 12.1.0 |
| Ansible Core | 2.19.3 |
| Ansible Lint | 25.9.2 |
| Molecule | 25.9.0 |
| Molecule Plugins | 25.8.12 |
| Ansible Navigator | 25.9.0 |
| Ansible Runner | 2.4.2 |
| Ansible Builder | 3.1.1 |

## Dependências Python

| Biblioteca | Versão |
|-----------|--------|
| Jinja2 | 3.1.6 |
| PyYAML | 6.0.3 |
| Cryptography | 46.0.3 |
| pytest | 8.4.2 |
| pytest-testinfra | 10.2.2 |
| yamllint | 1.37.1 |
| black | 25.9.0 |
| docker (Python SDK) | 7.1.0 |

## Comandos de Verificação

```bash
# Versão do Ansible
ansible --version

# Versão do Ansible Lint
ansible-lint --version

# Versão do Molecule
molecule --version

# Listar todas as dependências
pip list
```

## Atualização

Para atualizar todas as dependências:

```bash
pip install --upgrade -r requirements.txt
```

---
*Última atualização: 4 de novembro de 2025*
