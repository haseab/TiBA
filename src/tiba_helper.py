import numpy as np
import pandas as pd

class TiBAHelper:

    @staticmethod
    def sum_tags_hours(df2, keyword):
        bool_list = [True if keyword in tag_list else False for tag_list in df2['Tags'].values]
        df2 = df2[bool_list]
        keyword_time = 0
        for i, j in zip(df2['Tags'].values, df2['SecDuration'].values):
            for x in i.split(','):
                if keyword in x:
                    keyword_time += TiBAHelper.fraction_to_float(x.strip(" ''").split(' ')[0])*j
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
    def seconds_to_clock(series: pd.Series) -> np.array:
        duration = []
        for seconds in series:
            hours, minutes, seconds = str(int(seconds // 3600)), str(int(seconds % 3600 // 60)), str(int((seconds % 3600) % 60))
            if len(minutes) < 2:
                minutes = '0' + minutes
            if len(seconds) < 2:
                seconds = '0' + seconds
            if len(series) == 1:
                return f'{hours}:{minutes}:{seconds}'
            duration.append(f'{hours}:{minutes}:{seconds}')
        return np.array(duration)
