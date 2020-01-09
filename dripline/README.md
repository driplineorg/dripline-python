Top-level of dripline source tree.

## Navigation

### core/
Contains python classes which expand the capabilities of the bound dripline-cpp classes, or other important core behaviors.
Everything in this directory is considered highly-generic and widely useful.

### implementations/
Contains classes intended for direct use and/or subclassing in production meshes which are at least somewhat specialized.
To be included in dripline-python (rather than a plugin package), these classes should still attempt to be quite generic in implementation, but they may make some assumptions and not cover all cases.

### extensions
Directory creating a namespace to be extended by plugin namespace packages.
Nothing is or may be added in this repo, plugins will add content.
