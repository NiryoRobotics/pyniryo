SHELL := /bin/bash

venv:
	virtualenv venv
	source venv/bin/activate && pip install -r requirements.txt

gen_openapi:
	source venv/bin/activate && datamodel-codegen --input $(SPEC) --output pyniryo/nate/_internal/transport_models/models_gen.py --output-model-type pydantic_v2.BaseModel --input-file-type openapi
	source venv/bin/activate && scripts/generate_paths.py $(SPEC) --output pyniryo/nate/_internal/paths_gen.py

gen: gen_openapi