frida-gadget
============================================================
| Easy to use Frida Gadget. 
| Inject loadlibary code to dex, insert gadget.so and add internet permssion to apk file. 
| You just install apktool and this. 


.. code:: sh

  $ pip install frida-gadgetor 
  $ frida-gadgetor [apk_path] --arch=[arch, default arm]
  > [SOMETHING DUMMY PRINT]
  > Gadget APK: [gadget_apk_path]
  $ adb install [gadget_apk_path]

