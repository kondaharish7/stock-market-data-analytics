from smda_libraries import *

glue_client = get_glue_client()

response = glue_client.get_trigger(Name='smda-trigger-2')
print(json.dumps(response, indent=4, sort_keys=True, default=str))
