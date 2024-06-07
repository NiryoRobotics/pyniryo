# Sphinx Tutorial
## Prerequisites

To modify the documentation, you will first need Sphinx and its extensions:

It is advised to install sphinx in a python virtualenv

```
pip install -r docs/requirements.txt
``` 


## Commands
Inside your sphinx directory (`cd docs`):

### Generate the html
```bash
make html
```

### Preview the generated doc

```bash
x-www-browser _build/html/index.html
```

### Delete the generated files
```bash
make clean
```

### Live reload
```
sphinx-autobuild . _build/html --open-browser 
```
Use `--open-browser` to automatically open a browser page to the live reload server

## Modification
The pages that are displayed are written in _.rst_ format. 
Once the file is created, it needs to be added to the _index.rst_ file for it to appear.

## Ressources
#### Syntaxe
http://openalea.gforge.inria.fr/doc/openalea/doc/_build/html/source/sphinx/rest_syntax.html

#### Memo
https://rest-sphinx-memo.readthedocs.io/en/latest/index.html

#### Add Links
https://sublime-and-sphinx-guide.readthedocs.io/en/latest/references.html

#### Directives
https://docutils.sourceforge.io/docs/ref/rst/directives.html

#### References
https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#cross-referencing-arbitrary-locations

#### Domains
https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html

### Theme Customization
https://sphinx-rtd-theme.readthedocs.io/en/latest/index.html
