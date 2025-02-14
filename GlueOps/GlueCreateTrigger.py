from smda_libraries import *
import datetime
# job_start_time = datetime.now()

glue_client = get_glue_client()

glue_jobs_resp = glue_client.list_jobs(MaxResults=200, Tags = {'smda': 'etl-job'})
# print(json.dumps(glue_jobs_resp, indent=4, sort_keys=True, default=str))

args_list = []
for glue_job_name in glue_jobs_resp['JobNames']:
    # print(glue_job)
    args_dict = {"Arguments": {}, "JobName": glue_job_name, "Timeout": 30}
    args_list.append(args_dict)

# Create trigger
create_trig_resp = glue_client.create_trigger(Name='smda-workflow-trigger',
                                            Type='SCHEDULED',
                                            Schedule="cron(30 00 * * ? *)",
                                            Actions= args_list,
                                            StartOnCreation=False,
                                            Tags = {'smda': 'etl-trigger'}
                                        )
print(json.dumps(create_trig_resp, indent=4, sort_keys=True, default=str))
