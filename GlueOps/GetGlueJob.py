from smda_libraries import *
import datetime
# job_start_time = datetime.now()

glue_client = get_glue_client()

response = glue_client.get_job(JobName='smda-workflow')
for k,v in response['Job'].items():
    print(f"{k}\n\t{v}")

print()
for k,v in response['ResponseMetadata'].items():
    print(f"{k}\n\t{v}")
