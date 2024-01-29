import os
import re
import sys
import platform
import subprocess

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable,
                      '-DCMAKE_INSTALL_PREFIX:PATH=/usr/local',
                     ]

        cfg = 'Debug' if self.debug else 'Release'
        #cfg = 'DEBUG'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2', 'VERBOSE=1']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        # We need to remove the cache file because pip makes new /tmp source directories each time
        print('remove cache')
        subprocess.check_call(['rm', '-f', 'CMakeCache.txt'], cwd=self.build_temp, env=env)
        print("should make a cmake call:")
        print(' '.join(['cmake', ext.sourcedir] + cmake_args), 'cwd={}'.format(self.build_temp), 'env={}'.format(env))
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        print("should make a build call:")
        print(['cmake', '--build', '.'] + build_args, 'cwd={}'.format(self.build_temp))
        #subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)
        subprocess.check_call(['make', 'install', 'VERBOSE=1'], cwd=self.build_temp)

if __name__ == "__main__":

    setup(
        ext_modules=[CMakeExtension('dripline_python')],
        cmdclass=dict(build_ext=CMakeBuild),
        packages=["dripline", "_dripline"],
        package_dir={
            'dripline': 'dripline',
            '_dripline': 'module_bindings',
        },
        scripts=["bin/dl-serve"],
    )
