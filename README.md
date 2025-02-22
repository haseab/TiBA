# TiBA

## What Problem Does this Solve?

I have always been an avid gamer since I can remember. I used to play so much that it used to affect my grades (all the way up into 2nd year University!). In fear that I was addicted, I used an app called _Toggl_ started tracking **every minute** of my time (yes, every minute) to see where my time is really going at. It was a monumental revelation to the say the least. It is referenced below:

![](https://github.com/haseab/TiBA/blob/master/Github_tiba_time_results.png)

I spent over 57 hours a week either Gaming or watching YouTube. and just by able to **see** how much time I was spending, the amount of time spent on video games the very next week got reduced by 50%. For a while I would manually analyze, look at cumulative sums, look at a few graphs, etc. However since I was tracking every minute, I was accumulating hundreds of pieces of data every single day and I didn't have enough time to keep up with it.

After 2 years, I have accumulated over 50 000 actions which is a significant amount of data considering that this data about **me**. Exactly one year after I started tracking my time, I no longer was playing video games, and I had this brilliant idea. I could have an automatic time analyzer which can do all the way from analyzing my behaviour and telling me behaviours that I'm not even conscious of, to being my personal assistant and validating my time tracking **live** with my Google Calendar and seeing whether I'm doing what I'm supposed to be doing at any given moment.

Research in psychology states that we are so unaware of our own patterns and intricacies that we are prone to self-deception. Self deception is significantly damaging in the long term since our view from reality becomes more and more distorted. Our motive can become a complete mystery to us, and this is why I created this project called the TiBA - Time-tracking Behaviour Analyzer. This project allows not only the insight into bad habits, but any behavioural pattern in general so that we can be more self aware of our actions

## Table of Contents

- Overview
  - Description
  - Different Classes
  - Requirements
- Example
  - Initial Conditions
  - Instantiation
  - Behaviour Tracking
  -

### Description

This program essentially abstracts the physical actions that I do (e.g. Prepare food, watch YouTube video, Text Mom, etc.) into one whole behaviour. As input, it takes in a table of tracked time data, groups commonly clustered actions as "behaviours" and then returns a list of common behaviours that you have and their frequency

So for example, this is an example of a very common behaviour that I have every morning:

- **Behaviour 1**

  - Action: Resting (1:00 AM --> 5:47 AM)
  - Action: Washroom (5:47 AM --> 6:04 AM)
  - Action: Brushing Teeth (6:04 AM --> 6:08 AM)
  - Action: Flossing Teeth (6:08 AM --> 6:16 AM)
  - Action: Making Bed (6:16 AM --> 6:18 AM)

  These are shown in a picture below
  ![](https://github.com/haseab/TiBA/blob/master/TiBA_Getting%20Up.png)

Now that these behaviours have been abstracted into something called **Behaviour 1**, I can just rename **Behaviour 1** into something like **Morning Routine**.

### Different Classes

- TimeHandler (This class does basic getting features of the data)
  - Fetch Data -> Assuming that there are no CSV files, it will connect to your **_Toggl_** Account and grab the data from the range that you desire
