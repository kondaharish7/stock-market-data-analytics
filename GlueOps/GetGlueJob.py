from smda_libraries import *
import datetime
# job_start_time = datetime.now()

glue_client = get_glue_client()

# response = glue_client.get_job(JobName='smda-get-stocks-htmls')
# for k,v in response['Job'].items():
#     print(f"{k}\n\t{v}")

# print()
# for k,v in response['ResponseMetadata'].items():
#     print(f"{k}\n\t{v}")

response = glue_client.create_job(Name='smda-get-stocks-htmls-power-sector',
                                    Role='arn:aws:iam::621799566105:role/Role-S3AccessForGlue',
                                    ExecutionProperty={'MaxConcurrentRuns': 1},
                                    Command={'Name': 'pythonshell', 'ScriptLocation': 's3://stock-market-data-analytics/py_code/smda_get_stock_html_pages.py', 'PythonVersion': '3.9'},
                                    DefaultArguments={'--Sector':'Power', '--extra-py-files': 's3://python-libraries1/pythonlibraries/beautifulsoup4-4.12.2-py3-none-any.whl,s3://stock-market-data-analytics/py_code/smda_libraries.py,s3://stock-market-data-analytics/py_code/smda_contexts.py,s3://stock-market-data-analytics/py_code/smda_AWSOps.py', '--enable-job-insights': 'false', '--enable-observability-metrics': 'false', '--enable-glue-datacatalog': 'true', 'library-set': 'analytics', '--job-language': 'python', '--TempDir': 's3://stock-market-data-analytics/temp_path/'},
                                    MaxCapacity=0.0625,
                                    GlueVersion='3.0',
                                    ExecutionClass='STANDARD'
)