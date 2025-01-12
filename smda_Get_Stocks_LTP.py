import pandas as pd

from smda_libraries import *
job_start_time = datetime.now()

all_sectors_s3_key_latest = f"s3://{aws_s3_bucket}/data/all_sectors/latest/all_sectors.csv"
df_all_sectors = pd.read_csv(all_sectors_s3_key_latest, storage_options={"key": root_user_access_key, "secret": root_user_sceret_key})
df_all_sectors = df_all_sectors[df_all_sectors['Sector'] == 'Banks']
print(df_all_sectors)

s3_client = aws_client()
# create a dataframe with all the stocks and their url's
for index,row in df_all_sectors.iterrows():
    Sector_url = row.loc['Sector_url']
    Sector_url_response = requests.get(Sector_url)
    Sector_url_html_page = BeautifulSoup(Sector_url_response.text, 'html.parser')
    data = Sector_url_html_page.find('script', id="__NEXT_DATA__", type="application/json")
    json_val = json.loads(data.text)
    stocks_list = []
    for i in json_val['props']['pageProps']['data']['marketMapData']:
        for j in i['data']:
            stocks_list.append(j)
            j['sector1'] = row.loc['Sector']

    df_stocks_list = pd.DataFrame(stocks_list)
    df_stocks_list = df_stocks_list[['sector1','name','sector','url']]
    df_stocks_list.columns = ['sector', 'name', 'industry', 'url']
    df_stocks_list['industry'] = df_stocks_list['industry'].str.replace(" Sector","")
    # df_stocks_list = df_stocks_list[df_stocks_list['name'] == 'ICICI Bank']
    df_stocks_list = df_stocks_list[df_stocks_list['name'].isin(['ICICI Bank', 'HDFC Bank'])]
    # print(df_stocks_list)

stock_ltp_list = []
for index, row in df_stocks_list.iterrows():
    stock_ltp_dict = {}
    stock_url = row.loc['url']
    stock_url_response = requests.get(stock_url)
    stock_url_html_page = BeautifulSoup(stock_url_response.text, 'html.parser')

    stocks_html_file_key = f"data/stocks_html_files/{row.loc['name'].replace(" ", "_")}.html"
    html_io_buffer = io.BytesIO(str(stock_url_html_page).encode('utf-8'))
    # s3_client.upload_fileobj(buffer=html_io_buffer, bucket_name=aws_s3_bucket, file_key=stocks_html_file_key)
    s3_client.put_object(Body=html_io_buffer, Bucket=aws_s3_bucket, Key=stocks_html_file_key)

#     stock_ltp_dict['Sector'] = row.loc['sector']
#     stock_ltp_dict['Industry'] = row.loc['industry']
#     stock_ltp_dict['stock_name'] = row.loc['name']
#     for ltp_parent_tag in stock_url_html_page.findAll('div', class_="inindi_price"):
#         # get Last traded price (ltp) of the stock
#         for stock_ltp_tag in ltp_parent_tag.findAll('div', class_=lambda x: x and "inprice1 " in x):
#             if 'nse' in stock_ltp_tag['id'] or 'bse' in stock_ltp_tag['id']:
#                 stock_ltp_dict[stock_ltp_tag['id']] = stock_ltp_tag.text
#
#         # get price change and percentage change values of ltp
#         for stock_pricechng_tag in ltp_parent_tag.findAll('div', class_=lambda x: x and "pricupdn" in x):
#             if 'nsechange' in stock_pricechng_tag['class'] or 'bsechange' in stock_pricechng_tag['class']:
#                 stock_ltp_dict[stock_pricechng_tag['class'][1]] = stock_pricechng_tag.text
#     stock_ltp_list.append(stock_ltp_dict)
#     # print(stock_ltp_dict)
#
# df_stocks_ltp = pd.DataFrame(stock_ltp_list)
# df_stocks_ltp['nse_change'] = df_stocks_ltp['nsechange'].str.split("(").str[0]
# df_stocks_ltp['nse_%change'] = df_stocks_ltp['nsechange'].str.split("(").str[1].str.replace("%)","")
# df_stocks_ltp['bse_change'] = df_stocks_ltp['bsechange'].str.split("(").str[0]
# df_stocks_ltp['bse_%change'] = df_stocks_ltp['bsechange'].str.split("(").str[1].str.replace("%)","")
# df_stocks_ltp = df_stocks_ltp[['Sector', 'Industry', 'stock_name', 'nsecp', 'nse_change', 'nse_%change', 'bsecp', 'bse_change', 'bse_%change']]
# df_stocks_ltp.columns = ['Sector', 'Industry', 'stock_name', 'nse_ltp', 'nse_change', 'nse_%change', 'bse_ltp', 'bse_change', 'bse_%change']
# # print(df_stocks_ltp.columns)
# print(df_stocks_ltp)

    # with open(f'sample_files/{row.loc['name'].replace(" ","_")}.html', 'w', encoding="utf-8") as file_obj:
    #     file_obj.write(stock_url_html_page.prettify())

    # for a in stock_url_html_page.findAll('li'):
    #     for b in a.findAll('h3', class_="all_title_inner com_brdb"):
    #         # get List of Indices in which the Stock is listed in
    #         if b.text == "Included In":
    #             benchmarks = [i.text for i in a.findAll("span")]
    #             benchmarks_status = [i.text for i in a.findAll("p")]
    #             print(dict(zip(benchmarks, benchmarks_status)))
    #
    #         # get Security id's of the Stock
    #         if b.text == "Details":
    #             s_keys = [i.text for i in a.findAll("span")]
    #             s_values = [i.text for i in a.findAll("p")]
    #             print(dict(zip(s_keys, s_values)))




print(f"\n{str('--')*10}\n{job_start_time} | {datetime.now()} | {datetime.now() - job_start_time}")

