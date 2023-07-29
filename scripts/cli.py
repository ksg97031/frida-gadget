"""Frida gadget injector for Android APK"""
import os
import sys
import shutil
import subprocess
from shutil import which
from pathlib import Path
import click
from androguard.core.bytecodes.apk import APK
from .logger import logger
from .frida_github import FridaGithub
from . import INSTALLED_FRIDA_VERSION


p = Path(__file__)
ROOT_DIR = p.parent.resolve()
TEMP_DIR = ROOT_DIR.joinpath('temp')
FILE_DIR = ROOT_DIR.joinpath('files')

APKTOOL = which("apktool")
if not APKTOOL:
    raise FileNotFoundError(
        "Please download the 'apktool' and set it to your PATH environment.")

def run_apktool(option, apk_path: str):
    """Run apktool with option

    Args:
        option (list|str): option of apktool
        apk_path (str): path of apk file

    """
    if isinstance(option, list):
        cmd = [APKTOOL] + option + [apk_path]
    else:
        cmd = [APKTOOL, option, apk_path]

    pipe = subprocess.PIPE
    with subprocess.Popen(cmd, stdin=pipe, stdout=pipe, stderr=pipe) as process:
        _, stderr = process.communicate(b"\n")
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd, stderr)
        return True

def download_gadget(arch: str):
    """Download the frida gadget library

    Args:
        arch (str): architecture of the device
    """
    frida_github = FridaGithub(INSTALLED_FRIDA_VERSION)
    assets = frida_github.get_assets()
    file = f'frida-gadget-{INSTALLED_FRIDA_VERSION}-android-{arch}.so.xz'
    for asset in assets:
        if asset['name'] == file:
            logger.debug("Downloading the frida gadget library for %s", arch)
            so_gadget_path = str(FILE_DIR.joinpath(file[:-3]))
            return frida_github.download_gadget_so(asset['browser_download_url'], so_gadget_path)

    raise FileNotFoundError(f"'{file}' not found in the github releases")

def insert_loadlibary(decompiled_path, main_activity, load_library_name):
    """Inject loadlibary code to main activity

    Args:
        text (str): smali code of the main activity
    """
    logger.debug('Searching for the main activity in the smali files')
    target_smali = None

    target_relative_path = main_activity.replace(".", os.sep)

    for directory in decompiled_path.iterdir():
        if directory.is_dir() and directory.name.startswith("smali"):
            target_smali = directory.joinpath(target_relative_path + ".smali")
            if target_smali.exists():
                break

    if not target_smali or not target_smali.exists():
        raise FileNotFoundError(f"The target class file {target_smali} was not found.")

    logger.debug("Found the main activity at '%s'", str(target_smali))
    text = target_smali.read_text()

    text = text.replace(
        "invoke-virtual {v0, v1}, Ljava/lang/Runtime;->exit(I)V", "")
    text = text.split("\n")


    logger.debug(
        'Locating the entrypoint method and injecting the loadLibrary code')
    status = False
    entrypoints = ["onCreate(", "<init>"]
    for entrypoint in entrypoints:
        idx = 0
        while idx != len(text):
            line = text[idx].strip()
            if line.startswith('.method') and entrypoint in line:
                locals_line_bit = text[idx + 1].split(".locals ")
                locals_variable_count = int(locals_line_bit[1])
                locals_line_bit[1] = str(locals_variable_count + 1)
                if load_library_name.startswith('lib'):
                    load_library_name = load_library_name[3:]

                new_locals_line = ".locals ".join(locals_line_bit)
                text[idx + 1] = new_locals_line

                load_str = f'    const-string v{locals_variable_count}, "{load_library_name}"'
                load_library = f'    invoke-static {{v{locals_variable_count}}}, \
                    Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V'
                text.insert(idx + 2, load_library)
                text.insert(idx + 2, load_str)
                status = True
                break
            idx += 1

        if status:
            break

    if not status:
        issue_url = 'https://github.com/ksg97031/frida-gadget/issues'
        logger.error(
            "Cannot find the appropriate position in the main activity.")
        logger.error(
            "Please report the issue at %s with the following information:", issue_url)
        logger.error("APK Name: <Your APK Name>")
        logger.error("APK Version: <Your APK Version>")
        logger.error("APKTOOL Version: <Your APKTOOL Version>")
        sys.exit(-1)

    # Replace the smali file with the new one
    target_smali.write_text("\n".join(text))

