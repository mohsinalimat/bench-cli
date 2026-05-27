import sys

from bench_cli.config.site_config import SiteConfig
from bench_cli.core.site import Site
from .base_task import BaseTask


class NewSiteTask(BaseTask):
    @classmethod
    def _parser(cls):
        p = super()._parser()
        p.add_argument("name")
        p.add_argument("--admin-password", default="admin")
        return p

    def __init__(self, bench, bench_root, args):
        super().__init__(bench, bench_root, args)
        self.name = args.name
        self.admin_password = args.admin_password

    def run(self) -> None:
        site = Site(SiteConfig(name=self.name, apps=[], admin_password=self.admin_password), self.bench)
        if site.exists:
            print(f"Site '{self.name}' already exists. Skipping creation.")
            return
        print(f"Creating site '{self.name}'...")
        sys.stdout.flush()
        site.create()
        self.bench.write_common_site_config()
        print(f"\nSite '{self.name}' created successfully.")


if __name__ == "__main__":
    NewSiteTask.main()
