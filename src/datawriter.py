import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from notion.block import BulletedListBlock, ToggleBlock
from notion.client import NotionClient

from dataloader import DataLoader


class DataWriter:
    """
    This class is mainly used to write data
    """

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        # Getting the current date
        self.loader = DataLoader()
        self.today = str(datetime.now())[:10]
        # Fetching secret values from the environment variables
        self.TOGGL_EMAIL = os.getenv("TOGGL_EMAIL")
        self.TOGGL_API_KEY = os.getenv("TOGGL_API_KEY")
        self.TOGGL_WORKSPACE_ID = os.getenv("TOGGL_WORKSPACE_ID")
        self.NOTION_TOKEN_V2 = os.getenv("NOTION_TOKEN_V2")

    def get_report_summary(self, start_date, end_date, df):
        skip_projects = [
            "Biking",
            "Crypto",
            "Driving",
            "Food Prep/Clean/Order",
            "Getting Ready",
            "Intermission",
            "Location",
            "Maintaining",
            "Showering",
            "Resting",
            "Spiritual",
            "Tracking",
            "Transportation",
            "Washroom",
            "Hygiene",
            "Unavoidable Intermission",
        ]
        report_template_link = os.getenv("NOTION_REPORT_TEMPLATE_LINK")

        try:
            client = NotionClient(token_v2=self.NOTION_TOKEN_V2)
        except Exception as e:
            print(self.NOTION_TOKEN_V2)
            raise (e)

        block = client.get_block(report_template_link)

        data = (
            df.groupby(["Project", "Description"])
            .sum()
            .reset_index()
            .sort_values(by=["Project", "SecDuration"], ascending=[True, False])
        )

        projectGrouped = df.groupby("Project")["SecDuration"].sum().reset_index()
        projectGroupedSorted = projectGrouped.sort_values(
            by="SecDuration", ascending=False
        )

        for project in projectGroupedSorted["Project"].unique():
            if project in skip_projects:
                continue

            parent = block.children.add_new(ToggleBlock, title=project)

            dataIndexed = data.set_index(["Project", "Description"])
            # for keys in entry["time_entries"].keys():
            for description in dataIndexed.loc[project].index:
                hours = round(
                    dataIndexed.loc[(project, description), "SecDuration"] / 3600, 2
                )
                string = f"{description} -- {hours}h -- "
                print(string)
                try:
                    child = parent.children.add_new(BulletedListBlock, title=string)
                except Exception as e:
                    continue

        return data

    def _clean(self, data):
        df = data[
            [
                "Id",
                "Project",
                "Description",
                "Start date",
                "Start time",
                "End date",
                "End time",
                "Tags",
                "SecDuration",
            ]
        ].copy()
        df["Project"].fillna(value="No Project", inplace=True)
        df["Description"].fillna(value="", inplace=True)
        df["Tags"].fillna(value="", inplace=True)
        df["SecDuration"] = self._duration_in_seconds(df)
        return df

    def _days_ago(self, number_of_days_ago=0):
        return (datetime.now() - timedelta(days=number_of_days_ago)).strftime(
            "%Y-%m-%d"
        )

    def _get_project_list(self, account, api_token):
        projects = requests.get(
            f"https://api.track.toggl.com/api/v9/workspaces/{account}/projects",
            auth=(api_token, "api_token"),
        )
        projects_list = projects.json()
        project_id_to_name = {
            project["id"]: project["name"] for project in projects_list
        }
        return project_id_to_name

    def _duration_in_seconds(self, df):
        startdates = df["Start date"] + "-" + df["Start time"]
        enddates = df["End date"] + "-" + df["End time"]

        startdates = np.array(
            [datetime.strptime(i, "%Y-%m-%d-%H:%M:%S") for i in startdates]
        )
        enddates = np.array(
            [datetime.strptime(i, "%Y-%m-%d-%H:%M:%S") for i in enddates]
        )

        unixS = pd.DatetimeIndex(startdates).astype(np.int64) // 10**9
        unixE = pd.DatetimeIndex(enddates).astype(np.int64) // 10**9
        return unixE - unixS


# Example code that would be run in order to fetch data
if __name__ == "__main__":
    pass
    # file = 'TogglOfficialData-2018-2020.csv'
    # toggl = TogglApi(file, EMAIL, API_KEY)
