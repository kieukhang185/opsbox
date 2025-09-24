# OpsBox - All Devops in a Box
[![CI](https://github.com/kieukhang185/opsbox/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/kieukhang185/opsbox/actions/workflows/ci.yaml)
[![Build-and-test](https://github.com/kieukhang185/opsbox/actions/workflows/build-and-test.yaml/badge.svg?branch=main)](https://github.com/kieukhang185/opsbox/actions/workflows/build-and-test.yaml)
[![Pre-commit](https://github.com/kieukhang185/opsbox/actions/workflows/pre-commit.yaml/badge.svg?branch=main)](https://github.com/kieukhang185/opsbox/actions/workflows/pre-commit.yaml)

A small, real service (API + worker) and all the DevOps around it—containers, Kubernetes, CI/CD, observability, security—so you become production-fluent in Python and Bash.

## Tools
|      Tools    |    Version    |      Tools    |    Version    |
| ------------- | ------------- | ------------- | ------------- |
|    Python     |     3.12.3    |      Kind     |    v0.30.0    |
|     Helm      |     3.17.4    |     Kubectl   |    v1.33.4    |

### Setup python venv
```bash
sudo apt-get install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
```

### Pre-commit hooks
Install and enable once:

```bash
sudo apt install pre-commit
export PATH=$PATH:/home/ubuntu/.local/bin
pre-commit install
pre-commit run --all-files
```

### Opsbox-cli

```bash
opsbox --tag dev # Build API & Worker docker images
```

### CI/CD Flow

- `build-and-test:` Build and Push API & Worker images to github registry (on push & pull-request main branch)
- `ci:` Basic ci flow to check API & Worker (on push dev branch)
- `pre-commit:` Synctax flow to check for Python, Bash, Yaml and so on (on push & pull-request main branch)


### Developer workflow

```bash
make help   # List all targets avaliable on Makefile
make build  # Build api/worker images
make deploy # Deploy all applivations (api, worker, postgres, rabbitmq,...)
make smoke  # Test api app `/health`
make down   # Uninstall Helm releases, delete namespace, kill port-forward
make clean  # Cleanup docker/docker images
make reset  # make down + make clean: Reset k8s
make nuke   # Destroy kind and cleanup
make prune  # Clean docker
```
