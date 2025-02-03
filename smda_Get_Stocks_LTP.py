from smda_libraries import *
job_start_time = datetime.now()

aws_session = boto3.Session(profile_name='smda-etl')
s3_client = get_s3_client(aws_session = aws_session)

def get_stock_ltp(Sector, stock_name, Industry) -> dict:
    stock_html_file_s3_key = f"data/stocks_html_files/{Sector}/{stock_name}.html"
    html_file_resp = s3_client.get_object(Bucket=aws_s3_bucket, Key=stock_html_file_s3_key)
    html_content = html_file_resp['Body'].read().decode('utf-8')
    stock_html_page = BeautifulSoup(html_content, 'html.parser')

    stock_ltp_dict['Sector'] = Sector; stock_ltp_dict['stock_name'] = stock_name; stock_ltp_dict['Industry'] = Industry
    for ltp_parent_tag in stock_html_page.findAll('div', class_="inindi_price"):
        # get Last traded price (ltp) of the stock
        for stock_ltp_tag in ltp_parent_tag.findAll('div', class_=lambda x: x and "inprice1 " in x):
            if 'nse' in stock_ltp_tag['id'] or 'bse' in stock_ltp_tag['id']:
                stock_ltp_dict[stock_ltp_tag['id']] = stock_ltp_tag.text

        # get price change and percentage change values of ltp
        for stock_pricechng_tag in ltp_parent_tag.findAll('div', class_=lambda x: x and "pricupdn" in x):
            if 'nsechange' in stock_pricechng_tag['class'] or 'bsechange' in stock_pricechng_tag['class']:
                stock_ltp_dict[stock_pricechng_tag['class'][1]] = stock_pricechng_tag.text
    return stock_ltp_dict

def save_df_to_s3(stock_ltp_list) -> None:
    print(f"Saving the file for {Sector} to S3")
    df_stocks_ltp = pd.DataFrame(stock_ltp_list)
    df_stocks_ltp['nse_change'] = df_stocks_ltp['nsechange'].str.split("(").str[0]
    df_stocks_ltp['nse_%change'] = df_stocks_ltp['nsechange'].str.split("(").str[1].str.replace("%)", "")
    df_stocks_ltp['bse_change'] = df_stocks_ltp['bsechange'].str.split("(").str[0]
    df_stocks_ltp['bse_%change'] = df_stocks_ltp['bsechange'].str.split("(").str[1].str.replace("%)", "")
    df_stocks_ltp = df_stocks_ltp[['Sector', 'Industry', 'stock_name', 'nsecp', 'nse_change', 'nse_%change', 'bsecp', 'bse_change', 'bse_%change']]
    df_stocks_ltp.columns = ['Sector', 'Industry', 'stock_name', 'nse_ltp', 'nse_change', 'nse_%change', 'bse_ltp', 'bse_change', 'bse_%change']
    # print(df_stocks_ltp.groupby(['Sector']).aggregate({'Industry':'count'}));print()
    # print(df_stocks_ltp.groupby(['Sector','Industry']).aggregate({'stock_name': 'count'}))

    # Create an in-memory buffer and write the CSV data into it
    stocks_ltp_io_buffer = io.StringIO()
    df_stocks_ltp.to_csv(stocks_ltp_io_buffer, index=False)
    stocks_ltp_io_buffer.seek(0)
    stocks_ltp_io_buffer_bytes = stocks_ltp_io_buffer.getvalue().encode('utf-8')

    stocks_ltp_s3_key = f"data/stocks_ltp/hist/sector={Sector}/date={job_start_time.date()}/{Sector}_ltps.csv"
    stocks_ltp_s3_key_latest = f"data/stocks_ltp/latest/sector={Sector}/{Sector}_ltps.csv"

    s3_client.put_object(Body=stocks_ltp_io_buffer_bytes, Bucket=aws_s3_bucket, Key=stocks_ltp_s3_key)
    s3_client.put_object(Body=stocks_ltp_io_buffer_bytes, Bucket=aws_s3_bucket, Key=stocks_ltp_s3_key_latest)
    print(f"elapsed, {datetime.now() - log_time}")

if __name__ == '__main__':
    all_sectors_s3_key_latest = f"data/all_sectors/latest/all_sectors.csv"
    s3_file_resp = s3_client.get_object(Bucket=aws_s3_bucket, Key=all_sectors_s3_key_latest)

    # Create an in-memory buffer and write the CSV data into it
    sectors_list_io_buffer = io.StringIO(s3_file_resp['Body'].read().decode('utf-8'))
    df_all_sectors = pd.read_csv(filepath_or_buffer=sectors_list_io_buffer, sep=',', names=['Sector', 'Market_cap(Cr)', 'PE_Ratio', 'Industries', 'Stocks', 'Sector_url'], header=1, encoding='UTF-8')
    df_all_sectors = df_all_sectors[df_all_sectors['Sector'] == 'Software & IT Services']

    stock_ltp_list = []; failed_stocks_list = []
    for index,row in df_all_sectors.iterrows():
        Sector = row.loc['Sector'].replace(" ","_")
        sector_stocks_list_s3_key = f"data/stocks_list/{Sector}_stocks_list.csv"
        s3_file_resp = s3_client.get_object(Bucket=aws_s3_bucket, Key=sector_stocks_list_s3_key)
        sector_stocks_list_io_buffer = io.StringIO(s3_file_resp['Body'].read().decode('utf-8'))
        df_stocks_list = pd.read_csv(filepath_or_buffer=sector_stocks_list_io_buffer, sep=',', names=['Sector', 'industry', 'stock_name', 'url'], header=1, encoding='UTF-8')
        # df_stocks_list = df_stocks_list[df_stocks_list['stock_name'] == 'Axis Bank']
        for index, row in df_stocks_list.iterrows():
            try:
                stock_ltp_dict = {}
                Industry = row.loc['industry']; stock_name = row.loc['stock_name'].replace(" ", "_")
                print(f"{str('--') * 10}\nPulling data for {stock_name}, ",end="");log_time = datetime.now()
                stock_ltp_dict = get_stock_ltp(Sector=Sector, stock_name=stock_name, Industry=Industry)
            except Exception as data_pull_err:
                if data_pull_err.response['Error']['Code'] == 'NoSuchKey':
                    print(f"Html file for {stock_name} doesn't exists in the Bucket.")
                    failed_stocks_list.append(stock_name)
                    print(f", elapsed, {datetime.now() - log_time}")
            else:
                stock_ltp_list.append(stock_ltp_dict)
                print(f"elapsed, {datetime.now() - log_time}")

    save_df_to_s3(stock_ltp_list = stock_ltp_list)


    print(f"\n{str('--')*10}\n{job_start_time} | {datetime.now()} | {datetime.now() - job_start_time}")


"""
Convert the Dataframe to csv and save it to S3 
stocks_ltp_s3_key = f"s3://{aws_s3_bucket}/data/stocks_ltp/hist/sector={Sector}/date={job_start_time.date()}/{Sector}_ltps.csv"
stocks_ltp_s3_key_latest = f"s3://{aws_s3_bucket}/data/stocks_ltp/latest/sector={Sector}/{Sector}_ltps.csv"

df_stocks_ltp.to_csv(stocks_ltp_s3_key, index=False, storage_options={"key": root_user_access_key, "secret": root_user_sceret_key})
df_stocks_ltp.to_csv(stocks_ltp_s3_key_latest, index=False, storage_options={"key": root_user_access_key, "secret": root_user_sceret_key})
"""