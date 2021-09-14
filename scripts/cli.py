import os
import sys
import re
import click
import shutil
import logging
from time import sleep
from tqdm import tqdm
from pathlib import Path
from subprocess import check_output
from colorlog import ColoredFormatter
from androguard.core.bytecodes.apk import APK

DEBUG_STEPS = [None, 'aftermanifest']
DEBUG_STEP = DEBUG_STEPS[0]

# LOGGING
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = ColoredFormatter(
    "%(log_color)s[%(levelname)s] %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'white,bold',
        'INFOV':    'cyan,bold',
        'WARNING':  'yellow',
        'ERROR':    'red,bold',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)
ch.setFormatter(formatter)
logger = logging.getLogger('frida-gadget')
logger.setLevel(logging.DEBUG)
logger.addHandler(ch)

# APKTOOL, GADGET PATH
import shutil
from pathlib import Path
p = Path(__file__)
ROOT_DIR = p.parent.resolve()
TEMP_DIR = ROOT_DIR.joinpath('temp')
FILE_DIR = ROOT_DIR.joinpath('files')

binaries = ['apktool']
for binary in binaries:
    path = shutil.which(binary)
    if not path:
        raise Exception("Please download and set to your environment this file: " + binary)

    locals()[binary] = path

def run_apktool(option, apk_path: str):
    if isinstance(option, list):
        cmd = [apktool] + option + [apk_path]
    else:
        cmd = [apktool, option, apk_path]
    try:
        output = check_output(cmd)
    except:
        raise Exception("Error", " ".join(cmd))

    return True

@click.command()
@click.option('--arch', default="arm64", help='Support [arm, arm64, x86]')
@click.argument('apk_path')
def run(apk_path: str, arch: str):
    if not os.path.exists(apk_path):
        logger.error("Can't find the target APK '{}'".format(apk_path))
        sys.exit(-1)
    
    apk = APK(apk_path)
    apk_path = Path(apk_path)

    logger.info("APK : '{}'".format(apk_path))
    logger.info("Gadget Architecture(--arch) : '{}'".format(arch))

    gadget_so_paths = {'arm':'libfrida-gadget-15.1.1-android-arm.so', 'arm64':'libfrida-gadget-15.1.1-android-arm64.so', 'x86':'libfrida-gadget-15.1.1-android-x86.so'}
    if arch not in gadget_so_paths:
        logger.error("--arch option only support [{}]")
        sys.exit(-1)

    p_gadget_so = FILE_DIR.joinpath(gadget_so_paths[arch])
    if not p_gadget_so.exists():
        raise Exception("Can't find the target so file: " + str(p_gadget_so.resolve()))

    # Set main activity
    main_activity = apk.get_main_activity()
    main_activity = main_activity.split('.')
    main_activity[-1] += '.smali'

    # APK decompile with apktool
    logger.debug("Decompiling the target APK using apktool")
    decompiled_path = TEMP_DIR.joinpath(str(apk_path.resolve())[:-4])
    if decompiled_path.exists():
        shutil.rmtree(decompiled_path)

    decompiled_path.mkdir()
    result = run_apktool(['d', '-o', str(decompiled_path.resolve()), '-f'], str(apk_path.resolve()))

    if result:
        logger.debug("Checking the internet, extractNativeLibs settings")
        # Add internet permissions
        android_manifest = decompiled_path.joinpath("AndroidManifest.xml")
        txt = android_manifest.read_text()
        pos = txt.index('</manifest>')
        permission = 'android.permission.INTERNET'

        if permission not in txt:
            logger.debug("Adding 'android.permission.INTERNET' permission to AndroidManifest.xml")
            permissions_txt = "<uses-permission android:name='%s'/>" % permission
            txt = txt[:pos] + permissions_txt + txt[pos:]

        if ':extractNativeLibs="false"' in txt:
            logger.debug('Editing the extractNativeLibs="true"')
            txt = txt.replace(':extractNativeLibs="false"', ':extractNativeLibs="true"')
        android_manifest.write_text(txt)

        if DEBUG_STEP != DEBUG_STEPS[1]:
            # Read main activity smali code
            logger.debug('Searching the main activity from smali files')
            target_smali = None
            for smali_dir in decompiled_path.glob("smali*/"):
                target_smali = smali_dir.joinpath(*main_activity)
                if target_smali.exists():
                    break

            if not target_smali or not target_smali.exists():
                raise Exception("Not Found, target class file: " + ".".join(main_activity))

            logger.debug("Main activity founded at '{}'".format(str(target_smali)))
            text = target_smali.read_text()
            text = text.replace("invoke-virtual {v0, v1}, Ljava/lang/Runtime;->exit(I)V", "")
            text = text.split("\n")

            # Find onCreate method and inject loadLibary code for frida gadget
            logger.debug('Finding the onCreate method and inject loadLibrary code')
            idx = 0
            flag = False
            while idx != len(text):
                line = text[idx].strip()
                if line.startswith('.method') and "onCreate(" in line:
                    locals_line_bit = text[idx + 1].split(".locals ")
                    locals_variable_count = int(locals_line_bit[1])
                    locals_line_bit[1] = str(locals_variable_count + 1)
                    new_locals_line = ".locals ".join(locals_line_bit)
                    text[idx + 1] = new_locals_line

                    load_str = '    const-string v%d, "%s"' % (
                        locals_variable_count, p_gadget_so.name[3:-3])
                    load_library = '    invoke-static {v%d}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V' % (
                        locals_variable_count)
                    text.insert(idx + 2, load_library)
                    text.insert(idx + 2, load_str)
                    flag = True
                    break
                idx += 1

            if not flag:
                logger.error("Can't find the onCreate method in main activity")
                logger.error("Please request issue to https://github.com/ksg97031/frida-gadget/issues")
                sys.exit(-1)
             
            target_smali.write_text("\n".join(text)) # rewrite main_activity smali file

            # Copy gadget library to app's library directory 
            lib = decompiled_path.joinpath('lib')
            if not lib.exists():
                lib.mkdir()
            arch_dirnames = {'arm':'armeabi-v7a', 'arm64': 'arm64-v8a'}
            if arch not in arch_dirnames:
                raise Exception('The architecture "%s" is not support' % arch)

            arch_dirname = arch_dirnames[arch]
            lib = lib.joinpath(arch_dirname)
            if not lib.exists():
                lib.mkdir()
            shutil.copy(p_gadget_so, lib.joinpath(p_gadget_so.name))

            logger.debug('Recompiling the new APK using apktool')
        # Rebuild with apktool, print apk_path if process is success 
        result = run_apktool('b', str(decompiled_path.resolve()))
        if result:
            apk_path = decompiled_path.joinpath('dist', apk_path.name)
            logger.info('Success : ' + str(apk_path.resolve()))
            return 0
        else:
            shutil.rmtree(decompiled_path)
            return -1

if __name__ == '__main__':
    run()
