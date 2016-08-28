#! /usr/bin/python
#
# Gets a pkgbuild and builds a list of required packages
# Also returns a list of pkgs build by this PKGBUILD
# Might be better to build tokenizer to go over regexes
#
##########################################################################

class Deps(object):
    def __init__(self, pkg_name: str, pkg_deps: [str]):
        self.pkg_name = pkg_name
        self.pkg_deps = pkg_deps
        self.child_deps = []
        

import subprocess

pkgs = []
bld_pkgs = []

built_pkgs = subprocess.run(["makepkg", "--printsrcinfo"], stdout=subprocess.PIPE, universal_newlines=True).stdout.split("\n\n")
# First part gets base stuff
for baseP in built_pkgs[0].split("\n"):
    if "depends = " in baseP and "optdepends =" not in baseP:
        pkgs.append(baseP.strip().split("=")[1])
for i in range(1, len(built_pkgs) - 1):
    built_pkg = built_pkgs[i].split("\n")
    bld_pkgs2 = pkgs.copy()
    pkg_name = built_pkg[0].strip().split("=")[0]
    for builtP in built_pkg:
        if "depends = " in builtP and "optdepends =" not in builtP:
            bld_pkgs2.append(builtP.strip().split("=")[1])
    bld_pkgs.append(Deps(pkg_name, bld_pkgs2))


for pkg in bld_pkgs:
    print(pkg.pkg_deps)
        
#
#  makepkg --packagelist
# a2ps-4.14-7-i686
# a2ps-4.14-7-x86_64
# ls:  a2ps-4.14-7-x86_64.pkg.tar.xz
#
# These options can be passed to pacman:
#
#  --asdeps         Install packages as non-explicitly installed
#
# Going to have to edit PKGBUILD to remove unneeded packages
#
