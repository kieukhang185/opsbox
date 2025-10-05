#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

import typer

app = typer.Typer(help="Opsbox CLI: build, push")

ROOT = Path(__file__).resolve().parents[3]


def is_logged_in() -> bool:
    proc = subprocess.run(["docker", "info"], capture_output=True, text=True)
    return "Username:" in proc.stdout


def run_cmd(cmd: list[str], cwd: Path = ROOT, dry_run: bool = False):
    if dry_run:
        typer.echo(f"$ {' '.join(cmd)}")
        return
    typer.echo(f"$ {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=cwd)
    if proc.returncode != 0:
        sys.exit(proc.returncode)


@app.command()
def build(tag: str = "dev", dry_run: bool = False):
    """Build API & Worker docker images"""
    run_cmd(
        ["docker", "build", "-f", "api/Dockerfile", "-t", f"opsbox-api:{tag}", ".", "--rm"],
        dry_run=dry_run,
    )
    run_cmd(
        ["docker", "build", "-f", "worker/Dockerfile", "-t", f"opsbox-worker:{tag}", ".", "--rm"],
        dry_run=dry_run,
    )


@app.command()
def push(tag: str = "dev", registry: str = "hunterbxb", dry_run: bool = False):
    """Push api/worker docker images to registry"""
    if not dry_run and not is_logged_in():
        typer.echo("Not logged in to Docker registry. Please run 'docker login' first.")
        sys.exit(1)

    run_cmd(["docker", "tag", f"opsbox-api:{tag}", f"{registry}/opsbox-api:{tag}"], dry_run=dry_run)
    run_cmd(
        ["docker", "tag", f"opsbox-worker:{tag}", f"{registry}/opsbox-worker:{tag}"],
        dry_run=dry_run,
    )
    run_cmd(["docker", "push", f"{registry}/opsbox-api:{tag}"], dry_run=dry_run)
    run_cmd(["docker", "push", f"{registry}/opsbox-worker:{tag}"], dry_run=dry_run)
