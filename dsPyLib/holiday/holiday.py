# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-01-23 15:02:45'

import datetime
from dsPyLib.utils.timez import str_to_date, date_to_str, is_weekend
from dsPyLib.pandas.pandas_config import *

"""
    中国法定节假日数据 (chinese_holiday_data)
        整个数据是一个数组，数组中的每一个元素包含了一年的法定节假日数据(按照年份升序排列)，为字典类型，下面简称年数据
        每一个年数据中包含年份(year)和节假日(holidays)两个字段:
            year: int
            holidays: array
                按照时间顺序列出了当年所有的法定节假日，里面的每个元素都为字典，包含下列的字段：
                    name: string, 节假日名称
                    day_off: array[string], 放假日列表(只包含月和日，格式为%m-%d)
                    day_on: array[string], 调休日(也就是要上班的日期)列表(只包含月和日，格式为%m-%d)

    注意：
        1. 需要每年更新数据
        2. 不同节假日的放假日和调休日可能会有重复(例如2020年的中秋节和国庆节就重叠)
"""

chinese_holiday_data = [
    {
        "year": 2020,
        "holidays": [
            {
                "name": "元旦",
                "day_off": ["01-01"],
                "day_on": []
            },
            {
                "name": "春节",
                "day_off": ["01-24", "01-25", "01-26", "01-27", "01-28", "01-29", "01-30"],
                "day_on": ["01-19", "02-01"]
            },
            {
                "name": "清明节",
                "day_off": ["04-04", "04-05", "04-06"],
                "day_on": []
            },
            {
                "name": "劳动节",
                "day_off": ["05-01", "05-02", "05-03", "05-04", "05-05"],
                "day_on": ["04-26", "05-09"]
            },
            {
                "name": "端午节",
                "day_off": ["06-25", "06-26", "06-27"],
                "day_on": ["06-28"]
            },
            {
                "name": "中秋节",
                "day_off": ["10-01", "10-02", "10-03", "10-04", "10-05", "10-06", "10-07", "10-08"],
                "day_on": ["09-27", "10-10"]
            },
            {
                "name": "国庆节",
                "day_off": ["10-01", "10-02", "10-03", "10-04", "10-05", "10-06", "10-07", "10-08"],
                "day_on": ["09-27", "10-10"]
            }
        ]
    },
]


def is_chinese_holiday(d: datetime.date) -> bool:
    """
    判断指定的日期是否为中国法定节假日(如果没有节假日数据，就只判断周末)
    :param d: 日期
    :return: True - 是; False - 不是
    """
    # 准备数据
    the_year = d.year

    # 从法定节假日数据中找到对应年份的数据
    holidays = None
    for item in chinese_holiday_data:
        if item['year'] == the_year:
            holidays = item['holidays']
            break

    # 生成放假日期列表和调休日期列表
    day_offs = list()
    day_ons = list()
    if holidays:  # 有对应的年份数据
        for item in holidays:
            for day_off in item['day_off']:
                s_day_off = f'{the_year}-{day_off}'
                d_day_off = str_to_date(s_day_off)
                day_offs.append(d_day_off)
            for day_on in item['day_on']:
                s_day_on = f'{the_year}-{day_on}'
                d_day_on = str_to_date(s_day_on)
                day_ons.append(d_day_on)

    # 判断传入的日期
    #   如果在day_offs中，则为节假日
    #   如果在day_ons中，则为工作日
    #   如果既不在day_offs中，也不在day_ons中，则周末为节假日，其它为工作日
    if d in day_offs:
        return True
    elif d in day_ons:
        return False
    else:
        return is_weekend(d)


def is_chinese_stock_holiday(d: datetime.date) -> bool:
    """
    判断指定日期是否为中国股市假日(周末始终是假日，节假日也是假日)
    :param d: 日期
    :return: True - 是; False - 不是
    """
    ret = is_weekend(d) or is_chinese_holiday(d)
    return ret


if __name__ == '__main__':
    """
        Demo
            打印指定年度中国节假日(holiday)和中国股市节假日(stock_holiday)
    """

    year = 2020
    s_start = f'{year}-01-01'
    s_end = f'{year}-12-31'
    d_start = str_to_date(s_start)
    d_end = str_to_date(s_end)

    day = d_start
    all_days = list()
    while day <= d_end:
        day_data = {
            'date': date_to_str(day),
            'week': day.weekday() + 1,
            'holiday': is_chinese_holiday(day),
            'stock_holiday': is_chinese_stock_holiday(day),
        }
        all_days.append(day_data)
        day = day + datetime.timedelta(days=1)

    df = pandas.DataFrame(all_days)
    print(df)
