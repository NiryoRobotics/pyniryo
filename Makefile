SHELL := /bin/bash

venv:
	virtualenv venv
	source venv/bin/activate && pip install -r requirements.txt

gen_openapi:
	source venv/bin/activate && datamodel-codegen --input $(SPECS_DIR)/openapi.yml --output pyniryo/nate/_internal/transport_models/models_gen.py --output-model-type pydantic_v2.BaseModel --input-file-type openapi
	source venv/bin/activate && scripts/generate_paths.py $(SPECS_DIR)/openapi.yml --output pyniryo/nate/_internal/paths_gen.py

gen_asyncapi:
	source venv/bin/activate && scripts/generate_asyncapi_models.py $(SPECS_DIR)/asyncapi.yaml -o pyniryo/nate/_internal/transport_models/async_models_gen.py
	source venv/bin/activate && scripts/generate_topics.py $(SPECS_DIR)/asyncapi.yaml --output pyniryo/nate/_internal/topics_gen.py

gen: gen_openapi gen_asyncapi