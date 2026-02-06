{{ name | escape | underline }}

.. automodule:: {{ fullname }}

   {# -- SUB-MODULES -- #}
   {% block modules %}
   {% if modules %}
   .. rubric:: Modules

   .. autosummary::
      :toctree:
      :recursive:

   {% for item in modules %}
      {{ item }}
   {% endfor %}
   {% endif %}
   {% endblock %}

   {# -- CLASSES -- #}
   {% block classes %}
   {% if classes %}
   .. rubric:: Classes

   .. autosummary::
      :toctree:
      :nosignatures:

   {% for item in classes %}
      {{ item }}
   {% endfor %}
   {% endif %}
   {% endblock %}

   {# -- FUNCTIONS -- #}
   {% block functions %}
   {% if functions %}
   .. rubric:: Functions

   .. autosummary::
      :toctree:
      :nosignatures:

   {% for item in functions %}
      {{ item }}
   {% endfor %}
   {% endif %}
   {% endblock %}

   {# -- EXCEPTIONS -- #}
   {% block exceptions %}
   {% if exceptions %}
   .. rubric:: Exceptions

   .. autosummary::
      :toctree:
      :nosignatures:

   {% for item in exceptions %}
      {{ item }}
   {% endfor %}
   {% endif %}
   {% endblock %}