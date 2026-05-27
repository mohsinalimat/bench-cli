import sys
import tomllib

from bench_cli.utils import run_command, write_toml
from .base_task import BaseTask


class DropSiteTask(BaseTask):
    @classmethod
    def _parser(cls):
        p = super()._parser()
        p.add_argument("name")
        return p

    def __init__(self, bench, bench_root, args):
        super().__init__(bench, bench_root, args)
        self.name = args.name

    def run(self) -> None:
        bench_bin = str(self.bench.env_path / "bin" / "bench")
        cmd = [bench_bin, "frappe", "drop-site", "--force", self.name]
        if self.bench.config.mariadb.root_password:
            cmd += ["--db-root-password", self.bench.config.mariadb.root_password]
        print(f"Dropping site '{self.name}'...")
        sys.stdout.flush()
        run_command(cmd, cwd=self.bench.sites_path, stream_output=True)

        bench_toml = self.bench_root / "bench.toml"
        with bench_toml.open("rb") as fh:
            raw = tomllib.load(fh)
        raw["sites"] = [s for s in raw.get("sites", []) if s.get("name") != self.name]
        write_toml(bench_toml, raw)
        print(f"\nSite '{self.name}' dropped and removed from bench.toml.")


if __name__ == "__main__":
    DropSiteTask.main()
