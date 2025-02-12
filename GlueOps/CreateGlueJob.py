from smda_libraries import *
import datetime
# job_start_time = datetime.now()

s3_client = get_s3_client(); glue_client = get_glue_client()

all_sectors_s3_key_latest = f"data/all_sectors/latest/all_sectors.csv"
s3_file_resp = s3_client.get_object(Bucket=aws_s3_bucket, Key=all_sectors_s3_key_latest)
csv_data = s3_file_resp['Body'].read().decode('utf-8')

# Create an in-memory buffer and write the CSV data into it
sectors_list_io_buffer = io.StringIO(csv_data)
df_all_sectors = pd.read_csv(filepath_or_buffer=sectors_list_io_buffer,
                             sep=',',
                             names=['Sector', 'Market_cap(Cr)', 'PE_Ratio', 'Industries', 'Stocks', 'Sector_url'],
                             header=0,
                             encoding='UTF-8'
                             )

# print(df_all_sectors)
for index,row in df_all_sectors.iterrows():
    Sector = row.loc['Sector']
    glue_job_name = "smda-workflow-sector-{}".format(Sector)
    iam_role = iam_gluejob_role
    py_script_name = "smda_get_stock_html_pages.py"
    script_location = "s3://{}/py_code/{}".format(aws_s3_bucket, py_script_name)
    extra_py_files = "s3://python-libraries1/pythonlibraries/beautifulsoup4-4.12.2-py3-none-any.whl,s3://stock-market-data-analytics/py_code/smda_libraries.py,s3://stock-market-data-analytics/py_code/smda_contexts.py,s3://stock-market-data-analytics/py_code/smda_AWSOps.py,s3://stock-market-data-analytics/py_code/smda_get_stocks_list.py, s3://stock-market-data-analytics/py_code/smda_get_stock_html_pages.py, s3://stock-market-data-analytics/py_code/smda_Get_Stocks_LTP.py"
    temp_dir = "s3://stock-market-data-analytics/temp_path/"
    response = glue_client.create_job(Name=glue_job_name,
                                        Role=iam_role,
                                        ExecutionProperty={'MaxConcurrentRuns': 1},
                                        Command={'Name': 'pythonshell', 'ScriptLocation': script_location, 'PythonVersion': '3.9'},
                                        DefaultArguments={'--Sector':Sector, '--extra-py-files': extra_py_files, '--enable-job-insights': 'false', '--enable-observability-metrics': 'false', '--enable-glue-datacatalog': 'true', 'library-set': 'analytics', '--job-language': 'python', '--TempDir': temp_dir},
                                        MaxCapacity=0.0625,
                                        GlueVersion='3.0',
                                        ExecutionClass='STANDARD'
                                    )
    break # to limit to one loop