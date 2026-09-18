#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import subprocess
import sys
from pathlib import Path


def _use_project_venv():
    """Re-run this command with the project's Python when Django is missing."""
    venv_python = Path(__file__).resolve().parent / "venv" / "Scripts" / "python.exe"
    if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
        command = [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]]
        raise SystemExit(subprocess.call(command))


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laptop_store.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        _use_project_venv()
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
