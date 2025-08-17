# opsbox
A small, real service (API + worker) and all the DevOps around it—containers, Kubernetes, CI/CD, observability, security—so you become production-fluent in Python and Bash.

## Tools
```bash
python3 --version 
Python 3.12.3

helm 3.17.4
```

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
- Format: `make fmt`
- Lint: `make lint`
- Test: `make test`
- Build images: `make build` (uses TAG from `git rev-parse --short HEAD`)
- Full local pipeline: `make pipeline-local`
- Run local stack: `make run` (calls `ops/scripts/bootstrap.sh`)