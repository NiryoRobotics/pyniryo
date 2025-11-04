# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import re
import sys
from datetime import date
from pathlib import Path

module_directory = Path(__file__).parent.parent.absolute()
sys.path.append(str(module_directory))

project = 'PyNiryo'
copyright = f'{date.today().year}, Niryo'
author = 'Niryo'

file_content = module_directory.joinpath('pyniryo/version.py').read_text()
release = re.match(r'__version__ = ["\']((\d+\.?){3})', file_content)[1]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx_copybutton', 'sphinxemoji.sphinxemoji']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'en'

# code snippet which will be added to the top of every rst file
rst_prolog = """
.. role:: python(code)
   :language: python
   
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
# html_static_path = ['_static']
html_theme_options = {"collapse_navigation": False}

# -- AutoDoc configuration ---------------------------------------------------

# use the __init__ docstring instead of the class docstring for the class documentation
autoclass_content = 'init'
autodoc_default_flags = {
    'members': True,  # generate the doc recursively
    'undoc-members': True,  # also generate the doc for the undocumented members
    'member-order': 'bysource',  # display the members ordered by source (default: alphabetically)
}

# display the typehints in the function signature and the docstring
autodoc_typehints = 'both'

# mock the import, this avoid having to install it for building the doc
autodoc_mock_imports = ["cv2"]
