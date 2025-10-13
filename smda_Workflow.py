import sys

from smda_libraries import *
from smda_get_stocks_list import *
from smda_get_stock_html_pages import *
from smda_Get_Stocks_LTP import *
job_start_time = datetime.now()

try:
    from awsglue.utils import getResolvedOptions
    args = getResolvedOptions(sys.argv, ['Sector'])
    Sector = args['Sector']
except Exception as glue_lib_err:
    try:
        Sector = sys.argv[1]
    except Exception as args_err:
        Sector = 'Containers & Packaging'

if __name__ == '__main__':
    # Sector = 'Photographic Products'
    get_stocks_list(Sector = Sector)
    get_stocks_html_files(Sector = Sector)
    get_stock_ltp(Sector = Sector)

    print(f"\n{str('--') * 10}\n{job_start_time} | {datetime.now()} | {datetime.now() - job_start_time}")

