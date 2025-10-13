from smda_libraries import *
import datetime
# job_start_time = datetime.now()


ecs_client = get_ecs_client()

list_tasks_response = ecs_client.list_tasks(
    cluster="ecs-cluster-smda"
    # desiredStatus='RUNNING'  # Filter to show only running tasks
)

print(list_tasks_response)

response = ecs_client.describe_tasks(cluster='ecs-cluster-smda', tasks=['c2f96505f652457c8ec705c6006d1d8d',])
print(response)
print()
print(response['tasks'][0]['overrides'])
print()

#['tasks'][0]['attachments'][0]['details'][1]
# for k,v in response.items():
#     print(f"{k}\n{v}")
