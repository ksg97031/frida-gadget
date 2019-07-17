import os
import sys
import re
import click
import shutil
from pathlib import Path
from subprocess import check_output
from androguard.core.bytecodes.apk import APK

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
@click.option('--arch', default='arm', help='Support "arm" and "arm64"')
@click.argument('apk_path')
def run(apk_path: str, arch: str):
    apk = APK(apk_path)
    apk_path = Path(apk_path)

    gadget_so_paths = {'arm':'libfrida-gadget-12.6.10-android-arm.so', 'arm64':'libfrida-gadget-12.6.10-android-arm64.so'}
    if arch not in gadget_so_paths:
        raise Exception("Can't find the target arch: " + arch)

    p_gadget_so = FILE_DIR.joinpath(gadget_so_paths[arch])
    if not p_gadget_so.exists():
        raise Exception("Can't find the target so file: " + str(p_gadget_so.resolve()))

    # Set main activity
    main_activity = apk.get_main_activity()
    main_activity = main_activity.split('.')
    main_activity[-1] += '.smali'

    # APK decompile with apktool
    decompiled_path = TEMP_DIR.joinpath(str(apk_path.resolve())[:-4])
    if decompiled_path.exists():
        shutil.rmtree(decompiled_path)

    decompiled_path.mkdir()
    result = run_apktool(
        ['d', '-o', str(decompiled_path.resolve()), '-f'], str(apk_path.resolve()))

    if result:
        # Add internet permissions
        android_manifest = decompiled_path.joinpath("AndroidManifest.xml")
        txt = android_manifest.read_text()
        pos = txt.index('</manifest>')
        permission = 'android.permission.INTERNET'

        if permission not in txt:
            permissions_txt = "<uses-permission android:name='%s'/>" % permission
            txt = txt[:pos] + permissions_txt + txt[pos:]

        if ':extractNativeLibs="false"' in txt:
            txt = txt.replace(':extractNativeLibs="false"', ':extractNativeLibs="true"')
        android_manifest.write_text(txt)

        # Read main activity smali code
        target_smali = None
        for smali_dir in decompiled_path.glob("smali*/"):
            target_smali = smali_dir.joinpath(*main_activity)
            if target_smali.exists():
                break

        if not target_smali or not target_smali.exists():
            raise Exception("Not Found, target class file: " +
                                ".".join(main_activity))
        text = target_smali.read_text()
        text = text.replace("invoke-virtual {v0, v1}, Ljava/lang/Runtime;->exit(I)V", "")
        text = text.split("\n")

        # Find onCreate method and inject loadLibary code for frida gadget
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
            raise Exception("Not Found, onCreate")
         
        target_smali.write_text("\n".join(text)) # rewrite main_activity smali file

        # Copy gadget library to app library directory 
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

        # Rebuild with apktool, print apk_path if process is success 
        result = run_apktool('b', str(decompiled_path.resolve()))
        if result:
            apk_path = decompiled_path.joinpath('dist', apk_path.name)
            print('Gadget APK: ' + str(apk_path.resolve()))
        else:
            shutil.rmtree(decompiled_path)


if __name__ == '__main__':
    run()
