import json
import os
from pathlib import Path

script_dir = os.path.dirname(__file__)

cwd = Path(__file__).parents[3]
fileName = cwd/'properties.json'

with open(fileName) as fp:
	properties = json.load(fp)
properties

working_directory = Path(__file__).parents[1]
sonata_example_schema = working_directory/'schemas/sonata_schemas/example_schemas.json'

with open(sonata_example_schema) as fe:
	example_schema = json.load(fe)
example_schema

current_directory = Path(__file__).parents[0]
common_example_schema = current_directory/'example_schemas.json'

with open(common_example_schema) as file:
	common_schema = json.load(file)
common_schema

interlude_payloads = current_directory/'interlude_payload.json'
with open(interlude_payloads) as data:
	interlude_extra_payload = json.load(data)
interlude_extra_payload


file_name = 'field_mapping.json'
field_map_file_name = current_directory / file_name
with open(field_map_file_name) as data:
	field_mapping_key_val = json.load(data)
field_mapping_key_val
