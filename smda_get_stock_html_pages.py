from smda_libraries import *
job_start_time = datetime.now()

s3_client = get_s3_client()

def get_html_file(stock_url, stock_name) -> None:
    print(f"Saving html file for {stock_name}, ", end="");log_time = datetime.now()
    stock_url_response = requests.get(stock_url, timeout=2)
    stock_url_html_page = BeautifulSoup(stock_url_response.text, 'html.parser')
    stocks_html_file_key = "data/stocks_html_files/{}/{}.html".format(Sector, stock_name.replace(" ", "_"))
    html_io_buffer = io.BytesIO(str(stock_url_html_page).encode('utf-8'))
    s3_client.put_object(Body=html_io_buffer, Bucket=aws_s3_bucket, Key=stocks_html_file_key)
    print(f"elapsed: {datetime.now() - log_time}")

if __name__ == '__main__':
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

    df_all_sectors = df_all_sectors[df_all_sectors['Sector'] == 'Banks']

    # create a dataframe with all the stocks and their url's
    for index, row in df_all_sectors.iterrows():
        Sector = row.loc['Sector'].replace(" ", "_")
        print(Sector)

        sector_stocks_list_s3_key = "data/stocks_list/{}_stocks_list.csv".format(Sector)
        s3_file_resp = s3_client.get_object(Bucket=aws_s3_bucket, Key=sector_stocks_list_s3_key)
        # print(s3_file_resp)

        # Create an in-memory buffer and write the CSV data into it
        sector_stocks_list_io_buffer = io.StringIO(s3_file_resp['Body'].read().decode('utf-8'))
        df_stocks_list = pd.read_csv(filepath_or_buffer=sector_stocks_list_io_buffer, sep=',', names=['Sector', 'industry', 'stock_name', 'url'], header=1, encoding='UTF-8')
        # df_stocks_list = df_stocks_list[df_stocks_list['stock_name'] == 'HDFC Bank']

        failed_stocks_list = []
        for index, row in df_stocks_list.iterrows():
            try:
                stock_url = row.loc['url']; stock_name = row.loc['stock_name']
                get_html_file(stock_url=stock_url, stock_name=stock_name)
            except Exception as get_html_err:
                print(f"Timed Out.")
                failed_stocks_list.append([stock_url, stock_name])
            else:
                pass

        if len(failed_stocks_list) > 0:
            print(f"Stocks failed:\ncount: {len(failed_stocks_list)}\nlist: {failed_stocks_list}")
        while len(failed_stocks_list) > 0:
            print(f"\nRe-pulling the html files for the failed stocks.")
            failed_stocks_list1 = failed_stocks_list; failed_stocks_list = []
            for stock_details in failed_stocks_list1:
                try:
                    stock_url = stock_details[0];stock_name = stock_details[1]
                    get_html_file(stock_url=stock_url, stock_name=stock_name)
                except Exception as get_html_err:
                    print(f"Timed Out.")
                    failed_stocks_list.append([stock_url, stock_name])
            if len(failed_stocks_list) > 0:
                print(f"Stocks failed during re-pull\ncount: {len(failed_stocks_list)}\nlist: {failed_stocks_list}")

    print(f"\n{str('--')*10}\n{job_start_time} | {datetime.now()} | {datetime.now() - job_start_time}")

