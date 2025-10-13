from smda_libraries import *
import datetime
# job_start_time = datetime.now()

ecs_client = get_ecs_client()
smda_ecs_cluster = "ecs-cluster-smda"
smda_launch_type = "FARGATE"
smda_container_name = "cntnr-smda"
smda_task_definition_arn = "arn:aws:ecs:us-east-1:621799566105:task-definition/td-smda:3"
subnet_ids_list = ['subnet-f61fe2d7','subnet-1c2cdf43','subnet-038beb7d314647592']
security_grp_list = ["sg-bc1c2092"]

params_list = ['Containers & Packaging','Diamond  &  Jewellery','Electricals','Consumer Durables','ETF','Logistics','Hospitality','Media & Entertainment','Plastic Products']

for sector_value in params_list:
    task_overrides = {
        'containerOverrides': [
            {'name': smda_container_name, 'environment': [{'name': 'Sector', 'value': sector_value}]}
        ]
    }

    response = ecs_client.run_task(
        cluster=smda_ecs_cluster,
        launchType= smda_launch_type,
        taskDefinition= smda_task_definition_arn,
        count=1,
        overrides=task_overrides,
        networkConfiguration={'awsvpcConfiguration': {'subnets': subnet_ids_list, 'assignPublicIp': 'ENABLED', 'securityGroups': security_grp_list,}},
        platformVersion='LATEST'
    )

    print(f"Sector: {sector_value}, Task Arn: {response['tasks'][0]['taskArn']}")
