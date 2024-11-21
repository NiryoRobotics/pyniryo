import sys
import os
from datetime import date

sys.path.append(os.path.abspath('../pyniryo'))
# Kindda hack the import to import shared config file
sys.path.append(os.path.abspath('.'))

# Pdf options

## Header
pdf_header_font_name = "semplicitapro"

pdf_header_font_color = 203567

pdf_header_font_size = 16

pdf_header_spacing = 5  # In mm

## Footer

pdf_footer_font_name = "open-sans"

pdf_footer_font_color = 333333

pdf_footer_font_size = 10

pdf_footer_spacing = 5  # In mm

# front_end.config.base_conf ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.extlinks',
    'sphinx.ext.todo',
    'sphinx.ext.ifconfig',
    'sphinx_tabs.tabs',
    'sphinx_togglebutton'
]

# -- General configuration ---------------------------------------------------

# -- Project information -----------------------------------------------------

project = u'PyNiryo'
copyright = " ".join([
    str(date.today().year) + ", Niryo All rights reserved.",
    "No part of this document may be reproduced or transmitted in any form or by any",
    "means without prior written consent of Niryo SAS"
])
author = u'Niryo'

# The short X.Y version
version = u'v1.0'
# The full version, including alpha/beta/rc tags
release = u'v1.0.4'

# -- General configuration ---------------------------------------------------

# code snippet which will be added to the top of every rst file
rst_prolog = """
.. role:: python(code)
   :language: python

"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
# html_static_path = ['_static']
html_theme_options = {
    'analytics_id': 'UA-85632199-1',  #  Provided by Google in your dashboard
    "collapse_navigation": False
}

# Avoid autosection label to trigger warning on low level titles
autosectionlabel_maxdepth = 3
# Avoid clash between same label in different document
autosectionlabel_prefix_document = True

# Todo_extension
todo_include_todos = True
todo_emit_warnings = True

# Documentation infos
source_suffix = '.rst'
master_doc = 'index'

for arg in sys.argv:
    if not arg.startswith("language="):
        continue
    else:
        language = arg.replace("language=", "")
        break
else:
    language = 'en'

translation_object = {}
translation_object["fr"] = {}
translation_object["fr"]["PROJECT_NAME"] = "PyNiryo"

translation_object["en"] = {}
translation_object["en"]["PROJECT_NAME"] = "PyNiryo"

html_context = {}

html_context["BASE_FOLDER_URL"] = "https://docs.niryo.com/dev/pyniryo"

html_context["TRANSLATION"] = translation_object[language if language is not None else 'en']

exclude_patterns = [u'_build', 'Thumbs.db', '.DS_Store']

pygments_style = None

add_module_names = False

# -- Options for intersphinx extension ---------------------------------------

# Links
extlinks = {}

# -- Internationalization --
locale_dirs = ['locale/']  # path is example but recommended.
gettext_compact = False  # optional.
