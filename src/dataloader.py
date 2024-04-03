import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytz  # Make sure to import pytz for timezone data
import requests
from dotenv import load_dotenv


class DataLoader:
    """
    This class is mainly used to fetch data from the Toggl REST API. Data comes in the form of a JSON
    and then converted to a pandas dataframe object for further analysis.
    Data from a CSV is also available.
    """
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Getting the current date
        self.today = str(datetime.now())[:10]
        # Fetching secret values from the environment variables
        self.TOGGL_EMAIL = os.getenv("TOGGL_EMAIL")
        self.TOGGL_API_KEY = os.getenv("TOGGL_API_KEY")
        self.TOGGL_WORKSPACE_ID = os.getenv("TOGGL_WORKSPACE_ID")
        self.NOTION_TOKEN_V2 = os.getenv("NOTION_TOKEN_V2")


    def fetch_data(self, start_date=None, end_date=None, tasks_ago=None):
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
            'user_agent': self.TOGGL_EMAIL,
            'workspace_id': self.TOGGL_WORKSPACE_ID,
            'since': start_date,
            'until': end_date,
            'page': page,
            'order_desc': 'off'
        }
        url = 'https://api.track.toggl.com/reports/api/v2/details'
        headers = {'content-type': 'application/json'}

        # Interacting with API and getting data
        data = []
        r = requests.get(url, params=keys, headers=headers, auth=(self.TOGGL_API_KEY, 'api_token'))

        page_count = r.json()['total_count'] // 50 + 1
        count = 0
        for page in range(1, page_count + 1):
            keys.update(page=page)
            data_point = requests.get(url, params=keys, headers=headers, auth=(self.TOGGL_API_KEY, 'api_token'))
            data += data_point.json()['data']
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

    def get_toggl_current_task(self):
        url = "https://api.track.toggl.com/api/v8/time_entries/current"
        headers = {'content-type': 'application/json'}
        api_token = os.getenv("TOGGL_API_KEY")
        # Interacting with API and getting data
        r = requests.get(url, headers=headers, auth=(api_token, 'api_token'))
        data = r.json()['data']

        projects = self._get_project_list(self.TOGGL_EMAIL,self.TOGGL_API_KEY)

        project_name=projects[data['pid']]
        del data['pid']
        data['project'] = project_name

        columns = [column[0].upper() + column[1:] for column in data.keys()]

        if "Description" not in columns: 
            data['Description'] = ""
            columns.append("Description")
    
        if "pid" not in columns: 
            data['pid'] = ""
            columns.append("pid")

        df2 = pd.DataFrame([data.values()], columns=columns)

        df2['Start'] = pd.to_datetime(df2['Start'], utc=True)
        df2['Start'] = df2['Start'].dt.tz_convert('Canada/Eastern').dt.tz_localize(None)

        df2 = df2.drop('At', axis=1)

        df2['End'] = datetime.utcnow().replace(tzinfo=pytz.utc)  # Make 'End' timezone aware
        df2['End'] = df2['End'].dt.tz_convert('Canada/Eastern').dt.tz_localize(None)


        secDuration = float((df2['End']-df2['Start']).dt.total_seconds())

        df2['SecDuration'] = [int(secDuration)]

        df2['Start date'] = np.array([str(i)[:10] for i in df2['Start'].values])
        df2['End date'] = np.array([str(i)[:10] for i in df2['End'].values])
        df2['Start time'] = np.array([str(i)[11:19] for i in df2['Start'].values])
        df2['End time'] = np.array([str(i)[11:19] for i in df2['End'].values])

        df2['Tags'] = [""]
        df2 = df2[['Id', 'Project', 'Description', 'Start date', 'Start time', 'End date', 'End time', 'Tags', 'SecDuration']]
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

    def _get_project_list(self, account, api_token):
        projects = requests.get(f"https://api.track.toggl.com/api/v8/workspaces/{account}/projects", auth=(api_token, "api_token"))
        projects_list = projects.json()
        project_id_to_name = {project['id']: project['name'] for project in projects_list}
        return project_id_to_name
    

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
