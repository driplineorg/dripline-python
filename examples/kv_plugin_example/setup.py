from setuptools import setup

def set_version_data():
    import subprocess
    import re
    version_data = {}
    pwd = subprocess.check_output(['pwd'])
    print("pwd: {}".format(pwd))
    origin = subprocess.check_output(['git', 'remote', 'get-url', 'origin'])
    print("raw origin: '{}'".format(origin))

setup(
    use_scm_version={
        "root": "../..",
        "write_to": "./examples/kv_plugin_example/version.py",
    },
    setup_requires=['setuptools_scm'],
    name="kv_plugin",
    packages=['dripline.extensions.kve'],
)
