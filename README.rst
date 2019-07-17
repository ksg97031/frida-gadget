frida-gadget
============================================================
| Easy to use Frida Gadget. 
| 
| [Features] 
| 1. Inject loadlibary code to dex
| 2. Insert libfrida-gadget.so to lib/ directory
| 3. Add internet permssion to AndroidManifext.xml


.. code:: sh

  $ pip install frida-gadget 

  $ frida-gadget [apk_path] --arch=[arch, default arm]
  > [SOMETHING DUMMY PRINT]
  > Gadget APK: [gadget_apk_path]

  $ adb install [gadget_apk_path]

