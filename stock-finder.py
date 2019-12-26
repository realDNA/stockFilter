import requests
import pandas as pd
import numpy as np
import datetime

#https://www.finlab.tw/Python-%E8%B2%A1%E5%A0%B1%E7%88%AC%E8%9F%B2-1-%E7%B6%9C%E5%90%88%E6%90%8D%E7%9B%8A%E8%A1%A8/
#https://medium.com/renee0918/python%E7%88%AC%E8%9F%B2-%E5%80%8B%E8%82%A1%E6%AF%8F%E5%AD%A3%E8%B2%A1%E5%A0%B1-a83d1e21d9ca

def financial_statement(year, season, type='綜合損益彙總表'):

    if year >= 1000:
        year -= 1911

    if type == '綜合損益彙總表':
        url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb04'
    elif type == '資產負債彙總表':
        url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb05'
    elif type == '營益分析彙總表':
        url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb06'
    else:
        print('type does not match')

    r = requests.post(url, {
        'encodeURIComponent':1,
        'step':1,
        'firstin':1,
        'off':1,
        'TYPEK':'sii',
        'year':str(year),
        'season':str(season),
    })

    r.encoding = 'utf8'

    dfs = pd.read_html(r.text, header=None)

    return pd.concat(dfs[1:], axis=0, sort=False) \
        .set_index(['公司名稱']) \
        .apply(lambda s: pd.to_numeric(s, errors='ignore'))


def get_data_by_year_quarter(year, quarter):
    return financial_statement(year, quarter, type="綜合損益彙總表")


def get_lats_quater(month):
    quarter = 1 if month in [1, 2, 3] else \
        2 if month in [4, 5, 6] else \
        3 if month in [7, 8, 9] else\
        4 if month in [10, 11, 12] else 0

    last_quarter = quarter-1
    last_quarter = 4 if last_quarter == 0 else last_quarter

    return last_quarter


def remove_bad_company_by_eps(companys_key, companys_info, how_many_quarters=20):
    collect_result = {}
    for key in companys_key:
        eps_history = companys_info[key]["eps"][0:how_many_quarters]

        # if negative eps smaller >= half, then remove
        count = 0
        for number in eps_history:
            if number < 0:
                count += 1
        if count > how_many_quarters*0.5:
            continue

        # check whether eps is growing year by year
        years_eps = []
        for i in range(int(how_many_quarters/4)):
            years_eps.append(sum(eps_history[i*4:i*4+4]))

        years_eps_length = len(years_eps)
        is_growing = False
        for i in range(years_eps_length):
            if i+1 == years_eps_length:
                break
            is_growing = True if years_eps[i] > years_eps[i+1] else False
            if not is_growing:
                break

        if not is_growing:
            continue

        collect_result[key] = companys_info[key]

    return collect_result


if __name__ == '__main__':
    df1_list = {}
    now = datetime.datetime.now()
    year_now = now.year
    month_now = now.month
    last_quarter = get_lats_quater(month_now)
    df1 = financial_statement(year_now, last_quarter, type="綜合損益彙總表")

    for index, row in df1.iterrows():
        df1_list[row['公司代號']] = {}

    current_keys = df1_list.keys()
    print("current_keys = ", current_keys)
    # for index, row in df1.iterrows():
    #     df1_list[row['公司代號']].setdefault("eps", []).append(row['基本每股盈餘（元）'])


    quarter_start = last_quarter
    for year in range(year_now, 2012, -1):
        for quarter in range(quarter_start, 0, -1):
            print("year = ", year)
            print("quarter = ", quarter)
            df = get_data_by_year_quarter(year, quarter)
            for index, row in df.iterrows():
                if row['公司代號'] not in current_keys:
                    continue
                df1_list[row['公司代號']].setdefault("eps", []).append(row['基本每股盈餘（元）'])
            quarter_start = 4

    remain_companys = remove_bad_company_by_eps(current_keys, df1_list)
    print("remain_companys = ", remain_companys)
    print("remain_companys = ", len(remain_companys))


    # df2 = financial_statement(2013, 1, type="資產負債彙總表")
    #
    # df3 = financial_statement(2013, 1, type="營益分析彙總表")




    # print(data.loc[data['利息淨收益'] == 2801])
    # print(data['利息淨收益'] - data['利息以外淨損益'])
    # data['Address'] = data['利息淨收益'] - data['利息以外淨損益']
    # print(data['Address'])

