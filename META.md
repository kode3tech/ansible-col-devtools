# Collection Meta Information

This file provides additional metadata about the `kode3tech.devtools` collection.

## Collection Details

- **Namespace**: kode3tech
- **Name**: devtools
- **Description**: Ansible Collection for DevOps tools installation and configuration
- **License**: MIT
- **Repository**: https://github.com/kode3tech/ansible-devtools

## Roles Included

### docker
Docker Engine installation and configuration with Docker Compose support.

**Supported Platforms:**
- Ubuntu 22.04, 24.04, 25.04
- Debian 11, 12, 13
- RHEL/CentOS/Rocky Linux 9, 10

**Main Features:**
- Automatic repository configuration
- Docker Compose installation
- User group management
- Service configuration

### podman
Podman installation with rootless container support.

**Supported Platforms:**
- Ubuntu 22.04, 24.04, 25.04
- Debian 11, 12, 13
- RHEL/CentOS/Rocky Linux 9, 10

**Main Features:**
- Daemonless container engine
- Rootless mode configuration
- Buildah and Skopeo included
- OCI-compliant runtime

## Dependencies

### Runtime Dependencies
- ansible-core >= 2.15
- Python >= 3.9

### Development Dependencies
See `requirements.txt` for complete list:
- molecule[docker]
- ansible-lint
- yamllint
- pytest
- testinfra

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/kode3tech/ansible-devtools/issues
- Documentation: https://github.com/kode3tech/ansible-devtools

## Maintainers

- Kode3Tech DevOps Team
