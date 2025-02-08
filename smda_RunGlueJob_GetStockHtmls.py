from smda_libraries import *
job_start_time = datetime.now()

try:
    from awsglue.utils import getResolvedOptions
except:
    print("Unable to import aws glue libraries")

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

df_all_sectors = df_all_sectors.sort_values(by=['Stocks'], ascending=[True]).reset_index()
df_all_sectors['n_series'] = df_all_sectors.index // 10 + 1
# print(df_all_sectors)

# df_all_sectors = df_all_sectors[df_all_sectors['Sector'].isin(['Finance', 'Metals & Mining','Power'])]
# df_all_sectors = df_all_sectors[df_all_sectors['Sector'].isin(['Telecom', 'Infrastructure'])]
# df_all_sectors = df_all_sectors[df_all_sectors['Stocks'] < 100].reset_index()
# df_all_sectors = df_all_sectors.head(6)
# df_all_sectors = df_all_sectors[df_all_sectors['n_series'].isin([1, 2])]

print(df_all_sectors[['Sector', 'Stocks', 'n_series']])

job_run_args = {'--Sector': Sector}
jobs_running = []
for line in df_all_sectors['n_series'].unique():
    job_runs_list = []
    df = df_all_sectors[df_all_sectors['n_series'] == line]
    for index, row in df.iterrows():
        Sector = row['Sector']; job_runs_dict = {}
        start_glue_job_resp = glue_client.start_job_run(JobName='smda-get-stocks-htmls',
                                                        Arguments=job_run_args,
                                                        Timeout=50,
                                                        MaxCapacity=0.0625,
                                                        ExecutionClass='STANDARD'
                                                        )
        # print(f"{Sector} : {start_glue_job_resp['JobRunId']}")
        job_runs_dict['Sector'] = Sector; job_runs_dict['JobRunId'] = start_glue_job_resp['JobRunId']
        print(job_runs_dict)
        job_runs_list.append(job_runs_dict)

    # # job_runs_list = [{'Sector': 'Software & IT Services', 'JobRunId': 'jr_c62a9a1dcb01b8a9fb6a594abddd801edb9600e4851d875b9cc3a8a4abab2668'}, {'Sector': 'Finance', 'JobRunId': 'jr_635b7954bb77d7808a2af6e584dd1aeeba5475fa95eab4f04776616faf32be5b'}, {'Sector': 'Automobile & Ancillaries', 'JobRunId': 'jr_c04a7c87dd9f38b250cf1555abb6d929417be6c2829f484c6b4f4cf8f9c06926'}]
    # print(job_runs_list)
    # running = True
    # while running:
    #     print("------")
    #     jobs_running2 = []
    #     for i in job_runs_list:
    #         get_job_runs_resp = glue_client.get_job_run(JobName='smda-get-stocks-htmls', RunId=i['JobRunId'])
    #         # if get_job_runs_resp['JobRun']['JobRunState'] == 'RUNNING':
    #         i['Status'] = get_job_runs_resp['JobRun']['JobRunState']
    #         jobs_running.append(i); jobs_running2.append(i)
    #         df_jobs_running = pd.DataFrame(jobs_running)[['Sector', 'Status']]
    #         print(df_jobs_running[df_jobs_running['Status'] == 'RUNNING']);print()
    #         print(df_jobs_running[df_jobs_running['Status'] != 'RUNNING'])
    #     if len(jobs_running2) > 0:
    #         time.sleep(5)
    #     else:
    #         running = False
