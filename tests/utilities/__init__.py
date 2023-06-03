from pathlib import Path


def runs_list(run_dir: Path) -> list[Path]:
    runs = [x for x in run_dir.iterdir() if x.is_dir()]
    return runs
