"""test_cli.py"""
from pathlib import Path
from scripts.cli import run
from click.testing import CliRunner

p = Path(__file__)
ROOT_DIR = p.parent.resolve()

def test_run():
    """test frida-gadget run
    """
    runner = CliRunner()
    demo_apk_path = str(ROOT_DIR.joinpath('demo-apk/handtrackinggpu.apk').resolve())
    result = runner.invoke(run, [demo_apk_path])
    assert result.exit_code == 0
