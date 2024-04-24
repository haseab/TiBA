import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from notion.block.basic import BulletedListBlock, ToggleBlock
from notion.client import NotionClient
from openai import OpenAI


class AutoGenerator:
    """
    purpose is to automate the generation of weekly reports
    """

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        # Getting the current date
        self.today = str(datetime.now())[:10]
        self.TOGGL_EMAIL = os.getenv("TOGGL_EMAIL")
        self.TOGGL_API_KEY = os.getenv("TOGGL_API_KEY")
        self.TOGGL_WORKSPACE_ID = os.getenv("TOGGL_WORKSPACE_ID")
        self.NOTION_TOKEN_V2 = os.getenv("NOTION_TOKEN_V2")
        self.OPENAI = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.MODEL = "gpt-4-0125-preview"

    def get_JSON_from_TXT(self, date):
        """
        This function will read the txt file using date as the filename
        and submit to Open AI's Chat Completion API to get a JSON response
        """
        # file format is "2023-08-01 - Daily Report (1)"
        with open(f"{date} - Daily Report (1).txt", "r") as file:
            text = file.read()

        prompt = """Return a list of JSONs in the following format:
FORMAT:
{' Project': ' Project',
' Title': ' Creating -  Feature: more accurate distraction number prod dashboard',
' Description': ' I basically just cut the number of distraction numbers in half because I just thought it was gonna be a more accurate way of displaying How often I'm getting distracted That's it zigzag Title creating feature start dashboard on startup prod dashboard description This took way longer than I expected '}

Each JSON is delimited by "Zigzag". Do not include "Zigzag" in your output

The text is transcribed from an audio recording, so fix any text you suspect is a spelling error.

Some important Characters (for correct spelling):

- Lishy
- Afif Bhimani
- Shabnam Ullah
- Padar Jaan
- Dillion Verma
- Kerim Caliskan

TEXT:

"""  # make call to openai
        response = self.openai.chat.completions.create(
            model=self.model,
            temperature=0,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
        )
        return response["choices"][0]["message"]["content"]

    def extract_whisper(self, date):
        """
        This function will extract the JSONs from the response and return them as a list
        """
        response = self.get_JSON_from_TXT(date)
        JSON = response
        df_json = (pd.DataFrame(JSON),)
        # store as a dictionary
        JSONs = df_json.to_dict()

        return JSONs


# Example code that would be run in order to fetch data
if __name__ == "__main__":
    pass
    # file = 'TogglOfficialData-2018-2020.csv'
    # toggl = TogglApi(file, EMAIL, API_KEY)
