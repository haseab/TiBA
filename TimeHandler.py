import pandas as pd
import math
import requests
import matplotlib as plt
from datetime import datetime, timedelta
import numpy as np
import time
from toggl.TogglPy import Toggl


class TogglApi():

    def __init__(self, time_data, user_email, API_KEY):
        self.today = str(datetime.now())[:10]
        self.file = file
        self.data = pd.read_csv(time_data)
        self.api = API_KEY
        self.user = user_email

    def fetch_data(workspace_id, start_date=today, end_date=today):
        page = 1
        keys = {
            'user_agent': self.user,
            'workspace_id': workspace_id,
            'since': start_date,
            'until': end_date,
            'page': page,
            'order_desc': 'off'
        }
        url = 'https://toggl.com/reports/api/v2/details'
        url2 = 'https://toggl.com/api/v8/workspaces'
        headers = {'content-type': 'application/json'}

        date_list = np.array([i.strftime('%Y-%m-%d') for i in pd.date_range(start_date, end_date).to_pydatetime()])
        data = []
        for i in date_list:
            keys.update(page=1)
            keys.update(since=i)
            keys.update(until=i)
            r = requests.get(url, params=keys, headers=headers, auth=(API_KEY, 'api_token'))
            for i in range(1, r.json()['total_count'] // 50 + 2):
                keys.update(page=i)
                data += requests.get(url, params=keys, headers=headers, auth=(API_KEY, 'api_token')).json()['data']
        datas2 = []

        columns = [i[0].upper() + i[1:] for i in data[-1].keys()]
        for i in data:
            datas2.append(list(i.values()))
        df2 = pd.DataFrame(datas2, columns=columns)
        df2 = df2[['Id', 'Project', 'Description', 'Start', 'End', 'Tags']]
        df2['Start date'] = np.array([i[:10] for i in df2['Start'].values])
        df2['End date'] = np.array([i[:10] for i in df2['End'].values])
        df2['Start time'] = np.array([i[11:19] for i in df2['Start'].values])
        df2['End time'] = np.array([i[11:19] for i in df2['End'].values])
        df2['Tags'] = np.array([str(i).strip("''[]") for i in df2['Tags'].values])
        df2['SecDuration'] = duration_in_seconds(df2)
        # df2['Duration']
        df2 = df2[
            ['Id', 'Project', 'Description', 'Start date', 'Start time', 'End date', 'End time', 'Tags', 'SecDuration']]

        return df2

    def _clean(self, df):
        df = self.origin[['Id', 'Project', 'Description', 'Start date', 'Start time', 'End date', 'End time', 'Tags',
                          'SecDuration']].copy()
        df['Project'].fillna(value='No Project', inplace=True)
        df['Description'].fillna(value='', inplace=True)
        df['Tags'].fillna(value='', inplace=True)
        df['SecDuration'] = self._duration_in_seconds(df)
        return df

    def _days_ago(self, number_of_days_ago=0):
        return (datetime.now() - timedelta(days=number_of_days_ago)).strftime('%Y-%m-%d')

    def _get_project_list(self):
        df = self._clean(self.origin)
        return list(set(df['Project'].values))

    def _duration_in_seconds(self, df):
        startdates = df['Start date'] + '-' + df['Start time']
        enddates = df['End date'] + '-' + df['End time']

        startdates = np.array([datetime.strptime(i, '%Y-%m-%d-%H:%M:%S') for i in startdates])
        enddates = np.array([datetime.strptime(i, '%Y-%m-%d-%H:%M:%S') for i in enddates])

        unixS = pd.DatetimeIndex(startdates).astype(np.int64) // 10 ** 9
        unixE = pd.DatetimeIndex(enddates).astype(np.int64) // 10 ** 9
        return unixE - unixS

