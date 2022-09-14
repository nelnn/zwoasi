import matplotlib.pyplot as plt
import matplotlib.dates as md
import pandas as pd
import dateutil
import sys
df = pd.read_csv('data1.csv', names=["location","datetime","sqm","pixel","exposure","gain","interval"], index_col="datetime", parse_dates=True)
df = df.drop(["interval"],axis=1)
df["sqm"] = df["sqm"].apply(pd.to_numeric, errors='coerce')
df = df.dropna(subset=['sqm'])
df[df["location"] == 'hkspm'] 
df["sqm_1hr"] = df["sqm"].rolling('1h').mean()
plt.plot(df.index, df.sqm_1hr)
plt.xlabel("Datetime")
plt.ylabel("sqm value")
plt.title("sqm value hourly average")
plt.grid(which='minor',alpha=0.2)
plt.show()
sys.exit()
datetimestrings = df.datetime
datetime = [dateutil.parser.parse(s) for s in datetimestrings]


sqm_value = df.sqm
plt.subplots_adjust(bottom=0.2)
plt.xticks( rotation=25 )

ax=plt.gca()
ax.set_xticks(datetime)
xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
ax.xaxis.set_major_formatter(xfmt)
ax.xaxis.set_major_locator(md.DayLocator(interval = 1))
ax.set_title('SQM value')
plt.plot(datetime,sqm_value, "-")
plt.show()

