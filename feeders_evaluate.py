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




# pull full message log in reverse order, will find latest session start
logs_all = tm1.server.get_message_log_entries(reverse=True)



sStart = ''
sEnd = ''
# find most recent model restart
for entry in logs_all:
        if entry['Message'].find('TM1 Server is ready') > -1:
            sEnd = get_time_from_tm1_timestamp(tm1_timestamp=entry['TimeStamp'])
        elif entry['Message'].find('--Session Start--') > -1:
            sStart = get_time_from_tm1_timestamp(tm1_timestamp=entry['TimeStamp'])
            break

bPass = True if sStart != '' and sEnd != '' else False

# query filtered list from log
if bPass == True:
    logs = tm1.server.get_message_log_entries(reverse=True, start=sStart, end=sEnd)

    msg_list = {}
    for entry in logs:
        if entry['Logger'] == 'TM1.Server' and 'TM1CubeImpl::ProcessFeeders' in entry['Message'] and 'Done computing feeders for base cube' in entry['Message']:
            sCube = entry['Message'][entry['Message'].find('base cube')+11:-2]
            msg_list[sCube] = round(int(entry['Message'][31:entry['Message'].find('ms)')]) * .001, 2)

    df = pd.DataFrame.from_dict(data=msg_list, orient='index', columns=['Time'])

    # show chart
    fig1 = px.bar(df.sort_values(by='Time', ascending=False).head(25))
    fig1.show()