def modify_manifest(decompiled_path):
    """Modify manifest permssions

    Args:
        decompiled_path (str): decomplied path of apk file
    """
    # Add internet permission
    logger.debug("Checking internet permission and extractNativeLibs settings")
    android_manifest = decompiled_path.joinpath("AndroidManifest.xml")
    txt = android_manifest.read_text(encoding="utf-8")
    pos = txt.index('</manifest>')
    permission = 'android.permission.INTERNET'

    if permission not in txt:
        logger.debug(
            "Adding 'android.permission.INTERNET' permission to AndroidManifest.xml")
        permissions_txt = f"<uses-permission android:name='{permission}'/>"
        txt = txt[:pos] + permissions_txt + txt[pos:]

    # Set extractNativeLibs to true
    if ':extractNativeLibs="false"' in txt:
        logger.debug('Editing the extractNativeLibs="true"')
        txt = txt.replace(':extractNativeLibs="false"',
                            ':extractNativeLibs="true"')
    android_manifest.write_text(txt, encoding="utf-8")

def inject_gadget_into_apk(apk_path:str, arch:str, decompiled_path:str):
    """Inject frida gadget into an APK

    Args:
        apk (APK): path of apk file
        arch (str): architecture of the device
        decompiled_path (str): decomplied path of apk file

    Raises:
        FileNotFoundError: file not found
        NotImplementedError: not implemented
    """
    apk = APK(apk_path)
    gadget_path = download_gadget(arch) # Download gadget library
    gadget_name = Path(gadget_path).name
    main_activity = apk.get_main_activity()
    # Apply permission to android manifest
    modify_manifest(decompiled_path)

    # Search the main activity from smali files
    load_library_name = gadget_name[:-3]
    insert_loadlibary(decompiled_path, main_activity, load_library_name)

    # Copy the frida gadget library to the lib directory
    lib = decompiled_path.joinpath('lib')
    if not lib.exists():
        lib.mkdir()
    arch_dirnames = {'arm': 'armeabi-v7a', 'x86':'x86', 'arm64': 'arm64-v8a', 'x86_64':'x86_64'}
    if arch not in arch_dirnames:
        raise NotImplementedError(f"The architecture '{arch}' is not supported.")

    arch_dirname = arch_dirnames[arch]
    lib = lib.joinpath(arch_dirname)
    if not lib.exists():
        lib.mkdir()

    lib_library_name = gadget_name
    if not lib_library_name.startswith('lib'):
        lib_library_name = 'lib' + gadget_name
    shutil.copy(gadget_path, lib.joinpath(lib_library_name))

    logger.debug('Recompiling the new APK using apktool')



@click.command()
@click.option('--arch', default="arm64", help='Support [arm, arm64, x86, x86_64]')
@click.option('--skip-decompile', is_flag=True)
@click.option('--skip-recompile', is_flag=True)
@click.argument('apk_path', type=click.Path(exists=True), required=True)
def run(apk_path: str, skip_decompile:bool, skip_recompile:bool, arch: str):
    """Patch an APK with the Frida gadget library

    Args:
        apk_path (str): Path of the target APK file
        arch (str): Target architecture of the device

    Outputs:
        Injected APK file
    """
    apk_path = Path(apk_path)

    logger.info("APK: '%s'", apk_path)
    logger.info("Gadget Architecture(--arch): %s%s", arch, "(default)" if arch == "arm64" else "")

    arch = arch.lower()
    supported_archs = ['arm', 'arm64', 'x86', 'x86_64']
    if arch not in supported_archs:
        logger.error(
            "The --arch option only supports the following architectures: %s",
            ", ".join(supported_archs)
        )
        sys.exit(-1)

    # Make temp directory for decompile
   
    decompiled_path = TEMP_DIR.joinpath(str(apk_path.resolve())[:-4])
    if not skip_decompile:
        logger.debug("Decompiling the target APK using apktool")
        if decompiled_path.exists():
            shutil.rmtree(decompiled_path)
        decompiled_path.mkdir()

        # APK decompile with apktool
        run_apktool(['d', '-o', str(decompiled_path.resolve()), '-f'], str(apk_path.resolve()))

    # Process if decompile is success
    inject_gadget_into_apk(apk_path, arch, decompiled_path)

    # Rebuild with apktool, print apk_path if process is success
    if not skip_recompile:
        run_apktool('b', str(decompiled_path.resolve()))
        apk_path = decompiled_path.joinpath('dist', apk_path.name)
        logger.info('Success: %s', str(apk_path.resolve()))


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    run()
