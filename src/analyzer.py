import os
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv
from gcsa.google_calendar import GoogleCalendar

from helper import Helper as helper


class Analyzer:
    def __init__(self):
        load_dotenv()
        self.unplanned = GoogleCalendar(os.getenv("UNPLANNED_CALENDAR_ID"))
        self.wasted = {'Trading': 2, 'TV Show': 0, 'Social Media': 0.5, 'Messaging': 1, 'Casual Creative': 0.5,
                  'Podcast': 1.5, 'Private': 2.5, 'Music': 0.5, 'Sports': 1, 'Playing':0,
                  'People': 3.5, 'Exploring': 2, 'Chilling': 1.5, 'Movie': 0, 'Calling': 1, 'Dating': 3,
                  'YouTube': 0.5, 'News': 1, 'Under Influence': 1, 'Gaming': 0, 'Surfing Casually': 0, 'Relationship': 3}
        self.neutral = ['Washroom', 'Transportation', 'Unavoidable Intermission', 'Driving', 'Financial', 'Getting Ready',
                   'Thinking', 'Deciding', 'Intermission', 'Location', 'Listening',
                   'Hygiene','Helping Parents', 'Errands', 'Spiritual', 'Technicalities', 'Maintaining',
                   'Medical', 'Eating', 'Tracking', 'School', 'Food Prep/Clean/Order', 'Showering',
                   'Unavoidable Family Matters', 'Sleep', 'Shopping', 'Biking', 'Under Influence']
        self.productive = ['Analyzing','Reflecting', 'Project', 'Designing', 'General Learning', 'Yoga', 'Meditating', 'Working Out',
                      'Planning', 'Contemplating', 'Skill Learning', 'Studying/Homework', 'Problem Solving', 'Wycik', 'Organizing',
                      'Event', 'Business', 'Book', 'Report', 'Crypto', 'Helping/Giving', 'Meeting', 'Researching', 'Selling',
                      'Practical', 'Concentrating', 'Skill Practicing', 'Formal Learning', 'Recalling', 'Mentoring',
                      'Formal Working', 'Emailing']
    def max_mindful_slow(self, data):
        mindful_whitelist = ['Sleep', 'Concentration', 'Under Influence']
        slow_whitelist = ['Concentration', 'Crypto', 'Deciding', 'Formal Learning', 'Gaming',
                          'General Learning', "Contemplating", 'Meditating', 'Movie', 'Music', 'News', 'Podcast',
                          'Reflecting', 'Researching', 'Skill Learning', 'Social Media', 'Sleep', 'Sports',
                          'Thinking', 'Transportation', 'TV Show', 'Under Influence', 'Recalling', 'YouTube']

        week_summary = data[['Project', 'SecDuration']].groupby(by='Project').sum()

        max_mindful = 0
        max_slow = 0

        dftag = data[['Project', 'SecDuration', 'Tags']].set_index('Tags')
        dfslow = dftag[dftag.index.str.contains('Exclude Slow')].groupby("Project").sum()

        # Calculating total possible mindful seconds
        for project, seconds in zip(week_summary.index, week_summary['SecDuration'].values):
            if project not in mindful_whitelist:
                max_mindful += seconds

        # Calculating total possible slow seconds
        for project, seconds in zip(week_summary.index, week_summary['SecDuration'].values):
            if project not in slow_whitelist:
                max_slow += seconds
            if project in dfslow.index:
                excluded_seconds = dfslow.loc[project, "SecDuration"]
                max_slow -= excluded_seconds

        return round(max_mindful / 3600, 2), round(max_slow / 3600, 2)
    
    def prev_week(self, start_date, end_date, times=1):
        if (times == 0):
            return start_date, end_date
        if (times == 1):
            datetimes = pd.date_range(start_date, end_date).to_pydatetime()
            return str(datetimes[0]-timedelta(days=7))[:10], str(datetimes[-1] - timedelta(days=7))[:10]
        start_date, end_date = self.prev_week(start_date, end_date)
        return self.prev_week(start_date, end_date, times-1)
    
    def get_all_current_events(self, cal_dic):
        date_before = datetime.now().astimezone()
        date_after = datetime.now().astimezone() + timedelta(minutes=0.5)
        all_events = []
        
        for name, calendar in cal_dic.items():
            events = list(calendar.get_events(date_before, date_after, single_events=True))
            if events != []:
                events += [name]
                all_events += [events]
        return all_events


    def calculate_unplanned_time(self, start_date, end_date, week=False):
        # Turn start date and end date into datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
        end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)

        # Get all events from unplanned calendar
        all_events = self.unplanned.get_events(start_date, end_date, single_events=True)

        # Initialize total duration and a dictionary for daily totals
        total_duration = 0
        daily_totals = {str(start_date + timedelta(days=i))[:10]: 0 for i in range((end_date - start_date).days + 1)}

        # Calculate total time and accumulate daily totals
        for event in all_events:
            # print(event)
            duration = event.end - event.start
            total_duration += duration.total_seconds()

            # Accumulate daily total for the event's start day
            event_day = str(event.start.date())[:10]
            # print(event_day)
            if event_day in daily_totals:
                daily_totals[event_day] += duration.total_seconds()

        # If week=True, return the daily totals as a list
        if week:
          return {date: round(daily_totals[date]/3600, 3) for date in sorted(daily_totals.keys())}

        # Otherwise, return the total duration for the period
        return round(total_duration/3600, 3)

    
    def slow_mindful_scores(self, data):
        actual_mindful_hours = helper.sum_tags_hours(data, 'Mindfulness')
        actual_slow_hours = helper.sum_tags_hours(data, 'Slowness')
        actual_mindful_percentage = round(actual_mindful_hours / self.max_mindful_slow(data)[0], 5)
        actual_slow_percentage = round(actual_slow_hours / self.max_mindful_slow(data)[1], 5)

        start_date, end_date = data['Start date'][0], data['End date'][len(data)-2]

        string = f"""From {start_date} to {end_date}
Mindful Percentage: {actual_mindful_percentage * 100 }%
Slow Percentage:    {actual_slow_percentage * 100 }%
max hours to be mindful: {self.max_mindful_slow(data)[0]}
max hours to be slow   : {self.max_mindful_slow(data)[1]}
actual mindful (hours) : {round(actual_mindful_hours, 3)}
actual slow (hours)    : {round(actual_slow_hours, 3)}
        """
        return actual_mindful_percentage, actual_slow_percentage, string

    @staticmethod
    def get_week_summary(data):
        data = data[['Project', 'SecDuration']].groupby(by='Project').sum()
        data['Duration'] = helper.seconds_to_clock(data['SecDuration'])
        return data.sort_values(by='SecDuration', ascending=False).drop("SecDuration", axis=1)
    
    def dprint(self, *args):
        if self.debug:
            print(*args)

    def group_df(self, time_df):
    # Create a DataFrame
        df = pd.DataFrame(time_df, columns=['Id',"Start date", 'Start time', 'Project', 'Description', 'SecDuration', 'TagProductive', 'TagUnavoidable', 'TagUnproductive', 'Carryover', 'FlowExempt'])

        # Remove all Time entries that have ["Tracking", "Planning", "Eating", "Getting Ready", "Washroom"] , in the Project column and ALSO are under 100 seconds in SecDuration column
        # df = df[~((df['Project'].isin(["Tracking", "Planning", "Eating", "Getting Ready", "Washroom", "Messaging", "Calling", "Maintenance", "People", "Relationship", "Analyzing", "Emailing", "Listening", "Organizing", "Thinking", "Food Prep/Clean/Order", "Recalling", "Unavoidable Intermission", "Technicalities"])) & (df['SecDuration'] < 100))]

        df = df[~df['FlowExempt']]

        df['TagProductive'] = df['TagProductive'].astype(bool)
        df['TagUnproductive'] = df['TagUnproductive'].astype(bool)
        df['TagUnavoidable'] = df['TagUnavoidable'].astype(bool)
        
        # Mark Projects that are in self.productive as 'Productive'
        df['TagProductive'] = (df['Project'].isin(self.productive) | df['TagProductive']) & ~df['TagUnproductive'] & ~df['TagUnavoidable']
        df['TagProductiveCheck'] = df['TagProductive']
        df['ProjectTag'] = df['Project'] + ' ' + df['TagProductive'].astype(str) + ' ' + df['TagUnavoidable'].astype(str) + ' ' + df['TagUnproductive'].astype(str)
        df['Shifted ProjectTag'] = df['ProjectTag'].shift()
        shifted_carryover = df['Carryover'].shift(-1).fillna(False)
        df['Carryover'] = df['Carryover'] | shifted_carryover
        df['Shifted Carryover'] = df['Carryover'].shift()
        df['PreGroup'] = ~((df['ProjectTag'] == df['ProjectTag'].shift()) | (df['Carryover'] & df['Carryover'].shift()))
        df["Group"] = (~((df['ProjectTag'] == df['ProjectTag'].shift()) | (df['Carryover'] & df['Carryover'].shift()))).cumsum()

        # Group by the 'Group' column, and aggregate the 'SecDuration' using sum()
        # Also, take the first value of 'Project' for each group
        grouped = df.groupby('Group').agg({
            "Start date": "first",
            'Start time': 'first',
            'Project': 'first',
            'SecDuration': 'sum',
            'TagProductive': 'all',
            'TagProductiveCheck': 'any',
            'TagUnavoidable': 'all',
            'TagUnproductive': 'all',
        })

        # Update the 'Description' based on whether the group contains more than one row
        grouped['Description'] = grouped.apply(lambda row: 'General' if len(df[df['Group'] == row.name]) > 1 else df[df['Group'] == row.name].iloc[0]['Description'], axis=1)

        if not grouped['TagProductive'].equals(grouped['TagProductiveCheck']):
            dfPrint = grouped[~grouped['TagProductive'].eq(grouped['TagProductiveCheck'])]
            print(dfPrint[['Start date', 'Start time', 'Project']])
            raise ValueError("ERROR: TagProductive and TagProductiveCheck are not the same")

        # Reset the index
        grouped.reset_index(drop=True, inplace=True)
        grouped = grouped[["Start date", 'Start time', 'Project', 'Description', 'SecDuration', 'TagProductive', 'TagUnavoidable', 'TagUnproductive']]
        return grouped
    
    def calculate_1HUT(self, time_df, week=False):
        # display(Markdown("## p1HUT: Productive >1H Uninterrupted Time"))
        flow_threshold=50
        daily_totals = {}
        p1HUT_dict, n1HUT_dict, nw1HUT_dict, w1HUT_dict = {}, {}, {}, {}

        time_df['TagProductive'] = time_df['Tags'].str.contains('Productive')
        time_df['TagUnproductive'] = time_df['Tags'].str.contains('Unproductive')
        time_df['TagUnavoidable'] = time_df['Tags'].str.contains('Unavoidable')
        time_df['Carryover'] = time_df['Tags'].str.contains('Carryover')
        time_df['FlowExempt'] = time_df['Tags'].str.contains('FlowExempt')

        productive = self.productive
        wasted = self.wasted
        neutral = self.neutral

        time_df = self.group_df(time_df)
        for index in time_df.index:
            task_seconds = int(time_df.loc[index, "SecDuration"])
            project = time_df.loc[index, 'Project']
            task_date = time_df.at[index, 'Start date']  # Assuming 'Date' column exists
            tag_productive, tag_unavoidable, tag_unproductive = time_df.at[index, 'TagProductive'], time_df.at[index, 'TagUnavoidable'], time_df.at[index, 'TagUnproductive']
            if task_date not in daily_totals:
              daily_totals[task_date] = {'productive': 0, 'neutral': 0, 'non_wasted': 0, 'wasted': 0}
            
            neg_dic = ["Sleep"]
            if task_seconds > 60 * flow_threshold and project not in neg_dic:
                # print(task_date, project, time_df.loc[index, 'Start time'], time_df.loc[index, "Description"][:30], task_seconds/3600)
                # print(tag_productive, tag_unavoidable)
                if project in productive:
                    if tag_unavoidable:
                        daily_totals[task_date]['neutral'] += task_seconds
                    elif tag_unproductive:
                        daily_totals[task_date]['non_wasted'] += task_seconds
                        if task_seconds/3600 > wasted[project]:
                            # print(task_date, project, task_seconds/3600, wasted[project])
                            daily_totals[task_date]['wasted'] += task_seconds - wasted[project]*3600
                    elif tag_productive:
                        daily_totals[task_date]['productive'] += task_seconds
                    else:
                        print("PLEASE TAG YOUR CARRYOVER TASKS PROPERLY")
                        print(task_date, time_df.loc[index, 'Start time'], project, time_df.loc[index, "Description"][:10], task_seconds/3600)
                        raise ValueError("PLEASE TAG YOUR CARRYOVER TASKS PROPERLY")
                elif project in neutral:
                    if tag_productive:
                        daily_totals[task_date]['productive'] += task_seconds
                    elif tag_unproductive:
                        daily_totals[task_date]['non_wasted'] += task_seconds
                        if task_seconds/3600 > wasted[project]:
                            # print(task_date, project, task_seconds/3600, wasted[project])
                            daily_totals[task_date]['wasted'] += task_seconds - wasted[project]*3600
                    else:
                        daily_totals[task_date]['neutral'] += task_seconds
                elif project in wasted:
                    if tag_productive:
                        daily_totals[task_date]['productive'] += task_seconds
                    if tag_unavoidable:
                        daily_totals[task_date]['neutral'] += task_seconds
                    else:
                        daily_totals[task_date]['non_wasted'] += task_seconds
                        if task_seconds/3600 > wasted[project]:
                            # print(task_date, project, task_seconds/3600, wasted[project])
                            daily_totals[task_date]['wasted'] += task_seconds - wasted[project]*3600
        if week:
            for date in sorted(daily_totals.keys()):
                day_data = daily_totals[date]
                p1HUT_dict[date] = round(day_data['productive'] / 3600, 3)
                n1HUT_dict[date] = round(day_data['neutral'] / 3600, 3)
                nw1HUT_dict[date] = round(day_data['non_wasted'] / 3600, 3)
                w1HUT_dict[date] = round(day_data['wasted'] / 3600, 3)

            return {
                "p1HUT": p1HUT_dict,
                "n1HUT": n1HUT_dict,
                "nw1HUT": nw1HUT_dict,
                "w1HUT": w1HUT_dict
            }
                        
        else:
          # Calculate total duration for each category across the entire date range
          total_productive = sum(daily_totals[date]['productive'] for date in daily_totals)
          total_neutral = sum(daily_totals[date]['neutral'] for date in daily_totals)
          total_non_wasted = sum(daily_totals[date]['non_wasted'] for date in daily_totals)
          total_wasted = sum(daily_totals[date]['wasted'] for date in daily_totals)

          # Convert to hours and round
          p1HUT = round(total_productive / 3600, 3)
          n1HUT = round(total_neutral / 3600, 3)
          nw1HUT = round(total_non_wasted / 3600, 3)
          w1HUT = round(total_wasted / 3600, 3)

          # Count the number of days in which each category occurred
          Np1HUT = sum(1 for date in daily_totals if daily_totals[date]['productive'] > 0)
          Nn1HUT = sum(1 for date in daily_totals if daily_totals[date]['neutral'] > 0)
          Nnw1HUT = sum(1 for date in daily_totals if daily_totals[date]['non_wasted'] > 0)
          Nw1HUT = sum(1 for date in daily_totals if daily_totals[date]['wasted'] > 0)

          # Return the total duration for each category
          return {
              "p1HUT": p1HUT, "n1HUT": n1HUT, 
              "nw1HUT": nw1HUT, "w1HUT": w1HUT, 
              "Np1HUT": Np1HUT, "Nn1HUT": Nn1HUT, 
              "Nnw1HUT": Nnw1HUT, "Nw1HUT": Nw1HUT,
          }
        
    def efficiency(self, loader, data, debug=False, week=False):
        self.debug = debug
        productive = self.productive
        wasted = self.wasted
        neutral = self.neutral

        data['TagProductive'] = data['Tags'].str.contains('Productive')
        data['TagUnavoidable'] = data['Tags'].str.contains('Unavoidable')
        data['SecDuration'] = data['SecDuration'].astype(int)
        grouped_data = data.groupby(['Start date', 'Project', 'TagProductive', 'TagUnavoidable']).sum().reset_index()

        # Initializing total and daily metrics
        daily_metrics = {'hours_free': {}, 'efficiency':{}, 'inefficiency':{}, 'productive': {}, 'neutral': {}, 'wasted': {}, 'non_wasted': {}}

        # Processing each day and project
        for date, group in grouped_data.groupby('Start date'):
            day_totals = {key: 0 for key in daily_metrics.keys()}
            for _, row in group.iterrows():
                project, seconds = row['Project'], row['SecDuration']
                tag_productive, tag_unavoidable = row['TagProductive'], row['TagUnavoidable']
                day_totals['hours_free'] += seconds

                if project in neutral:
                    if tag_productive:
                        productive_seconds = seconds
                        day_totals['productive'] += productive_seconds
                    else:
                        day_totals['hours_free'] -= seconds
                        day_totals['neutral'] += seconds
                elif project in productive:
                    day_totals['productive'] += seconds
                    if tag_unavoidable:
                        neutral_seconds = seconds
                        day_totals['neutral'] += neutral_seconds
                        day_totals['hours_free'] -= neutral_seconds
                elif project in wasted.keys():
                    wasted_seconds = seconds #3600
                    if tag_productive:
                        productive_seconds = seconds
                        wasted_seconds -= productive_seconds 
                        day_totals['productive'] += productive_seconds
                    elif tag_unavoidable:
                        neutral_seconds = seconds
                        wasted_seconds -= neutral_seconds
                        day_totals['neutral'] += neutral_seconds
                        day_totals['hours_free'] -= neutral_seconds
                    non_wasted_seconds = min(wasted_seconds, wasted[project] * 3600)
                    day_totals['non_wasted'] += non_wasted_seconds
                    day_totals['wasted'] += (wasted_seconds - non_wasted_seconds)

            for metric, value in day_totals.items():
                daily_metrics[metric][str(date)[:10]] = round(value / 3600, 3)

        # Calculating hours free and efficiency for each day and adding to daily_metrics
        for date in daily_metrics['hours_free']:
            daily_metrics['efficiency'][date] = round(daily_metrics['productive'][date]/daily_metrics['hours_free'][date],4)
            daily_metrics['inefficiency'][date] = round(daily_metrics['wasted'][date]/daily_metrics['hours_free'][date],4)

        if week:
            return daily_metrics
        else:
            return {metric: sum(daily_metrics[metric].values()) for metric in daily_metrics}

