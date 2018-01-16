# http://nfoti.github.io/a-creative-blog-name/posts/2013/02/07/cleaning-cython-build-files/
import sysconfig

import os
import sys
import subprocess

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from distutils.core import setup
from Cython.Build import cythonize



args = sys.argv[1:]

# Make a `cleanall` rule to get rid of intermediate and library files
if "cleanall" in args:
    print("Deleting cython files...")
    # Just in case the build directory was created by accident,
    # note that shell=True should be OK here because the command is constant.
    subprocess.Popen("rm -rf build", shell=True, executable="/bin/bash")
    subprocess.Popen("rm -rf *.c", shell=True, executable="/bin/bash")
    subprocess.Popen("rm -rf *.so", shell=True, executable="/bin/bash")

    # Now do a normal clean
    sys.argv[1] = "clean"
# We want to always use build_ext --inplace
elif args.count("build_ext") > 0 and args.count("--inplace") == 0:
    sys.argv.insert(sys.argv.index("build_ext")+1, "--inplace")
# Only build for 64-bit target

if args.count("build_ext") > 0:
    os.environ['ARCHFLAGS'] = "-arch x86_64"
#     setup(
#       name = 'api',
#       ext_modules=[
#         Extension('api',
#                   sources=,
#                   extra_compile_args=['-Ofast'])
#         ],
#       cmdclass = {'build_ext': build_ext}
#     )

    setup(
        name = 'api',
        ext_modules = cythonize(["sandman2/*.py"]),
    )

