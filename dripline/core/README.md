# dripline.core

Directory containing actual implementation of dripline.

Conventional notes:
  - Each module explicitly adds content to the `__all__` list
  - Each module should create a logger instance and use that rather than printing
  - Any class inheriting from another local class should make use of the `@fancy_doc` decorator
  - Any new source files need to be added to the `__init__.py` file so that they are included in the package.
