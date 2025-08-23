# opsbox
A small, real service (API + worker) and all the DevOps around it—containers, Kubernetes, CI/CD, observability, security—so you become production-fluent in Python and Bash.

## Tools
|      Tools    |    Version    |      Tools    |    Version    |
| ------------- | ------------- | ------------- | ------------- |
|    Python     |     3.12.3    |      Kind     |    v0.23.0    |
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
pip3 install pre-commit --break-system-packages
export PATH=$PATH:/home/ubuntu/.local/bin
pre-commit install
pre-commit run --all-files
```

### Developer workflow
- List targets: `make help`
- Build images: `make build`
- Deploy: `make deploy`
- Test: `make smoke`
- Uninstall Helm releases, delete namespace, kill port-forward: `make down`
- Cleanup: `make clean`
- Reset: `make down + make clean`
- Nuke: `make nuke`
- Clean docker: `make prune`
