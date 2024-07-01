rm -rf dist/* &&
python setup.py sdist &&
twine upload -r frida-gadget dist/*
