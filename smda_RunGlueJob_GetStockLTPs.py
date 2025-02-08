from smda_libraries import *
job_start_time = datetime.now()

glue_client = get_glue_client()
s3_client = get_s3_client()

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

# df_all_sectors = df_all_sectors[df_all_sectors['Sector'].isin(['Photographic Products'])]
df_all_sectors = df_all_sectors.sort_values(by=['Stocks'], ascending=[True]).reset_index()
df_all_sectors['n_series'] = df_all_sectors.index // 10 + 1
# print(df_all_sectors)

# df_all_sectors = df_all_sectors[df_all_sectors['Sector'].isin(['Finance'])]
# df_all_sectors = df_all_sectors[df_all_sectors['Sector'].isin(['Telecom', 'Infrastructure'])]
# df_all_sectors = df_all_sectors[df_all_sectors['Stocks'] < 100].reset_index()
# df_all_sectors = df_all_sectors.head(6)
# df_all_sectors = df_all_sectors[df_all_sectors['n_series'].isin([1, 2])]

print(df_all_sectors[['Sector', 'Stocks', 'n_series']])

jobs_running = []
for line in df_all_sectors['n_series'].unique():
    job_runs_list = []
    df = df_all_sectors[df_all_sectors['n_series'] == line]
    for index, row in df.iterrows():
        Sector = row['Sector']; job_runs_dict = {}
        start_glue_job_resp = glue_client.start_job_run(JobName='smda-get-stocks-ltps',
                                                        Arguments={'--Sector': Sector},
                                                        Timeout=20,
                                                        MaxCapacity=0.0625,
                                                        ExecutionClass='STANDARD')
        # print(f"{Sector} : {start_glue_job_resp['JobRunId']}")
        job_runs_dict['Sector'] = Sector; job_runs_dict['JobRunId'] = start_glue_job_resp['JobRunId']
        print(job_runs_dict)
        job_runs_list.append(job_runs_dict)

    # job_runs_list = [{'Sector': 'Finance', 'JobRunId': 'jr_55a614a8068eed063463ee06a95ddd3985689cc5a0a3a9a220c8a41c45312ed4'}]
    # print(job_runs_list)
    # running = True
    # while running:
    #     print("------")
    #     jobs_running2 = []
    #     for i in job_runs_list:
    #         get_job_runs_resp = glue_client.get_job_run(JobName='smda-get-stocks-ltps', RunId=i['JobRunId'])
    #         i['Status'] = get_job_runs_resp['JobRun']['JobRunState']
    #         jobs_running2.append(i)
    #         df_jobs_running = pd.DataFrame(jobs_running2)[['Sector', 'Status']]
    #         print(df_jobs_running[df_jobs_running['Status'] == 'RUNNING']);print()
    #         print(df_jobs_running[df_jobs_running['Status'] != 'RUNNING'])
    #     if len(jobs_running2) > 0:
    #         time.sleep(5)
    #     else:
    #         running = False
