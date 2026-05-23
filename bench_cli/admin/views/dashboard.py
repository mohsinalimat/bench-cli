from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, current_app, render_template

from bench_cli.admin.readers.app_reader import AppReader
from bench_cli.admin.readers.bench_reader import BenchReader
from bench_cli.admin.readers.process_reader import ProcessReader
from bench_cli.admin.readers.site_reader import SiteReader
from bench_cli.tasks.task_reader import TaskReader

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    bench_root = current_app.config["BENCH_ROOT"]
    try:
        summary = BenchReader(bench_root).summary()
        apps = AppReader(bench_root).read_all()
        sites = SiteReader(bench_root).read_all()
        processes = ProcessReader(bench_root).read_all()
        recent_tasks = TaskReader(bench_root).list_tasks(limit=5)
    except Exception as error:
        return render_template("error.html", error=str(error))

    now = datetime.now(timezone.utc)
    running_count = sum(1 for p in processes if p.status == "running")
    cloned_count = sum(1 for a in apps if a.is_cloned)
    online_count = sum(1 for s in sites if s.exists)

    return render_template(
        "dashboard.html",
        summary=summary,
        apps=apps,
        sites=sites,
        processes=processes,
        recent_tasks=recent_tasks,
        now=now,
        running_count=running_count,
        cloned_count=cloned_count,
        online_count=online_count,
    )
