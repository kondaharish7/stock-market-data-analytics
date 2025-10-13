from smda_libraries import *
# job_start_time = datetime.now()

events_client = get_aws_service_client(aws_service='events')

# --- Configuration --- #
Rule_Name = 'rule-smda-ecs-3'
smda_ecs_cluster_arn = "arn:aws:ecs:us-east-1:621799566105:cluster/ecs-cluster-smda"
smda_task_definition_arn = "arn:aws:ecs:us-east-1:621799566105:task-definition/td-smda:4"
Ecs_events_role_arn = "arn:aws:iam::621799566105:role/ecsEventsRole"
Ecs_Task_role_arn = "arn:aws:iam::621799566105:role/ecsTaskExecutionRole"
subnet_ids_list = ['subnet-f61fe2d7','subnet-1c2cdf43','subnet-038beb7d314647592']
security_grp_list = ["sg-bc1c2092"]

CONTAINER_OVERRIDES = '"containerOverrides": [{"name": "cntnr-smda", "environment": [{"name": "Sector", "value": "Aviation"}]}]}'

ecs_target_config = {
    'Id': 'tgt-smda-Aviation',  # A unique ID for the target
    'Arn': smda_ecs_cluster_arn, # Arn of the Target service
    'RoleArn': Ecs_events_role_arn,
    'Input': CONTAINER_OVERRIDES,
    'EcsParameters': {
        'TaskDefinitionArn': smda_task_definition_arn,
        'LaunchType': 'FARGATE',
        'PlatformVersion': 'LATEST',
        'NetworkConfiguration': {
            'awsvpcConfiguration': {
                'Subnets': subnet_ids_list,
                'AssignPublicIp': 'ENABLED',
                'SecurityGroups': security_grp_list
            }
        }
    }
}

print("Connecting the rule to the ECS task as a target...")
create_tgt_resp = events_client.put_targets(Rule=Rule_Name, Targets=[ecs_target_config])
print(create_tgt_resp)

# for a in events_client.list_targets_by_rule(Rule=Rule_Name)['Targets']:
#     print(a)
# print()

# for k, v in events_client.list_targets_by_rule(Rule=Rule_Name).items():
#     print(f"{k}\n{v}")
