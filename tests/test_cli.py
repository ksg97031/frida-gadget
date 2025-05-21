"""test_cli.py"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from scripts.cli import run
from click.testing import CliRunner

from scripts.cli import wrap_js_with_timeout

p = Path(__file__)
ROOT_DIR = p.parent.resolve()
DEMO_APK_PATH = str(ROOT_DIR.joinpath('demo-apk/handtrackinggpu.apk').resolve())

def test_run():
    """test frida-gadget run
    """
    runner = CliRunner()
    result = runner.invoke(run, [DEMO_APK_PATH])
    assert result.exit_code == 0

@patch('scripts.cli.detect_adb_arch')
@patch('scripts.cli.run_apktool')
@patch('scripts.cli.inject_gadget_into_apk')
@patch('scripts.cli.sign_apk')
def test_run_options(mock_sign_apk, mock_inject_gadget, mock_run_apktool, mock_detect_adb_arch):
    """Test 'run' command with various options."""
    runner = CliRunner()
    mock_detect_adb_arch.return_value = 'arm64' # Default mock value

    # Test --arch option
    result = runner.invoke(run, [DEMO_APK_PATH, '--arch', 'x86'])
    assert result.exit_code == 0
    mock_inject_gadget.assert_called_with(
        Path(DEMO_APK_PATH), 'x86', Path(f'scripts/temp/handtrackinggpu'), False, False, None, None, None, None, None
    )

    # Test --js option
    with runner.isolated_filesystem():
        with open('test.js', 'w') as f:
            f.write('console.log("test");')
        result = runner.invoke(run, [DEMO_APK_PATH, '--js', 'test.js'])
        assert result.exit_code == 0
        # Check that inject_gadget_into_apk was called with the js file (potentially wrapped)
        args, _ = mock_inject_gadget.call_args
        assert args[7] is not None # js argument
        assert 'test.js' in args[7] or '_wrapped.js' in args[7]


    # Test --config option
    with runner.isolated_filesystem():
        with open('config.json', 'w') as f:
            f.write('{"interaction": {"type": "script", "path": "script.js"}}')
        result = runner.invoke(run, [DEMO_APK_PATH, '--config', 'config.json'])
        assert result.exit_code == 0
        mock_inject_gadget.assert_called_with(
            Path(DEMO_APK_PATH), 'arm64', Path(f'scripts/temp/handtrackinggpu'), False, False, None, 'config.json', None, None, None
        )

    # Test --js-delay option (requires --js)
    with runner.isolated_filesystem():
        with open('test_delay.js', 'w') as f:
            f.write('console.log("delayed test");')
        result = runner.invoke(run, [DEMO_APK_PATH, '--js', 'test_delay.js', '--js-delay', '10'])
        assert result.exit_code == 0
        args, _ = mock_inject_gadget.call_args
        assert args[7] is not None and '_wrapped.js' in args[7] # js argument should be the wrapped version


    # Test --sign option
    result = runner.invoke(run, [DEMO_APK_PATH, '--sign'])
    assert result.exit_code == 0
    mock_sign_apk.assert_called()

    # Test --no-res option
    result = runner.invoke(run, [DEMO_APK_PATH, '--no-res'])
    assert result.exit_code == 0
    # Check that run_apktool was called with --no-res for decompile
    # The first call to run_apktool is for decompile
    decompile_call_args, _ = mock_run_apktool.call_args_list[0]
    assert '--no-res' in decompile_call_args[0]
    # Check that inject_gadget_into_apk was called with no_res=True
    args, _ = mock_inject_gadget.call_args
    assert args[3] is True # no_res argument

    # Test --force-manifest option
    result = runner.invoke(run, [DEMO_APK_PATH, '--force-manifest'])
    assert result.exit_code == 0
    # Check that run_apktool was called with --force-manifest for decompile
    decompile_call_args, _ = mock_run_apktool.call_args_list[0]
    assert '--force-manifest' in decompile_call_args[0]
     # Check that inject_gadget_into_apk was called with force_manifest=True
    args, _ = mock_inject_gadget.call_args
    assert args[4] is True # force_manifest argument

    # Test --custom-gadget-name option
    result = runner.invoke(run, [DEMO_APK_PATH, '--custom-gadget-name', 'mygadget'])
    assert result.exit_code == 0
    mock_inject_gadget.assert_called_with(
        Path(DEMO_APK_PATH), 'arm64', Path(f'scripts/temp/handtrackinggpu'), False, False, None, None, None, 'mygadget', None
    )

    # Test --skip-decompile option
    # Need to create a dummy decompiled directory for this test
    with runner.isolated_filesystem():
        Path(f'scripts/temp/handtrackinggpu').mkdir(parents=True, exist_ok=True)
        result = runner.invoke(run, [DEMO_APK_PATH, '--skip-decompile'])
        assert result.exit_code == 0
        # Assert that run_apktool was not called for decompilation (should only be called for recompile)
        assert mock_run_apktool.call_count == 1 # Only recompile
        assert 'd' not in mock_run_apktool.call_args[0][0] # 'd' is for decompile

    # Test --skip-recompile option
    result = runner.invoke(run, [DEMO_APK_PATH, '--skip-recompile'])
    assert result.exit_code == 0
    # Assert that run_apktool was not called for recompilation (should only be called for decompile)
    assert mock_run_apktool.call_count == 1 # Only decompile
    assert 'b' not in mock_run_apktool.call_args[0][0] # 'b' is for recompile

    # Test --use-aapt2 option
    result = runner.invoke(run, [DEMO_APK_PATH, '--use-aapt2'])
    assert result.exit_code == 0
    # Check that run_apktool was called with --use-aapt2 for recompile
    # The second call to run_apktool is for recompile (if not skipped)
    recompile_call_args, _ = mock_run_apktool.call_args_list[1] # Assuming decompile was also called
    assert '--use-aapt2' in recompile_call_args[0]


    # Test --decompile-opts option
    result = runner.invoke(run, [DEMO_APK_PATH, '--decompile-opts', '--no-crunch -v'])
    assert result.exit_code == 0
    decompile_call_args, _ = mock_run_apktool.call_args_list[0]
    assert '--no-crunch' in decompile_call_args[0]
    assert '-v' in decompile_call_args[0]

    # Test --recompile-opts option
    result = runner.invoke(run, [DEMO_APK_PATH, '--recompile-opts', '--verbose'])
    assert result.exit_code == 0
    recompile_call_args, _ = mock_run_apktool.call_args_list[1]
    assert '--verbose' in recompile_call_args[0]

    # Test --apktool-path option
    with patch('scripts.cli.Path.exists') as mock_path_exists:
        mock_path_exists.return_value = True # Mock that the apktool path exists
        result = runner.invoke(run, [DEMO_APK_PATH, '--apktool-path', '/custom/apktool'])
        assert result.exit_code == 0
        # Hard to directly check if APKTOOL global var was changed,
        # but we can check if run_apktool was called (indirectly implies apktool was found)
        assert mock_run_apktool.called

    # Test --frida-version option
    result = runner.invoke(run, [DEMO_APK_PATH, '--frida-version', '16.0.0'])
    assert result.exit_code == 0
    mock_inject_gadget.assert_called_with(
        Path(DEMO_APK_PATH), 'arm64', Path(f'scripts/temp/handtrackinggpu'), False, False, None, None, None, None, '16.0.0'
    )

    # Test invalid --js-delay without --js (should exit with error)
    result = runner.invoke(run, [DEMO_APK_PATH, '--js-delay', '5'])
    assert result.exit_code != 0 # Expecting error

    # Test invalid --js file not found (should exit with error)
    result = runner.invoke(run, [DEMO_APK_PATH, '--js', 'nonexistent.js'])
    assert result.exit_code != 0 # Expecting error

    # Test invalid --config file not found (should exit with error)
    result = runner.invoke(run, [DEMO_APK_PATH, '--config', 'nonexistent.json'])
    assert result.exit_code != 0

    # Test invalid --config file not valid JSON
    with runner.isolated_filesystem():
        with open('invalid_config.json', 'w') as f:
            f.write('this is not json')
        result = runner.invoke(run, [DEMO_APK_PATH, '--config', 'invalid_config.json'])
        assert result.exit_code != 0

    # Test invalid --arch option
    result = runner.invoke(run, [DEMO_APK_PATH, '--arch', 'invalid_arch'])
    assert result.exit_code != 0

    # Test --skip-decompile without existing decompiled directory
    with runner.isolated_filesystem(): # Ensure no pre-existing temp dir
        result = runner.invoke(run, [DEMO_APK_PATH, '--skip-decompile'])
        assert result.exit_code != 0 # Expecting error because dir won't exist


def test_wrap_js_with_timeout():
    """Test wrap_js_with_timeout function"""
    # Test case 1: Basic JavaScript content and delay
    js_content1 = "console.log('Hello');"
    delay1 = 5
    expected_output1 = """setTimeout(function() {
console.log('Hello');
}, 5000);"""
    assert wrap_js_with_timeout(js_content1, delay1) == expected_output1

    # Test case 2: Multi-line JavaScript content and delay
    js_content2 = """var x = 5;
