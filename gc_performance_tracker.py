##
## Python program will run on selection
##
## Author: Florian Lungu
## Contact: florian@agourasoftware.com
##
## 06-Apr-2020 initial creation
##
import numpy as np
import plotly
import plotly.graph_objs as go
import tempfile
import pathlib
import pandas as pd
import dateutil
import datetime
from datetime import date, timedelta, datetime
import csv

# Title 
athlete = GC.athlete()
athleteName = athlete['name']
chartTitle = "Performance Tracker: " + athleteName
chartSubTitle = "Chart displaying maximum monthly value of: "

# Time range in seconds (edit this)
ctlDays = 42
timeRanges = 1, 1200, 600, 300, 60, 10, 1
fieldNames = ['CTL', '20min Pwr', '10min Pwr', '5min Pwr', '1min Pwr', '10sec Pwr', '1sec Pwr']

# Chart settings
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July','August', 'September', 'October', 'November', 'December']
colors = ['#ff46ac', '#ffa4fd', '#4389ff', '#3ab6ff', '#6688bd', '#a7b96d', 'greenyellow', '#339900', '#d44fd0', '#b358ff']

# Query data
print('py chart code start')
fig = go.Figure()
# query gc for each time range
for i in range(len(fieldNames)):
	if fieldNames[i] == 'CTL':
		dataQ = GC.seasonPeaks(series="power", duration=1) 
		dataZ = GC.seasonMetrics(all=True, filter="", compare=False)
		startDate = dataZ['date'][0]
		ctlDates = []
		ctlDateTimes = []
		ctlVals = []
		tssVals = []
		today = date.today()
		while startDate < today:	
			tssVals.append(0)	
			ctlVals.append(0)
			ctlDates.append(startDate)
			dt = datetime.combine(startDate, datetime.min.time())
			ctlDateTimes.append(dt)
			startDate = startDate + timedelta(days=1)
			
		for j in range(len(dataZ['date'])):
			for k in range(len(ctlDates)):
				if dataZ['date'][j] == ctlDates[k]:
					tssVals[k] += dataZ['BikeStress'][j]
		ctlY = 0
		for k in range(len(ctlDates)):
			ctlVals[k] = ctlY + (tssVals[k] - ctlY)/ctlDays
			ctlY = ctlVals[k]							
			
		dataQ = {'datetime': ctlDateTimes, 'ctl': ctlVals} 
				
	else:
		dataQ = GC.seasonPeaks(series="power", duration=timeRanges[i])
	
	df = pd.DataFrame(dataQ)
	df.columns = ['datetime','maxval']
	df['maxval'] = df['maxval'].round(0)
	df['maxval'] = df['maxval'].astype(int)
	df['maxval'] = df['maxval'].replace({0:np.nan})
	df.index = df['datetime'] 

	df['year'] = pd.DatetimeIndex(df['datetime']).year
	df['month'] = pd.DatetimeIndex(df['datetime']).strftime('%B')
	df['year'] = df['year'].astype(str)
	df['month'] = df['month'].astype(str)
	df['month_year'] = df['month'] + " - " + df['year']

	# set monthly bests
	resultSet = df.resample('M').max()
	resultSet.set_index(['month_year'])
	df_pivoted = resultSet.pivot(index='month', columns='year', values='maxval').reindex(months)

	# Create and style traces
	tColumns = df_pivoted.columns
	y = 0
	z = 0

	for colName in reversed(tColumns):
		fig.add_trace(go.Scatter(visible=False, x=months, y=df_pivoted[colName], name=colName, line=dict(color=colors[z], width=3)))
		y += 1
		z = y
		if y == len(colors):
			z = 0

# Make 1st trace group visible
for j in range(len(df_pivoted.columns)):
	fig.data[j].visible = True

# Edit the layout
fig.update_layout(title=chartTitle, xaxis_title='Month', yaxis_title='Watts', plot_bgcolor='#343434', paper_bgcolor='#343434', xaxis_gridcolor='rgba(0,0,0,0)', yaxis_gridcolor='#5e5e5e', font_color='white')

# Create and add slider
steps = []
for i in range(len(fieldNames)):
	step = dict(method="restyle", args=["visible", [False] * len(fig.data)], label=fieldNames[i])
	for j in range(len(df_pivoted.columns)):
		step["args"][1][len(df_pivoted.columns)*i+j] = True
	steps.append(step)

sliders = [dict(active=0, currentvalue={"prefix": chartSubTitle}, pad={"t": 50}, steps=steps)]
fig.update_layout(sliders=sliders)

# Define temporary file
temp_file = tempfile.NamedTemporaryFile(mode="w+t", prefix="GC_", suffix=".html", delete=False)

# Prepare plot
plotly.offline.plot({"data": fig}, auto_open = False, filename=temp_file.name)

# Load plot
GC.webpage(pathlib.Path(temp_file.name).as_uri())

print('py chart code success') 

