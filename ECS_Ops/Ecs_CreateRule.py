from smda_libraries import *
# job_start_time = datetime.now()

events_client = get_aws_service_client(aws_service='events')

# --- Configuration --- #
smda_ecs_cluster = "ecs-cluster-smda"
Rule_Name = 'rule-smda-glue-daily-jobs'
CRON_EXPRESSION = 'cron(0/5 * * * ? *)'  # For example: 10:00 AM every day

print(f"Creating EventBridge rule '{Rule_Name}' with schedule '{CRON_EXPRESSION}'...")
response_rule = events_client.put_rule(
    Name=Rule_Name,
    ScheduleExpression=CRON_EXPRESSION,
    State='ENABLED',
    Description='Rule to schedule the Aws Glue jobs for SMDA project.'
)

rule_arn = response_rule['RuleArn']
print(f"Rule created with ARN: {rule_arn}")
