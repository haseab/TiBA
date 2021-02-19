from helper import Helper
from toggl_loader import DataLoader

class Analyzer:
    def __init__(self):
        self.data = None

    def max_mindful_slow(self, data):
        mindful_whitelist = ['Sleep', 'Concentration', 'Under Influence']
        slow_whitelist = ['Analyzing', 'Concentration', 'Crypto', 'Deciding', 'Formal Learning', 'Gaming',
                          'General Learning', 'Meditating', 'Movie', 'Music', 'News', 'Podcast', 'Recalling',
                          'Reflecting', 'Researching', 'Skill Learning', 'Social Media', 'Sleep', 'Sports',
                          'Thinking', 'Transportation', 'TV Show', 'Under Influence', 'YouTube']

        week_summary = data[['Project', 'SecDuration']].groupby(by='Project').sum()

        max_mindful = 0
        max_slow = 0
        # Calculating total possible mindful seconds
        for project, seconds in zip(week_summary.index, week_summary['SecDuration'].values):
            if project not in mindful_whitelist:
                max_mindful += seconds

        # Calculating total possible slow seconds
        for project, seconds in zip(week_summary.index, week_summary['SecDuration'].values):
            if project not in slow_whitelist:
                max_slow += seconds
        return round(max_mindful / 3600, 2), round(max_slow / 3600, 2)

    def slow_mindful_scores(self, data):
        actual_mindful_hours = Helper.sum_tags_hours(data, 'Mindful')
        actual_slow_hours = Helper.sum_tags_hours(data, 'Slow')
        actual_mindful_percentage = round(actual_mindful_hours * 100 / self.max_mindful_slow(data)[0], 5)
        actual_slow_percentage = round(actual_slow_hours * 100 / self.max_mindful_slow(data)[1], 5)

        start_date, end_date = data['Start date'][0], data['End date'][len(data)-2]

        print(f'From {start_date} to {end_date}')
        print(f'Mindful Percentage: {actual_mindful_percentage}%')
        print(f'Slow Percentage:    {actual_slow_percentage}%')
        print(f"""max hours to be mindful: {self.max_mindful_slow(data)[0]}
                  max hours to be slow   : {self.max_mindful_slow(data)[1]}
                  actual mindful (hours) : {round(actual_mindful_hours, 3)}
                  actual slow (hours)    : {round(actual_slow_hours, 3)}
        """)
        return actual_mindful_percentage, actual_slow_percentage

    @staticmethod
    def get_week_summary(data):
        data = data[['Project', 'SecDuration']].groupby(by='Project').sum()
        data['Duration'] = Helper.seconds_to_clock(data['SecDuration'])
        return data.sort_values(by='SecDuration', ascending=False).drop("SecDuration", axis=1)

    def efficiency(self, loader, data):
        wasted = {'Trading': 2, 'TV Show': 0, 'Social Media': 0.5, 'Messaging': 1,
                  'Podcast': 1.5, 'Reflecting': 0.75, 'Private': 0.5, 'Music': 0.5, 'Sports': 1,
                  'People': 3.5, 'Exploring': 2, 'Chilling': 1.5, 'Movie': 0, 'Calling': 1,
                  'YouTube': 0.5, 'News': 1, 'Under Influence': 1, 'Gaming': 0, 'Surfing Casually': 0}
        neutral = ['Washroom', 'Transportation', 'Unavoidable Intermission', 'Driving', 'Financial', 'Getting Ready',
                   'Thinking', 'Deciding', 'Emailing', 'Intermission', 'Location', 'Transportation',
                   'Hygiene', 'Report', 'Helping Parents', 'Errands', 'Spiritual', 'Technicalities', 'Maintaining',
                   'Medical', 'Eating', 'Tracking', 'School', 'Food Prep/Clean/Order', 'Showering', 'Organizing',
                   'Unavoidable Family Matters', 'Sleep', 'Shopping', 'Biking', 'Under Influence']
        productive = ['Analyzing', 'Project', 'Designing', 'General Learning', 'Yoga', 'Meditating', 'Working Out',
                      'Planning', 'Contemplating', 'Skill Learning', 'Studying/Homework', 'Problem Solving', 'Wycik',
                      'Event', 'Business', 'Book', 'Crypto', 'Helping/Giving', 'Meeting', 'Researching', 'Selling',
                      'Practical', 'Concentrating', 'Skill Practicing', 'Formal Learning', 'Recalling', 'Tutoring',
                      'Formal Working']

        pure_wasted = {i: 0 for i in wasted.keys() if wasted[i] == 0}
        project_list = loader._get_project_list(data)
        non_wasted = set(project_list) - set(pure_wasted) - set(neutral) - set(productive)

        dftest = data[['Project', 'SecDuration', 'Tags']].set_index('Tags')
        # Adds the sum of all tags that are labeled "Productive", separated by project.
        dfproductive = dftest[dftest.index.str.contains('Productive')].groupby("Project").sum()
        dfneutral = dftest[dftest.index.str.contains('Unavoidable')].groupby("Project").sum()
        # print(dfproductive)
        # print(dfneutral)

        # Calculating Hours Free:
        data = data[['Project', 'SecDuration']].groupby(by='Project').sum()
        total, totalw, totalp, totaln = 0, 0, 0, 0
        productive_seconds, neutral_seconds = 0, 0
        for project, seconds in zip(data.index, data['SecDuration'].values):
            total += seconds
            if project in neutral:
                # print(project, seconds/3600)
                totaln += seconds
            elif project in productive:
                # print(j,round(j/3600,3))
                totalp += seconds
            elif project in wasted.keys():
                totalw += seconds

                if project in dfproductive.index:
                    productive_seconds = dfproductive.loc[project, "SecDuration"]
                    totalw -= productive_seconds
                    totalp += productive_seconds
                #             print(productive_seconds)
                #             print(project, wasted[project]*3600)
                elif project in dfneutral.index:
                    neutral_seconds = dfneutral.loc[project, "SecDuration"]
                    totalw -= neutral_seconds
                    totaln += neutral_seconds
                    # print(neutral_seconds)
                    # print(project, wasted[project]*3600)
                totalw -= min(seconds - productive_seconds - neutral_seconds, wasted[project] * 3600)
                productive_seconds = 0
        #             print(totalw)
        #             print()

        hours_free = (total - totaln) / 3600
        wasted_time = totalw / 3600
        efficiency = round(totalp / (total - totaln), 4)
        inefficiency = round(totalw / (total - totaln), 4)

        string = f"""
Hours free: {round(hours_free, 3)} hours 
Total productive hours = {round(totalp / 3600, 3)}
Wasted time: {round(wasted_time, 3)} hours
Inefficiency: {inefficiency*100}%
Efficiency: {efficiency*100}%
            """
        # print(string)
        return efficiency, inefficiency, string
