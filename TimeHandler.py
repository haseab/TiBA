import pandas as pd
import math
import requests
import matplotlib as plt
from datetime import datetime, timedelta
import numpy as np
import time

class TogglApi():
    """
    This class is mainly used to fetch data from the Toggl REST API. Data comes in the form of a JSON
    and then converted to a pandas dataframe object for further analysis.
    Data from a CSV is also available and is
    """
    def __init__(self, user_email, API_KEY, file =None):
        # Getting a reference for the date the instance is created
        self.today = str(datetime.now())[:10]
        self.api_key = API_KEY
        self.user = user_email

        # In case that there is a CSV filename passed as argument
        if file !=None:
            self.data = pd.read_csv(file)

    def fetch_data(self, workspace_id, start_date=None, end_date=None):
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
            'workspace_id': workspace_id,
            'since': start_date,
            'until': end_date,
            'page': page,
            'order_desc': 'off'
        }
        url = 'https://toggl.com/reports/api/v2/details'
        url2 = 'https://toggl.com/api/v8/workspaces'
        headers = {'content-type': 'application/json'}

        # Getting range of start->end dates in an array format
        date_list = np.array([i.strftime('%Y-%m-%d') for i in pd.date_range(start_date, end_date).to_pydatetime()])
        data = []

        # Interacting with API and getting data
        for i in date_list:
            keys.update(page=1)
            keys.update(since=i)
            keys.update(until=i)
            r = requests.get(url, params=keys, headers=headers, auth=(self.api_key, 'api_token'))
            for i in range(1, r.json()['total_count'] // 50 + 2):
                keys.update(page=i)
                data += requests.get(url, params=keys, headers=headers, auth=(self.api_key, 'api_token')).json()['data']
        datas2 = []

        # Getting the column names
        columns = [i[0].upper() + i[1:] for i in data[-1].keys()]

        # Converting JSON into a list of lists format
        for i in data:
            datas2.append(list(i.values()))

        # Data Cleaning and processing
        ## Creating pandas dataframe from columns and data
        df2 = pd.DataFrame(datas2, columns=columns)
        ## Choosing which columns to be used
        df2 = df2[['Id', 'Project', 'Description', 'Start', 'End', 'Tags']]
        ## Separating start_date from start_time and end_date from end_time
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

# Example code that would be run in order to fetch data
if __name__ == "__main__":
    #file = 'TogglOfficialData-2018-2020.csv'
    #toggl = TogglApi(file, EMAIL, API_KEY)
