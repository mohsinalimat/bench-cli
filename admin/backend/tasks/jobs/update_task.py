from bench_cli.commands.update import UpdateCommand
from .base_task import BaseTask


class UpdateTask(BaseTask):
    def run(self) -> None:
        UpdateCommand(self.bench, skip_confirm=True).run()


if __name__ == "__main__":
    UpdateTask.main()
