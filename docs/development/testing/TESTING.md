# Testing Strategy for Docker Role

## Overview

A role Docker possui uma estrutura completa de testes usando **Molecule** com **Docker** como driver e **Testinfra** para testes de verificação.

## Test Structure

```text
docker/
├── molecule/
│   └── default/              # Cenário de teste padrão
│       ├── molecule.yml      # Configuração do Molecule
│       ├── converge.yml      # Playbook de aplicação da role
│       ├── verify.yml        # Verificações com Ansible
│       ├── prepare.yml       # Preparação do ambiente
│       ├── create.yml        # Criação dos containers
│       ├── destroy.yml       # Destruição dos containers
│       └── test_default.py   # Testes com pytest/testinfra
└── pytest.ini                # Configuração do pytest
```

## Test Platforms

Os testes são executados em múltiplas plataformas usando containers Docker:

1. **Ubuntu 22.04 (Jammy)** - `geerlingguy/docker-ubuntu2204-ansible`
2. **Debian 12 (Bookworm)** - `geerlingguy/docker-debian12-ansible`
3. **Rocky Linux 9** - `geerlingguy/docker-rockylinux9-ansible`

## Test Sequence

O Molecule executa a seguinte sequência de testes:

1. **dependency** - Instala dependências (roles/collections)
2. **cleanup** - Limpa ambiente anterior
3. **destroy** - Remove containers antigos
4. **syntax** - Valida sintaxe dos playbooks
5. **create** - Cria containers de teste
6. **prepare** - Prepara ambiente (instala pré-requisitos)
7. **converge** - Aplica a role nos containers
8. **idempotence** - Verifica idempotência (segunda execução)
9. **verify** - Executa verificações (Ansible + Testinfra)
10. **cleanup** - Limpa ambiente
11. **destroy** - Remove containers

## Running Tests

### Full Test Suite

```bash
# Executar todos os testes em todas as plataformas
cd docker/
molecule test
```

### Individual Steps

```bash
# Criar containers
molecule create

# Aplicar role
molecule converge

# Verificar resultado
molecule verify

# Executar testes testinfra
molecule verify --scenario-name default

# Limpar ambiente
molecule destroy
```

### Testing Specific Platforms

```bash
# Testar apenas Ubuntu
molecule test --platform-name ubuntu2204

# Testar apenas Debian
molecule test --platform-name debian12

# Testar apenas Rocky Linux
molecule test --platform-name rockylinux9
```

### Development Mode

Durante o desenvolvimento, você pode manter os containers ativos:

```bash
# Criar e manter containers
molecule create

# Aplicar mudanças
molecule converge

# Verificar (pode executar várias vezes)
molecule verify

# Quando terminar, destruir
molecule destroy
```

## Test Cases

### Ansible-based Verification (verify.yml)

1. ✅ Docker está instalado
2. ✅ Serviço Docker está rodando
3. ✅ Docker daemon responde
4. ✅ Grupo docker existe
5. ✅ Usuário está no grupo docker
6. ✅ Docker funciona (hello-world)

### Testinfra Tests (test_default.py)

1. ✅ Pacote docker-ce instalado
2. ✅ Serviço docker rodando e habilitado
3. ✅ Grupo docker existe
4. ✅ Comando docker disponível
5. ✅ Docker Compose plugin instalado
6. ✅ Docker info funciona
7. ✅ Arquivo daemon.json configurado
8. ✅ Container hello-world executa
9. ✅ Usuário no grupo docker

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Molecule Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        platform:
          - ubuntu2204
          - debian12
          - rockylinux9

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run Molecule tests
        run: |
          cd docker/
          molecule test --platform-name ${{ matrix.platform }}
```

## Requirements

Certifique-se de ter as seguintes ferramentas instaladas:

- Python 3.11+
- Docker Desktop (para rodar containers)
- Molecule
- molecule-plugins[docker]
- pytest
- pytest-testinfra

Todas já estão no `requirements.txt` do projeto.

## Troubleshooting

### Container fails to start

```bash
# Verificar logs
molecule --debug create

# Verificar se Docker está rodando
docker ps
```

### Tests fail on specific platform

```bash
# Testar apenas aquela plataforma com debug
molecule --debug test --platform-name ubuntu2204
```

### Idempotence test fails

Verifique se suas tasks são idempotentes (não fazem mudanças na segunda execução):

```bash
# Aplicar duas vezes e comparar
molecule converge
molecule converge
```

## Best Practices

1. **Sempre teste em múltiplas plataformas** antes de fazer commit
2. **Garanta idempotência** - role deve poder ser executada múltiplas vezes
3. **Teste cases de erro** - não apenas o caminho feliz
4. **Use check_mode** quando possível para testes não destrutivos
5. **Documente casos de teste** específicos no código

## Next Steps

1. Adicionar mais plataformas (CentOS Stream, Fedora)
2. Adicionar testes de upgrade do Docker
3. Adicionar testes de configurações avançadas
4. Integrar com CI/CD (GitHub Actions, GitLab CI)
5. Adicionar testes de performance
6. Adicionar testes de segurança

## Resources

- [Molecule Documentation](https://molecule.readthedocs.io/)
- [Testinfra Documentation](https://testinfra.readthedocs.io/)
- [Jeff Geerling Docker Images](https://hub.docker.com/u/geerlingguy)
