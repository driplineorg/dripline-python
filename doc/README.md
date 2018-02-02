# Documentation
This subdirectory contains source and support files for building sphinx-based documentation.
Most source files may be added directly to this directory, though subdirectories may be used for organization if desired.
Contents of general use include:
  - `index.rst`: the main page for the generated documentation, any new pages should be added to the table of contents in this file (or to a the table of contents of something in this top-level table of contents)
  - `_templates`: may contain rst tempalte files for generated API documentation (must be enabled in conf.py)
  - `tutorials`: contains several tutorials which are no-longer applicable to this repo, these need to be moved to dragonfly
  - `*.rst`: are the input files containing text content for the website
