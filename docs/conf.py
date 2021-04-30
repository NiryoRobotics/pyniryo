import os
import sys

sys.path.insert(0, os.path.abspath('../pyniryo'))

# -- Project information -----------------------------------------------------

project = u'PyNiryo'
copyright = " ".join([
    "2021, Niryo All rights reserved.",
    "No part of this document may be reproduced or transmitted in any form or by any",
    "means without prior written consent of Niryo SAS"
])
author = u'Niryo Software Team'

# The short X.Y version
version = u'1.0'
# The full version, including alpha/beta/rc tags
release = u'1.0.0a'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.extlinks',
    'sphinx.ext.todo',
]

# Avoid autosection label to trigger warning on low level titles
autosectionlabel_maxdepth = 3

# Todo_extension
todo_include_todos = True
todo_emit_warnings = True

# Documentation infos
source_suffix = '.rst'
master_doc = 'index'


def generate_dict_trad(lang):
    import json

    def update_dict_recursive(base_dict, new_dict):
        # Iterate over keys
        for key in base_dict:
            if key not in new_dict:
                continue
            # If key is related to a dict, go deeper
            if type(base_dict[key]) == dict:
                update_dict_recursive(base_dict[key], new_dict[key])
            # Update key
            else:
                base_dict[key] = new_dict[key]

    # Use english dict as default dict !
    with open("front_end/trad/en.json") as json_file:
        dict_trad = json.load(json_file)

    # If language selected, update the dict !
    if lang is not None:
        with open('front_end/trad/{}.json'.format(lang)) as json_file:
            sub_dict_trad = json.load(json_file)
            update_dict_recursive(dict_trad, sub_dict_trad)

    return dict_trad


for arg in sys.argv:
    if not arg.startswith("language="):
        continue
    else:
        language = arg.replace("language=", "")
        break
else:
    language = None

html_context = generate_dict_trad(language)

exclude_patterns = [u'_build', 'Thumbs.db', '.DS_Store']

pygments_style = None

add_module_names = False

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'

templates_path = ['front_end/templates/']
html_static_path = ['front_end/static/']

html_logo = "images/PyNiryo_logo_1.png"
html_favicon = html_static_path[0] + "favicon32.ico"

html_css_files = [
    'override.css'
]

html_js_files = [
    'app.js',
]

html_theme_options = {
    # 'analytics_id': 'UA-XXXXXX-X',  #  Provided by Google in your dashboard
}

# -- Options for intersphinx extension ---------------------------------------

# Links
extlinks = {
}

# -- Internationalization --
locale_dirs = ['locale/']  # path is example but recommended.
gettext_compact = False  # optional.

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'https://docs.python.org/': None,
}
