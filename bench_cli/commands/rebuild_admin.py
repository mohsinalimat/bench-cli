from __future__ import annotations

import shutil
from pathlib import Path

import click

from bench_cli.exceptions import BenchError
from bench_cli.utils import run_command


class RebuildAdminCommand:
    def run(self) -> None:
        frontend = self._find_frontend()
        click.echo(f"Building admin frontend at {frontend}...")
        if not (frontend / "node_modules").exists():
            click.echo("Running npm install...")
            run_command(["npm", "install"], cwd=frontend, stream_output=True)
        run_command(["npm", "run", "build"], cwd=frontend, stream_output=True)
        click.echo("\nAdmin frontend rebuilt successfully.")

    def _find_frontend(self) -> Path:
        for source in self._source_candidates():
            candidate = source / "admin" / "frontend"
            if (candidate / "package.json").exists():
                return candidate
        raise BenchError(
            "admin/frontend not found.\n"
            "This command requires the bench-cli source directory with admin/frontend/."
        )

    def _source_candidates(self):
        # Standard location created by install.sh
        yield Path.home() / "bench-cli"
        # Editable / development install: __file__ points into the source tree
        import bench_cli as _pkg
        yield Path(_pkg.__file__).parent.parent