if (x > 0) {
    console.log('Positive');
}"""
    delay2 = 10
    expected_output2 = """setTimeout(function() {
var x = 5;
if (x > 0) {
    console.log('Positive');
}
}, 10000);"""
    assert wrap_js_with_timeout(js_content2, delay2) == expected_output2

    # Test case 3: Zero delay
    js_content3 = "alert('Now!');"
    delay3 = 0
    expected_output3 = """setTimeout(function() {
alert('Now!');
}, 0);"""
    assert wrap_js_with_timeout(js_content3, delay3) == expected_output3

    # Test case 4: Empty JavaScript content
    js_content4 = ""
    delay4 = 3
    expected_output4 = """setTimeout(function() {

}, 3000);"""
    assert wrap_js_with_timeout(js_content4, delay4) == expected_output4


@patch('scripts.cli.subprocess.Popen')
def test_detect_adb_arch(mock_subproc_popen):
    """Test detect_adb_arch function."""
    from scripts.cli import detect_adb_arch

    # Helper to create a mock process
    def create_mock_process(stdout_data, stderr_data, return_code):
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (stdout_data.encode(), stderr_data.encode())
        mock_proc.returncode = return_code
        mock_subproc_popen.return_value.__enter__.return_value = mock_proc
        return mock_proc

    # Test case 1: Successful detection - arm64-v8a
    create_mock_process(stdout_data="arm64-v8a\n", stderr_data="", return_code=0)
    assert detect_adb_arch() == "arm64"
    mock_subproc_popen.assert_called_with(
        ["adb", "shell", "getprop", "ro.product.cpu.abi"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


    # Test case 2: Successful detection - armeabi-v7a
    create_mock_process(stdout_data="armeabi-v7a\n", stderr_data="", return_code=0)
    assert detect_adb_arch() == "arm"

    # Test case 3: Successful detection - x86
    create_mock_process(stdout_data="x86\n", stderr_data="", return_code=0)
    assert detect_adb_arch() == "x86"

    # Test case 4: Successful detection - x86_64
    create_mock_process(stdout_data="x86_64\n", stderr_data="", return_code=0)
    assert detect_adb_arch() == "x86_64"

    # Test case 5: ADB command fails (non-zero return code)
    create_mock_process(stdout_data="", stderr_data="device not found", return_code=1)
    assert detect_adb_arch() == "arm64"  # Fallback to default

    # Test case 6: ADB command returns empty output
    create_mock_process(stdout_data="\n", stderr_data="", return_code=0)
    assert detect_adb_arch() == "arm64"  # Fallback to default

    # Test case 7: ADB command returns unexpected output
    create_mock_process(stdout_data="unexpected_arch\n", stderr_data="", return_code=0)
    assert detect_adb_arch() == "unexpected_arch" # Should return the output as is if not arm64-v8a or armeabi-v7a

    # Test case 8: FileNotFoundError (adb not installed)
    mock_subproc_popen.side_effect = FileNotFoundError
    assert detect_adb_arch() == "arm64"  # Fallback to default

    # Test case 9: Other unexpected exception during Popen
    mock_subproc_popen.side_effect = Exception("Some other error")
    assert detect_adb_arch() == "arm64" # Fallback to default
    # Reset side effect for further tests if any, or ensure this is the last one modifying Popen globally
    mock_subproc_popen.side_effect = None


@patch('scripts.cli.Path.write_text')
@patch('scripts.cli.Path.read_text')
def test_modify_manifest(mock_read_text, mock_write_text):
    """Test modify_manifest function."""
    from scripts.cli import modify_manifest
    from pathlib import Path

    decompiled_path = Path("dummy_decompiled_path")

    # Case 1: Permission missing, extractNativeLibs missing (should default to true, so no change)
    manifest_v1_before = """<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application android:label="TestApp">
    </application>
