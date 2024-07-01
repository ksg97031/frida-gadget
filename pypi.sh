rm -rf dist/* &&
python setup.py sdist &&
twine check dist/* &&
twine upload -r frida-gadget dist/*
