import pandas as pd

from smda_libraries import *
job_start_time = datetime.now()

all_sectors_s3_key_latest = f"s3://{aws_s3_bucket}/data/all_sectors/latest/all_sectors.csv"
df_all_sectors = pd.read_csv(all_sectors_s3_key_latest, storage_options={"key": root_user_access_key, "secret": root_user_sceret_key})
df_all_sectors = df_all_sectors[df_all_sectors['Sector'] == 'Banks']
print(df_all_sectors)

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

    df_stocks_list = pd.DataFrame(stocks_list)
    df_stocks_list = df_stocks_list[df_stocks_list['name'] == 'ICICI Bank']
    # print(df_stocks_list)

for index,row in df_stocks_list.iterrows():
    security_url = row.loc['url']
    security_url_response = requests.get(security_url)
    security_url_html_page = BeautifulSoup(security_url_response.text, 'html.parser')
    # print(security_url_html_page.prettify())
    for a in security_url_html_page.findAll('li'):
        for b in a.findAll('h3', class_="all_title_inner com_brdb"):
            # print(b)
            if b.text == "Included In":
                benchmarks = [i.text for i in a.findAll("span")]; print(benchmarks)
                benchmarks_status = [i.text for i in a.findAll("p")]; print(benchmarks_status)
                print(dict(zip(benchmarks, benchmarks_status)))


    # span_tags , p_tags = [], []
    # for tags in security_url_html_page.findAll('ul', class_="comdetl"):
    #     for sub_tags in tags.findAll('li', class_="clearfix"):
    #         for a in sub_tags.findAll('span'):
    #             span_tags.append(a.text)
    #         for a in sub_tags.findAll('p'):
    #             p_tags.append(a.text)

    # for tags in security_url_html_page.findAll('ul', class_="comdetl2"):
    #     for sub_tags in tags.findAll('li', class_="clearfix"):
    #         for a in sub_tags.findAll('span'):
    #             span_tags.append(a.text)
    #         for a in sub_tags.findAll('p'):
    #             p_tags.append(a.text)

    # print(f"{span_tags}\n{p_tags}")
    # for k,v in dict(zip(span_tags, p_tags)).items():
    #     print(f"{k}\n\t{v}")

    # with open('file_op.html', 'w', encoding="utf-8") as file_obj:
    #     file_obj.write(security_url_html_page.prettify())


print(f"\n{str('--')*10}\n{job_start_time} | {datetime.now()} | {datetime.now() - job_start_time}")

