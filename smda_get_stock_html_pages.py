import pandas as pd

from smda_libraries import *
job_start_time = datetime.now()

s3_client = get_s3_client()

def get_stocks_list(Sector) -> pd.DataFrame:
    Sector = Sector.replace(" ", "_")
    print(f"PUlling html files for {Sector} Sector.")

    sector_stocks_list_s3_key = "data/stocks_list/{}_stocks_list.csv".format(Sector)
    s3_file_resp = s3_client.get_object(Bucket=aws_s3_bucket, Key=sector_stocks_list_s3_key)

    # Create an in-memory buffer and write the CSV data into it
    sector_stocks_list_io_buffer = io.StringIO(s3_file_resp['Body'].read().decode('utf-8'))
    df_stocks_list = pd.read_csv(filepath_or_buffer=sector_stocks_list_io_buffer, sep=',', names=['Sector', 'industry', 'stock_name', 'url'], header=1, encoding='UTF-8')
    return df_stocks_list

def get_html_file(stock_url, stock_name) -> None:
    print(f"Saving html file for {stock_name}, ", end="");log_time = datetime.now()
    stock_url_response = requests.get(stock_url, timeout=2)
    stock_url_html_page = BeautifulSoup(stock_url_response.text, 'html.parser')
    stocks_html_file_key = "data/stocks_html_files/{}/{}.html".format(Sector, stock_name.replace(" ", "_"))
    html_io_buffer = io.BytesIO(str(stock_url_html_page).encode('utf-8'))
    s3_client.put_object(Body=html_io_buffer, Bucket=aws_s3_bucket, Key=stocks_html_file_key)
    print(f"elapsed: {datetime.now() - log_time}")

def get_stocks_html_files(Sector):
    # Get Stocks list dataframe
    df_stocks_list = get_stocks_list(Sector='Power')

    # Get html files from web
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

if __name__ == '__main__':

    get_stocks_html_files(Sector = 'Power')

print(f"\n{str('--')*10}\n{job_start_time} | {datetime.now()} | {datetime.now() - job_start_time}")

