from smda_libraries import *
# job_start_time = datetime.now()

events_client = get_aws_service_client(aws_service='events')

# --- Configuration --- #
Rule_Name = 'rule-smda-ecs-3'

for a in events_client.list_targets_by_rule(Rule=Rule_Name)['Targets']:
    print(a)
print()

# for k, v in events_client.list_targets_by_rule(Rule=Rule_Name).items():
#     print(f"{k}\n{v}")