</manifest>"""
    manifest_v1_after_expected = """<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application android:label="TestApp">
    </application>
<uses-permission android:name='android.permission.INTERNET'/></manifest>"""
    mock_read_text.return_value = manifest_v1_before
    modify_manifest(decompiled_path)
    mock_write_text.assert_called_once_with(manifest_v1_after_expected, encoding="utf-8")
    mock_read_text.reset_mock()
    mock_write_text.reset_mock()

    # Case 2: Permission present, extractNativeLibs="false"
    manifest_v2_before = """<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name='android.permission.INTERNET'/>
    <application android:label="TestApp" android:extractNativeLibs="false">
    </application>
</manifest>"""
    manifest_v2_after_expected = """<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name='android.permission.INTERNET'/>
    <application android:label="TestApp" android:extractNativeLibs="true">
    </application>
</manifest>"""
    mock_read_text.return_value = manifest_v2_before
    modify_manifest(decompiled_path)
    mock_write_text.assert_called_once_with(manifest_v2_after_expected, encoding="utf-8")
    mock_read_text.reset_mock()
    mock_write_text.reset_mock()

    # Case 3: Permission present, extractNativeLibs="true"
    manifest_v3_before = """<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name='android.permission.INTERNET'/>
    <application android:label="TestApp" android:extractNativeLibs="true">
    </application>
