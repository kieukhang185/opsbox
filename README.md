# opsbox
A small, real service (API + worker) and all the DevOps around it—containers, Kubernetes, CI/CD, observability, security—so you become production-fluent in Python and Bash.

## Tools
```bash
python3 --version 
Python 3.12.3
```

## Setup python venv
```bash
sudo apt-get install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
```

### Pre-commit hooks
Install and enable once:

```bash
pip3 install pre-commit
pre-commit install
pre-commit run --all-files

