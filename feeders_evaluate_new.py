# initial setup
from TM1py.Services import TM1Service

from datetime import date, time, datetime, timedelta
import plotly.express as px
import pandas as pd


# connect to environment
tm1 = TM1Service([your parameters here])


# Time magic with python ~from TM1Py sample
def get_time_from_tm1_timestamp(tm1_timestamp):
    f = lambda x: int(x) if x else 0
    year = f(tm1_timestamp[0:4])
    month = f(tm1_timestamp[5:7])
    day = f(tm1_timestamp[8:10])
    hour = f(tm1_timestamp[11:13])
    minute = f(tm1_timestamp[14:16])
    second = f(tm1_timestamp[17:19])
    return datetime.combine(date(year, month, day), time(hour, minute, second))


# pull latest server restart timestamps from message log using new filter for get_mesage_log_entries
logs_start = vEnv.server.get_message_log_entries(reverse=True, msg_contains='--Session Start--', top=1)
logs_end = vEnv.server.get_message_log_entries(reverse=True, msg_contains='TM1 Server is ready', top=1)

sEnd = get_time_from_tm1_timestamp(tm1_timestamp=logs_end[0]['TimeStamp'])
sStart = get_time_from_tm1_timestamp(tm1_timestamp=logs_start[0]['TimeStamp'])

bPass = True if sStart != '' and sEnd != '' else False

# query filtered list from log
if bPass == True:
    logs = vEnv.server.get_message_log_entries(reverse=True, start=sStart, end=sEnd, msg_contains='Done computing feeders')

    msg_list = {}
    for entry in logs:
        sCube = entry['Message'][entry['Message'].find('base cube')+11:-2]
        msg_list[sCube] = round((int(entry['Message'][31:entry['Message'].find('ms)')]) * .001) / 60, 2)

    df = pd.DataFrame.from_dict(data=msg_list, orient='index', columns=['Minutes'])

    # show chart
    fig1 = px.bar(df.sort_values(by='Minutes', ascending=False).head(25))
    fig1.show()