</manifest>"""
    manifest_v3_after_expected = manifest_v3_before # No change expected
    mock_read_text.return_value = manifest_v3_before
    modify_manifest(decompiled_path)
    # In this case, the content doesn't change, but write_text is still called.
    mock_write_text.assert_called_once_with(manifest_v3_after_expected, encoding="utf-8")
    mock_read_text.reset_mock()
    mock_write_text.reset_mock()

    # Case 4: Permission missing, extractNativeLibs="false"
    manifest_v4_before = """<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application android:label="TestApp" android:extractNativeLibs="false">
    </application>
</manifest>"""
    manifest_v4_after_expected = """<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application android:label="TestApp" android:extractNativeLibs="true">
    </application>
<uses-permission android:name='android.permission.INTERNET'/></manifest>"""
    mock_read_text.return_value = manifest_v4_before
    modify_manifest(decompiled_path)
    mock_write_text.assert_called_once_with(manifest_v4_after_expected, encoding="utf-8")
    mock_read_text.reset_mock()
    mock_write_text.reset_mock()

    # Case 5: Permission missing, extractNativeLibs present and true
    manifest_v5_before = """<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application android:label="TestApp" android:extractNativeLibs="true">
    </application>
</manifest>"""
    manifest_v5_after_expected = """<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application android:label="TestApp" android:extractNativeLibs="true">
    </application>
<uses-permission android:name='android.permission.INTERNET'/></manifest>"""
    mock_read_text.return_value = manifest_v5_before
    modify_manifest(decompiled_path)
    mock_write_text.assert_called_once_with(manifest_v5_after_expected, encoding="utf-8")
