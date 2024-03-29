from tiba_helper import TiBAHelper
from toggl_loader import DataLoader


class Analyzer:
    def __init__(self):
        self.data = None

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

    def slow_mindful_scores(self, data):
        actual_mindful_hours = TiBAHelper.sum_tags_hours(data, 'Mindfulness')
        actual_slow_hours = TiBAHelper.sum_tags_hours(data, 'Slowness')
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
        data['Duration'] = TiBAHelper.seconds_to_clock(data['SecDuration'])
        return data.sort_values(by='SecDuration', ascending=False).drop("SecDuration", axis=1)

    def efficiency(self, loader, data):
        wasted = {'Trading': 2, 'TV Show': 0, 'Social Media': 0.5, 'Messaging': 1, 'Casual Creative': 0.5,
                  'Podcast': 1.5, 'Reflecting': 0.75, 'Private': 0.5, 'Music': 0.5, 'Sports': 1, 'Playing':0,
                  'People': 3.5, 'Exploring': 2, 'Chilling': 1.5, 'Movie': 0, 'Calling': 1, 'Dating': 0,
                  'YouTube': 0.5, 'News': 1, 'Under Influence': 1, 'Gaming': 0, 'Surfing Casually': 0} 
        neutral = ['Washroom', 'Transportation', 'Unavoidable Intermission', 'Driving', 'Financial', 'Getting Ready',
                   'Thinking', 'Deciding', 'Intermission', 'Location', 'Listening',
                   'Hygiene', 'Report', 'Helping Parents', 'Errands', 'Spiritual', 'Technicalities', 'Maintaining',
                   'Medical', 'Eating', 'Tracking', 'School', 'Food Prep/Clean/Order', 'Showering', 'Organizing',
                   'Unavoidable Family Matters', 'Sleep', 'Shopping', 'Biking', 'Under Influence']
        productive = ['Analyzing', 'Project', 'Designing', 'General Learning', 'Yoga', 'Meditating', 'Working Out',
                      'Planning', 'Contemplating', 'Skill Learning', 'Studying/Homework', 'Problem Solving', 'Wycik',
                      'Event', 'Business', 'Book', 'Crypto', 'Helping/Giving', 'Meeting', 'Researching', 'Selling',
                      'Practical', 'Concentrating', 'Skill Practicing', 'Formal Learning', 'Recalling', 'Tutoring',
                      'Formal Working', 'Emailing']

        pure_wasted = {project: 0 for project in wasted.keys() if wasted[project] == 0}
        project_list = loader._get_project_list(data)
        non_wasted = set(project_list) - set(pure_wasted) - set(neutral) - set(productive)

        dftest = data[['Project', 'SecDuration', 'Tags']].set_index('Tags')
        # Adds the sum of all tags that are labeled "Productive", separated by project.
        dfproductive = dftest[dftest.index.str.contains('Productive')].groupby("Project").sum()
        dfneutral = dftest[dftest.index.str.contains('Unavoidable')].groupby("Project").sum()
        # print(dfproductive)
        # print()

        # Calculating Hours Free:
        data = data[['Project', 'SecDuration']].groupby(by='Project').sum()
        total, totalw, totalp, totaln, totalnw = 0, 0, 0, 0, 0
        for project, seconds in zip(data.index, data['SecDuration'].values):
            productive_seconds, neutral_seconds = 0, 0
            total += seconds
            if project in neutral:
                print(project, seconds/3600)
                totaln += seconds
                # print(totaln/3600)
            elif project in productive:
                # print(project,round(seconds/3600,3))
                totalp += seconds
            elif project in wasted.keys():
                totalw += seconds
                # print(totalw)
                # print(project, seconds/3600)
                # print(dfneutral.index)
                if project in dfproductive.index:
                    productive_seconds = dfproductive.loc[project, "SecDuration"]
                    totalw -= productive_seconds
                    totalp += productive_seconds
                    # print(project, productive_seconds)
                if project in dfneutral.index:
                    neutral_seconds = dfneutral.loc[project, "SecDuration"]
                    totalw -= neutral_seconds
                    totaln += neutral_seconds
                    print(neutral_seconds)
                # print(f"Total: {totalw}")
                totalw -= min(seconds - productive_seconds - neutral_seconds, wasted[project] * 3600)
                totalnw += min(seconds - productive_seconds - neutral_seconds, wasted[project] * 3600)
                # print(f"Total: {totalw}")
                # print(project, totalw)

        hours_free = round((total - totaln) / 3600, 2)
        wasted_time = totalw / 3600
        efficiency = round(totalp / (total - totaln), 4)
        inefficiency = round(totalw / (total - totaln), 4)
        non_wasted_time = totalnw/3600
        # print(non_wasted_time)

        if totalnw != total-totaln-totalp-totalw:
            raise Exception("Time fell through the cracks!")

        string = f"""
Hours free: {round(hours_free, 3)} hours 
Total productive hours = {round(totalp / 3600, 3)}
Wasted time: {round(wasted_time, 3)} hours
Inefficiency: {inefficiency*100}%
Efficiency: {efficiency*100}%
            """
        # print(string)
        return efficiency, inefficiency, string
