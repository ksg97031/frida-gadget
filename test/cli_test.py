from scripts.cli import run
from click.testing import CliRunner

from pathlib import Path
p = Path(__file__)
ROOT_DIR = p.parent.resolve()

def test_run():
    runner = CliRunner()
    demo_apk_path = str(ROOT_DIR.joinpath('demo-apk/handtrackinggpu.apk').resolve())
    result = runner.invoke(run, [demo_apk_path])
    assert result.exit_code == 0
