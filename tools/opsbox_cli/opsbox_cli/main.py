#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

import typer

app = typer.Typer(help="Opsbox CLI: build")

ROOT = Path(__file__).resolve().parents[3]


def run_cmd(cmd: list[str], cwd: Path = ROOT):
    typer.echo(f"$ {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=cwd)
    if proc.returncode != 0:
        sys.exit(proc.returncode)


@app.command()
def build(tag: str = "dev"):
    """Build API & Worker docker images"""
    run_cmd(["docker", "build", "-f", "api/Dockerfile", "-t", f"opsbox-api:{tag}", ".", "--rm"])
    run_cmd(
        ["docker", "build", "-f", "worker/Dockerfile", "-t", f"opsbox-worker:{tag}", ".", "--rm"]
    )


# @app.command()
# def push(tag: str = "dev", registry: str = "hunterbxb"):
#     """Push api/worker docker images to registry"""
#     run_cmd(["docker", "tag", f"opsbox-api:{tag}", f"{registry}/opsbox-api:{tag}"])
#     run_cmd(["docker", "tag", f"opsbox-worker:{tag}", f"{registry}/opsbox-worker:{tag}"])
#     run_cmd(["docker", "push", f"{registry}/opsbox-api:{tag}"])
#     run_cmd(["docker", "push", f"{registry}/opsbox-worker:{tag}"])
