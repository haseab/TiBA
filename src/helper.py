from datetime import datetime, timedelta

import numpy as np
import pandas as pd


class Helper:

    @staticmethod
    def sum_tags_hours(df2, keyword):
        bool_list = [True if keyword in tag_list else False for tag_list in df2['Tags'].values]
        df2 = df2[bool_list]
        keyword_time = 0
        for i, j in zip(df2['Tags'].values, df2['SecDuration'].values):
            for x in i.split(','):
                if keyword in x:
                    keyword_time += Helper.fraction_to_float(x.strip(" ''").split(' ')[0])*j
        return keyword_time/3600

    @staticmethod
    def fraction_to_float(string):
        string = string.split('/')
        return float(string[0])/float(string[1])

    @staticmethod
    def get_actual_efficiency(loader, analyzer, start_date, end_date):
        data = loader.fetch_data(start_date, end_date)
        return analyzer.efficiency(loader, data)[:2]

    @staticmethod
    def clock_to_seconds(str_time):
        dt = datetime.strptime(str_time, "%H:%M:%S")
        delta = timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)
        return delta.seconds

    @staticmethod
    def seconds_to_clock(second_series: pd.Series) -> np.array:
        return np.array([str(timedelta(seconds=second)) for second in second_series])
