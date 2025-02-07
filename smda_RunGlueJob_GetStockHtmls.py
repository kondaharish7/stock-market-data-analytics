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

# df_all_sectors = df_all_sectors[df_all_sectors['Sector'].isin(['Finance', 'Metals & Mining','Power'])]
# df_all_sectors = df_all_sectors[df_all_sectors['Sector'].isin(['Telecom', 'Infrastructure'])]
df_all_sectors = df_all_sectors[df_all_sectors['Stocks'] < 100].reset_index()
# print(df_all_sectors)
df_all_sectors['n_series'] = df_all_sectors.index // 3 + 1
df_all_sectors = df_all_sectors[df_all_sectors['n_series'].isin([1,2])]
print(df_all_sectors[['Sector', 'n_series']])
# print(df_all_sectors['n_series'].unique())

for line in df_all_sectors['n_series'].unique():
    print(line)
    df = df_all_sectors[df_all_sectors['n_series'] == line]
    job_run_ids = {}
    for index, row in df.iterrows():
        Sector = row['Sector']
        start_glue_job_resp = glue_client.start_job_run(JobName='smda-get-stocks-htmls',
                                                        Arguments={'--Sector': Sector},
                                                        Timeout=20,
                                                        MaxCapacity=0.0625,
                                                        ExecutionClass='STANDARD')
        print(f"{Sector} : {start_glue_job_resp['JobRunId']}")
        job_run_ids[Sector] = start_glue_job_resp['JobRunId']
        # job_run_ids = {'Telecom':'jr_bf3683c60ae341704046491e196639cf6776e11276d62c6f8003946fb1c167fe', 'Infrastructure':'jr_32f5835eafc61b2eef293633251d95012eb4cdd5c014eeae8d2c96a0a670f796'}
        print(job_run_ids)

    running = True
    while running:
        print("------")
        jobs_running = []
        for Sector, job_run_id in job_run_ids.items():
            get_job_runs_resp = glue_client.get_job_run(JobName='smda-get-stocks-htmls', RunId=job_run_id)
            if get_job_runs_resp['JobRun']['JobRunState'] == 'RUNNING':
                print(f"{Sector}: {get_job_runs_resp['JobRun']['JobRunState']}")
                jobs_running.append(Sector)
        if len(jobs_running) > 0:
             time.sleep(5)
        else:
            running = False
