from smda_libraries import *
import datetime
# job_start_time = datetime.now()
ecs_client = get_ecs_client()

# get task definitions list
# response = ecs_client.list_task_definitions(familyPrefix='td-smda')
# print(response)

# # get clusters list
# response = ecs_client.list_clusters()
# print(response)

# # get contaienr instances list
# ecs_container_intsnc_resp = ecs_client.list_container_instances(
#     cluster="arn:aws:ecs:us-east-1:621799566105:cluster/ecs-cluster-smda"
# )
# print(ecs_container_intsnc_resp)

# task_overrides = {
#     'containerOverrides': [
#         {
#             'name': 'cntnr-smda-Paper', # Must match the container name in your task definition
#             'environment': [
#                 {
#                     'name': 'Sector',
#                     'value': 'Paper'
#                 }
#             ]
#         }
#     ]
# }
# start_ecs_task_resp = ecs_client.start_task(
# cluster="ecs-cluster-smda",
# # containerInstances=[CONTAINER_INSTANCE_ARN],
# taskDefinition="arn:aws:ecs:us-east-1:621799566105:task-definition/td-smda:3",
# overrides=task_overrides
# )
# print(start_ecs_task_resp)

desc_tasks_resp = ecs_client.describe_tasks(cluster="ecs-cluster-smda")
print(desc_tasks_resp)

