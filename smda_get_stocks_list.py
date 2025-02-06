from smda_libraries import *
job_start_time = datetime.now()

s3_client = get_s3_client()

base_url = "https://www.moneycontrol.com/india/stockpricequote/"
all_sectors_s3_key_latest = f"data/all_sectors/latest/all_sectors.csv"
s3_file_resp = s3_client.get_object(Bucket=aws_s3_bucket, Key=all_sectors_s3_key_latest)
csv_data = s3_file_resp['Body'].read().decode('utf-8')

# Create an in-memory buffer and write the CSV data into it
sectors_list_io_buffer = io.StringIO(csv_data)
df_all_sectors = pd.read_csv(filepath_or_buffer=sectors_list_io_buffer,
                             sep=',',
                             names=['Sector','Market_cap(Cr)','PE_Ratio','Industries','Stocks','Sector_url'],
                             header=1,
                             encoding='UTF-8'
                             )

# Create a dataframe with all the stocks and their url's
empty_stocks_list = []
for index, row in df_all_sectors.iterrows():
    print(f"Pulling stock lists for the Sector: {row.loc['Sector']},", end="");log_time = datetime.now()
    try:
        Sector_url = row.loc['Sector_url']
        Sector_url_response = requests.get(Sector_url)
        Sector_url_html_page = BeautifulSoup(Sector_url_response.text, 'html.parser')

        data = Sector_url_html_page.find('script', id="__NEXT_DATA__", type="application/json")
        json_val = json.loads(data.text)
        stocks_list = []

        if len(json_val['props']['pageProps']['data']['allStocks']) > 0:
            for a in json_val['props']['pageProps']['data']['allStocks']:
                if 'slug' in a.keys():
                    stocks_list.append([row.loc['Sector'], a['slug'].split("/")[0], a['stockName'], base_url+a['slug']])

            df_stocks_list = pd.DataFrame(stocks_list)
            df_stocks_list.columns = ['sector', 'industry', 'stock_name', 'url']
            df_stocks_list = df_stocks_list.sort_values(by=['industry'], ascending=[True])

            # Create an in-memory buffer and write the CSV data into it
            stocks_list_io_buffer = io.StringIO()
            df_stocks_list.to_csv(stocks_list_io_buffer, index=False)
            stocks_list_io_buffer.seek(0)

            # Get the CSV data as bytes and upload to S3
            stocks_list_io_buffer_bytes = stocks_list_io_buffer.getvalue().encode('utf-8')
            stocks_list_file_key = "data/stocks_list/{}_stocks_list.csv".format(row.loc['Sector'].replace(" ","_"))
            s3_client.put_object(Body=stocks_list_io_buffer_bytes, Bucket=aws_s3_bucket, Key=stocks_list_file_key)
        else:
            empty_stocks_list.append(row.loc['Sector'])
            print(f", No data found for the Sector,")
    except Exception as stocks_pull_err:
        print(f"failed, elapsed: {datetime.now() - log_time}")
        print(traceback.format_exc())
    else:
        print(f" elapsed: {datetime.now() - log_time}")

if len(empty_stocks_list) > 0:
    print(f"No data for stocks found for the below Sectors, \n{empty_stocks_list}")

print(f"\n{str('--')*10}\n{job_start_time} | {datetime.now()} | {datetime.now() - job_start_time}")

"""
Using Access keys and Secret keys

all_sectors_s3_key_latest = f"s3://{aws_s3_bucket}/data/all_sectors/latest/all_sectors.csv"
df_all_sectors = pd.read_csv(all_sectors_s3_key_latest, storage_options={"key": root_user_access_key, "secret": root_user_sceret_key})
df_all_sectors = df_all_sectors[df_all_sectors['Sector'].isin(['FMCG'])]#'Banks','Insurance','Finance','Software & IT Services', 'FMCG'
"""

"""
# with open(f'sample_files/{row.loc['Sector'].replace(" ","_")}.html', 'w', encoding="utf-8") as file_obj:
#     file_obj.write(Sector_url_html_page.prettify())
"""