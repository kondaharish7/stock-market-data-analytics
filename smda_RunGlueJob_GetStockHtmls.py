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

# df_all_sectors = df_all_sectors[df_all_sectors['Sector'].isin(['Finance','Metals & Mining','Power'])]
df_all_sectors = df_all_sectors[df_all_sectors['Sector'].isin(['Power'])]
# df_all_sectors = df_all_sectors.head(3)
print(df_all_sectors)

for index,row in df_all_sectors.iterrows():
    Sector = row['Sector']
    start_glue_job_resp = glue_client.start_job_run(
                                                    JobName='smda-get-stocks-htmls',
                                                    Arguments={'--Sector': Sector,
                                                    Timeout=20,
                                                    MaxCapacity=0.0625,
                                                    ExecutionClass='STANDARD'
                                                    )
    print(f"{Sector} : {start_glue_job_resp['JobRunId']}")

