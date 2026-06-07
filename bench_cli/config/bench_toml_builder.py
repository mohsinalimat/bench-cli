from __future__ import annotations

_BASE_TEMPLATE = """\
[bench]
name = "{name}"
python = "{python}"
http_port = {http_port}
socketio_port = {socketio_port}

[[apps]]
name = "frappe"
repo = "{app_repo}"
branch = "{app_branch}"

[mariadb]
host = "localhost"
port = 3306
root_password = "{mariadb_password}"

[redis]
port = {redis_port}

[workers]
default = {workers_default}
short = {workers_short}
long = {workers_long}

[admin]
port = {admin_port}
enabled = {admin_enabled}
timeout = 180
password = "{admin_password}"
"""

_VOLUME_TEMPLATE = """
[volume]
enabled = true
pool = "{volume_pool}"
device = "{volume_device}"

[volume.benches]
reservation = "{volume_benches_reservation}"
quota = "{volume_benches_quota}"

[volume.mariadb]
reservation = "{volume_mariadb_reservation}"
quota = "{volume_mariadb_quota}"
data_dir = "{volume_mariadb_data_dir}"

[volume.snapshots]
enabled = {volume_snapshots_enabled}
"""


def _toml_bool(value: object) -> str:
    return "true" if value else "false"


class BenchTomlBuilder:
    """Single source of truth for rendering a bench.toml document.

    Used by both `bench new` (starter config) and the setup wizard
    (config from user-supplied values), so the layout never diverges.
    """

    def __init__(self, name: str, settings: dict | None = None) -> None:
        self._name = name
        self._settings = settings or {}

    def render(self) -> str:
        content = self._render_base()
        if self._settings.get("volume_enabled"):
            content += self._render_volume()
        return content

    def _render_base(self) -> str:
        get = self._settings.get
        return _BASE_TEMPLATE.format(
            name=self._name,
            python=get("python", "3.14"),
            http_port=int(get("http_port", 8000)),
            socketio_port=int(get("socketio_port", 9000)),
            app_repo=get("app_repo", "https://github.com/frappe/frappe"),
            app_branch=get("app_branch", "version-16"),
            mariadb_password=get("mariadb_password", "root"),
            redis_port=int(get("redis_port", 13000)),
            workers_default=int(get("workers_default", 2)),
            workers_short=int(get("workers_short", 1)),
            workers_long=int(get("workers_long", 1)),
            admin_port=int(get("admin_port", 8002)),
            admin_enabled=_toml_bool(get("admin_enabled", False)),
            admin_password=get("admin_password", ""),
        )

    def _render_volume(self) -> str:
        get = self._settings.get
        return _VOLUME_TEMPLATE.format(
            volume_pool=get("volume_pool", ""),
            volume_device=get("volume_device", ""),
            volume_benches_reservation=get("volume_benches_reservation", "10G"),
            volume_benches_quota=get("volume_benches_quota", "50G"),
            volume_mariadb_reservation=get("volume_mariadb_reservation", "5G"),
            volume_mariadb_quota=get("volume_mariadb_quota", "20G"),
            volume_mariadb_data_dir=get("volume_mariadb_data_dir", "/var/lib/mysql"),
            volume_snapshots_enabled=_toml_bool(get("volume_snapshots_enabled", False)),
        )
