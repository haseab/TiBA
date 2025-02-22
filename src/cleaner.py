from datetime import datetime, timedelta

from IPython.display import Latex, Markdown, display

from helper import Helper as helper


class Cleaner:
    def __init__(self):
        self.wasted = {
            "Trading": 2,
            "TV Show": 0,
            "Social Media": 0.5,
            "Messaging": 1,
            "Casual Creative": 0.5,
            "Podcast": 1.5,
            "Private": 2.5,
            "Music": 0.5,
            "Sports": 1,
            "Playing": 0,
            "People": 3.5,
            "Exploring": 2,
            "Chilling": 1.5,
            "Movie": 0,
            "Calling": 1,
            "Dating": 3,
            "YouTube": 0.5,
            "News": 1,
            "Under Influence": 1,
            "Gaming": 0,
            "Surfing Casually": 0,
            "Relationship": 3,
        }
        self.neutral = [
            "Washroom",
            "Transportation",
            "Unavoidable Intermission",
            "Driving",
            "Financial",
            "Getting Ready",
            "Thinking",
            "Deciding",
            "Intermission",
            "Location",
            "Listening",
            "Hygiene",
            "Helping Parents",
            "Errands",
            "Spiritual",
            "Technicalities",
            "Maintaining",
            "Medical",
            "Eating",
            "Tracking",
            "School",
            "Food Prep/Clean/Order",
            "Showering",
            "Unavoidable Family Matters",
            "Resting",
            "Shopping",
            "Biking",
            "Under Influence",
        ]
        self.productive = [
            "Analyzing",
            "Reflecting",
            "Project",
            "Designing",
            "General Learning",
            "Yoga",
            "Meditating",
            "Working Out",
            "Planning",
            "Contemplating",
            "Skill Learning",
            "Studying/Homework",
            "Problem Solving",
            "Wycik",
            "Organizing",
            "Event",
            "Business",
            "Book",
            "Report",
            "Crypto",
            "Helping/Giving",
            "Meeting",
            "Researching",
            "Selling",
            "Practical",
            "Concentrating",
            "Skill Practicing",
            "Formal Learning",
            "Recalling",
            "Mentoring",
            "Formal Working",
            "Emailing",
        ]

    def show_time_gaps(self, start_date, end_date, time_df):
        """Note: This function depends on the index being incremental integers starting at 0"""
        for index in range(len(time_df) - 1):
            end_time_before = time_df.loc[index, "End time"]
            start_time_after = time_df.loc[index + 1, "Start time"]
            project_before = time_df.loc[index, "Project"]
            project_after = time_df.loc[index + 1, "Project"]
            if (
                end_time_before != start_time_after
                and project_before != "Location"
                and project_after != "Location"
            ):
                disparity = helper.clock_to_seconds(
                    start_time_after
                ) - helper.clock_to_seconds(end_time_before)
                if disparity < 60 and disparity > -60:
                    continue
                print(disparity)
                display(time_df[index : index + 2])

        # Checking for midnight separation
        for index in range(len(time_df)):
            start_date_before = time_df.loc[index, "Start date"]
            end_date_before = time_df.loc[index, "End date"]
            end_date_before_time = time_df.loc[index, "End time"]
            if (
                start_date_before != end_date_before
                and end_date_before_time[:5] != "00:00"
            ):
                print("Over MIDNIGHT")
                display(time_df[index : index + 1])

        print("Done")
        return None

    def show_duplicates(self, start_date, end_date, time_df):
        """Note: This function depends on the index being incremental integers starting at 0"""
        for index in range(len(time_df) - 1):
            desc_before = time_df.loc[index, "Description"]
            desc_after = time_df.loc[index + 1, "Description"]
            project_after = time_df.loc[index + 1, "Project"]
            start_date_before = time_df.loc[index, "Start date"]
            start_date_after = time_df.loc[index + 1, "Start date"]

            tag_before = time_df.loc[index, "Tags"]
            tag_after = time_df.loc[index + 1, "Tags"]

            if (
                desc_before != ""
                and desc_before == desc_after
                and project_after != "Eating"
                and tag_before == tag_after
                and start_date_before == start_date_after
            ):
                print(desc_before)
                display(time_df[index : index + 2])
        print("Done")
        return None

    def show_abnormal_times(self, start_date, end_date, time_df, neg=True, large=True):
        display(Markdown("## Negligible times"))
        if neg:
            for index in time_df.index:
                task_seconds = int(time_df.loc[index, "SecDuration"])
                project_before = time_df.loc[index, "Project"]
                if task_seconds <= 5 and project_before != "Location":
                    display(time_df[index : index + 1])

        display(Markdown("## Large times"))
        productive_list = []
        neutral_list = []
        non_wasted_list = []
        wasted_list = []
        productive = self.productive
        wasted = self.wasted
        neutral = self.neutral

        if large:
            for index in time_df.index:
                task_seconds = int(time_df.loc[index, "SecDuration"])
                project = time_df.loc[index, "Project"]
                neg_dic = ["Resting"]
                if task_seconds > 3600 and project not in neg_dic:
                    if project in productive:
                        print("Productive:", project, timedelta(seconds=task_seconds))
                        productive_list.append(task_seconds)
                    elif project in neutral:
                        print("Neutral:", project, timedelta(seconds=task_seconds))
                        neutral_list.append(task_seconds)
                    elif project in wasted:
                        if (
                            task_seconds / 3600 < wasted[project]
                            and task_seconds / 3600 > 1
                        ):
                            print(
                                "Non Wasted:", project, timedelta(seconds=task_seconds)
                            )
                            non_wasted_list.append(task_seconds)
                        if task_seconds / 3600 > wasted[project]:
                            print(
                                "Non Wasted:",
                                project,
                                timedelta(seconds=wasted[project] * 3600),
                            )
                            non_wasted_list.append(wasted[project] * 3600)

                        if (task_seconds - wasted[project] * 3600) > 1:
                            print(
                                "WASTED:",
                                project,
                                timedelta(
                                    seconds=task_seconds - wasted[project] * 3600
                                ),
                            )
                            wasted_list.append(task_seconds)
                    display(time_df[index : index + 1])

                if project == "Timetracking" and task_seconds > 600:
                    print("Timetracking over 10 minutes")
                    # print(timedelta(seconds=task_seconds))
                    display(time_df[index : index + 1])

                if project == "Timetracking" and task_seconds > 600:
                    print("Walking over 10 minutes")
                    # print(timedelta(seconds=task_seconds))
                    display(time_df[index : index + 1])

                if project == "Biking" and task_seconds > 900:
                    print("Scootering over 15 minutes")
                    # print(timedelta(seconds=task_seconds))
                    display(time_df[index : index + 1])

            string = f""" 
          TOTAL MINIMUM 1 HOUR UNINTERRUPTED TIME SPLIT (1HUT):
          Productive: {round(sum(productive_list)/3600,2)} hours over {len(productive_list)} tasks
          Neutral: {round(sum(neutral_list)/3600,2)} hours over {len(neutral_list)} tasks
          Non Wasted: {round(sum(non_wasted_list)/3600,2)} hours over {len(non_wasted_list)} tasks
          Wasted: {round(sum(wasted_list)/3600,2)} hours over {len(wasted_list)} tasks"""
            print(string)
