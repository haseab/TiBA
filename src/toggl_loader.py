import pandas as pd
import math
import requests
import matplotlib as plt
from datetime import datetime, timedelta
import numpy as np
import os
import time

class DataLoader:
    """
    This class is mainly used to fetch data from the Toggl REST API. Data comes in the form of a JSON
    and then converted to a pandas dataframe object for further analysis.
    Data from a CSV is also available and is
    """
    def __init__(self):
        # Getting a reference for the date the instance is created
        self.path = os.path.dirname(os.getcwd()) + r"\local\toggl_account.txt"
        secret_info = pd.read_csv(self.path)
        self.today = str(datetime.now())[:10]
        self.user = secret_info.loc[0,"email"]
        self.api_key = secret_info.loc[0,"key"]
        self.account = secret_info.loc[0,"account"]

    def fetch_data(self, start_date=None, end_date=None):
        """
        Interacts with Toggl REST API and gets the minute data from the date range given.
        If start and end date are the same, the data for that day will be shown (non-inclusive)
        :param workspace_id: Your Toggl workspace id (provided in website)
        :param start_date: the starting date of the data
        :param end_date: the ending date of the data
        :return: pandas dataframe, the time data
        """
        # Assuming they did not pass in a start and end date
        if start_date == None:
            start_date = self.today
        if end_date == None:
            end_date = self.today

        page = 1
        # Parameters used to pass into API
        keys = {
            'user_agent': self.user,
            'workspace_id': self.account,
            'since': start_date,
            'until': end_date,
            'page': page,
            'order_desc': 'off'
        }
        url = 'https://toggl.com/reports/api/v2/details'
        headers = {'content-type': 'application/json'}

        # Interacting with API and getting data
        data = []
        r = requests.get(url, params=keys, headers=headers, auth=(self.api_key, 'api_token'))
        page_count = r.json()['total_count'] // 50 + 1
        for page in range(1, page_count + 1):
            keys.update(page=page)
            data += requests.get(url, params=keys, headers=headers, auth=(self.api_key, 'api_token')).json()['data']
        datas2 = []

        # Getting the column names
        columns = [column[0].upper() + column[1:] for column in data[-1].keys()]

        # Converting JSON into a list of lists format
        for i in data:
            datas2.append(list(i.values()))

        # Data Cleaning and processing
        ## Creating pandas dataframe from columns and data
        df2 = pd.DataFrame(datas2, columns=columns)
        ## Choosing which columns to be used
        df2 = df2[['Id', 'Project', 'Description', 'Start', 'End', 'Tags']]
        ## Separating start_date column from start_time column and end_date from end_time
        df2['Start date'] = np.array([i[:10] for i in df2['Start'].values])
        df2['End date'] = np.array([i[:10] for i in df2['End'].values])
        df2['Start time'] = np.array([i[11:19] for i in df2['Start'].values])
        df2['End time'] = np.array([i[11:19] for i in df2['End'].values])
        df2['Tags'] = np.array([str(i).strip("''[]") for i in df2['Tags'].values])
        ## Adding a column that converts the datetime difference into a duration
        df2['SecDuration'] = self._duration_in_seconds(df2)
        # df2['Duration']
        df2 = df2[
            ['Id', 'Project', 'Description', 'Start date', 'Start time', 'End date', 'End time', 'Tags', 'SecDuration']]

        return df2

    def get_range_data(self, start_date='2020-1-1', end_date='2020-12-31'):
        datetimes = pd.date_range(start_date, end_date).to_pydatetime()
        if len(datetimes) - 1 < 8:
            return self.fetch_data(start_date, end_date)
        else:
            date_list = [i.strftime('%Y-%m-%d') for i in datetimes]
            return df[df['Start date'].isin(date_list)]

    def _clean(self, data):
        df = data[['Id', 'Project', 'Description', 'Start date', 'Start time', 'End date', 'End time', 'Tags',
                          'SecDuration']].copy()
        df['Project'].fillna(value='No Project', inplace=True)
        df['Description'].fillna(value='', inplace=True)
        df['Tags'].fillna(value='', inplace=True)
        df['SecDuration'] = self._duration_in_seconds(df)
        return df

    def _days_ago(self, number_of_days_ago=0):
        return (datetime.now() - timedelta(days=number_of_days_ago)).strftime('%Y-%m-%d')

    def _get_project_list(self,df):
        return list(set(df['Project'].values))

    def _duration_in_seconds(self, df):
        startdates = df['Start date'] + '-' + df['Start time']
        enddates = df['End date'] + '-' + df['End time']

        startdates = np.array([datetime.strptime(i, '%Y-%m-%d-%H:%M:%S') for i in startdates])
        enddates = np.array([datetime.strptime(i, '%Y-%m-%d-%H:%M:%S') for i in enddates])

        unixS = pd.DatetimeIndex(startdates).astype(np.int64) // 10 ** 9
        unixE = pd.DatetimeIndex(enddates).astype(np.int64) // 10 ** 9
        return unixE - unixS

# Example code that would be run in order to fetch data
if __name__ == "__main__":
    pass
    #file = 'TogglOfficialData-2018-2020.csv'
    #toggl = TogglApi(file, EMAIL, API_KEY)
