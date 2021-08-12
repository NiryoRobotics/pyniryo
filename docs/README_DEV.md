# Tuto Sphinx
## Pré-requis

1. (Vous pouvez passez cette partie si vous utilisez Docker).

    Pour modifier la doc, vous aurez tout d'abord besoin de Sphinx :

    `pip install Sphinx sphinx_rtd_theme`

2. Le dossier front_end est un [sous-module git](https://git-scm.com/book/fr/v2/Utilitaires-Git-Sous-modules),
    il peux donc être nécessaire de le mettre à jour régulièrement.
    Pour cloner / update le sous module front-end, veuillez effectuer la commande suivante:

    `git submodule update --init relative_path_to/front_end`


## Génération
Placez vous à la racine de votre dossier sphinx

Pour générer le html, utilisez : `make html`

Le fichier à ouvrir est : **_build/html/index.html**

Command clean + make + open : `make clean; make html ; google-chrome _build/html/index.html`


## Modification
Les pages qui s'affichent sont écrites en format _.rst_ et stockés dans le dossier _source_. 
Une fois le fichier créé, il faut l'ajouter au fichier _index.rst_ pour qu'il apparaisse.

## Si vous voulez recréer un dossier Sphinx
1) Aller dans le dossier du package en question
2) Créer un dossier sphinx, et aller dedans : `mdkir sphinx; cd sphinx`
3) Exécuter la commande `sphinx-quickstart` et faire les bons choix !

Pour pouvoir documenter des fichiers de votre dossier src, il faudra l'ajouter au path. 
Pour cela, on peut déjà ajouter le dossier mère au PYTHONPATH via le fichier _conf.py_
```python
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
```

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
