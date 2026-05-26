"""
Installs an app into a site then rebuilds its assets.
Invoked as: python -m admin.backend.tasks.jobs.install_app_task <bench_root> <site> <app>
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


class InstallAppJob:
    def __init__(self, bench_root: Path, site: str, app: str) -> None:
        self.bench_root = bench_root
        self.site = site
        self.app = app
        self.bench_bin = str(bench_root / "env" / "bin" / "bench")
        self.sites_dir = bench_root / "sites"

    def run(self) -> None:
        self._install_into_site()
        self._build_assets()

    def _install_into_site(self) -> None:
        print(f"Installing {self.app} into {self.site}...")
        sys.stdout.flush()
        result = subprocess.run(
            [self.bench_bin, "frappe", "--site", self.site, "install-app", self.app],
            cwd=str(self.sites_dir),
        )
        if result.returncode != 0:
            sys.exit(result.returncode)

    def _build_assets(self) -> None:
        app_dir = self.bench_root / "apps" / self.app
        if (app_dir / "package.json").exists():
            print(f"\nInstalling JS dependencies for {self.app}...")
            sys.stdout.flush()
            subprocess.run(["yarn", "install"], cwd=str(app_dir), check=False)

        print(f"\nBuilding assets...")
        sys.stdout.flush()
        subprocess.run(
            [self.bench_bin, "frappe", "build", "--force"],
            cwd=str(self.sites_dir),
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bench_root")
    parser.add_argument("site")
    parser.add_argument("app")
    args = parser.parse_args()
    InstallAppJob(Path(args.bench_root), args.site, args.app).run()


if __name__ == "__main__":
    main()
