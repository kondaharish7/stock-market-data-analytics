from smda_libraries import *
job_start_time = datetime.now()

aws_session = boto3.Session(profile_name='smda-etl')
s3_client = get_s3_client(aws_session = aws_session)

base_url = f"https://www.moneycontrol.com/markets/sector-analysis/"
base_url_response = requests.get(base_url)
base_url_html_page = BeautifulSoup(base_url_response.text, 'html.parser')

# print(base_url_html_page.prettify())

sectors_info_list = []
for a in base_url_html_page.findAll('a', class_="CardWeb_grayBoxStrip__4UAIy"):
    try:
        sector_url = f"{a['href']}"
        sector = a.find('span', class_="CardWeb_sectors_name__bryNo").text
        market_cap = a.find('span', class_="CardWeb_value__NLX7e CardWeb_font14____K3u").text
        PE_Ratio = a.find('span', class_="CardWeb_value__NLX7e CardWeb_mt5__d9MW6 CardWeb_font14____K3u").text

        for b in a.findAll('span', class_="CardWeb_stocksNum__7tKf8"):
            if 'industries' in str(b.text).lower():
                Industries = str(b.text).replace("Industries : ","")
            if 'stocks' in str(b.text).lower():
                Stocks = str(b.text).replace("Stocks : ","")

        # print(f"{sector}, {market_cap}, {PE_Ratio}, {Industries}, {Stocks}")
        sectors_info_list.append([sector, market_cap, PE_Ratio, Industries, Stocks, sector_url])
    except Exception as err:
        print(err)
    # break #to limit to one loop

df_sectors = pd.DataFrame(sectors_info_list, columns=['Sector', 'Market_cap(Cr)', 'PE_Ratio', 'Industries', 'Stocks', 'Sector_url'])
print(df_sectors)

# Create an in-memory buffer and write the CSV data into it
sectors_info_list_io_buffer = io.StringIO()
df_sectors.to_csv(sectors_info_list_io_buffer, index=False)
sectors_info_list_io_buffer.seek(0)

# Get the CSV data as bytes
sectors_info_list_io_buffer_bytes = sectors_info_list_io_buffer.getvalue().encode('utf-8')

# upload the bytes data to S3
all_sectors_s3_key = f"data/all_sectors/hist/date={job_start_time.date()}/all_sectors_{job_start_time.date()}.csv"
all_sectors_s3_key_latest = f"data/all_sectors/latest/all_sectors.csv"

s3_client.put_object(Body=sectors_info_list_io_buffer_bytes, Bucket=aws_s3_bucket, Key=all_sectors_s3_key)
s3_client.put_object(Body=sectors_info_list_io_buffer_bytes, Bucket=aws_s3_bucket, Key=all_sectors_s3_key_latest)

# df_sectors.to_csv(all_sectors_s3_key, index=False, storage_options={"key": root_user_access_key, "secret": root_user_sceret_key})
# df_sectors.to_csv(all_sectors_s3_key_latest, index=False, storage_options={"key": root_user_access_key, "secret": root_user_sceret_key})

print(f"\n{str('--')*10}\n{job_start_time} | {datetime.now()} | {datetime.now() - job_start_time}")
