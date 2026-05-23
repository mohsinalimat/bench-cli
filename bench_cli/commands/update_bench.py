from __future__ import annotations

from pathlib import Path

import click

from bench_cli.exceptions import BenchError
from bench_cli.utils import run_command, uv_bin


class UpdateBenchCliCommand:
    def run(self) -> None:
        source = self._find_source()
        click.echo(f"Updating bench-cli from {source}...")
        self._git_pull(source)
        click.echo("Reinstalling bench-cli...")
        self._reinstall(source)
        click.echo("\nbench-cli updated successfully.")

    def _find_source(self) -> Path:
        # Standard location created by install.sh
        standard = Path.home() / "bench-cli"
        if (standard / ".git").exists():
            return standard

        # Editable / development install: walk up from the package directory
        import bench_cli as _pkg
        pkg_root = Path(_pkg.__file__).parent.parent
        if (pkg_root / ".git").exists():
            return pkg_root

        raise BenchError(
            "Cannot find the bench-cli source repository.\n"
            "bench-cli must be installed from a local git clone. "
            "Re-run the installer:\n"
            "  curl -fsSL https://raw.githubusercontent.com/frappe/bench-cli/main/install.sh | bash"
        )

    def _git_pull(self, source: Path) -> None:
        run_command(["git", "-C", str(source), "pull"], stream_output=True)

    def _reinstall(self, source: Path) -> None:
        run_command(
            [uv_bin(), "tool", "install", "--reinstall", str(source)],
            stream_output=True,
        )
