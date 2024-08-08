## Imports
import pandas as pd
import dash
from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots #for dual axes
from datetime import datetime as dt
import os

## Load Data
data = pd.read_csv("2023final.csv")
#data['time_stamp'] = pd.to_datetime(data['time_stamp'])


## Charts
def create_pm25(monitor):
    '''
    This function creates the pm2.5 scatter plot where the values above 35 are colored red and below are green.
    The monitor parameter is returned from the dropdown menu.
    '''
    #print(f'monitor is: {monitor}')
    #print(f'type monitor is: {type(monitor)}')
    # temp_df = data.loc[data['Name'] == monitor] 
    temp_df = data.query(f"Name == '{monitor}' ")
    #print(temp_df)
    threshold = 35 #EPA number

    pm25_figure = go.Figure()
    # full scatter
    pm25_figure.add_trace(
        go.Scatter(
            x=temp_df['time_stamp'],
            y=temp_df['pm2.5_alt'],
            # marker = dict(color=(temp_df['pm2.5_alt'] >= 35).astype('int'),
            #             colorscale = [[0, "green"], [1, "red"]]),
            marker = {'color': 'green'},
            mode = 'markers',
            name = 'Below EPA threshold'
        )
    ),
    # Above threshold
    pm25_figure.add_trace(
        go.Scatter(
            x=temp_df['time_stamp'],
            y=temp_df['pm2.5_alt'].where(temp_df['pm2.5_alt'] >= threshold),
            marker={'color':'red'},
            mode = 'markers',
            name = 'Above EPA threshold'
        )
    ),
    pm25_figure.update_layout(
        title='{} vs Time at {}'.format('Particulate Matter', monitor),
        xaxis_title='2023',
        yaxis_title='Amount of Particulates < 2.5 mcg',
        showlegend=True,
    )
    #Update Plot sizing
    pm25_figure.update_layout(
        width = 1000,
        height = 600,
        autosize = False,
        margin = dict(t=100, b=0, l=0, r=0),
        template = "plotly_white"
    )
    return pm25_figure

def create_temp(monitors):
    '''
    This function accepts a list of monitors from the multiselect dropdown as a parameter.
    Creates a line graph that can have multiple Temperature graphs on it.
    
    This function accepts month from dropdown as type string.
    '''

    #temp_df = data.query(f"Name == '{monitors}' ")

    if len(monitors) == 0:
        return dash.no_update
    else:
        temp_dff=data[data['Name'].isin(monitors)]
        #temp_fig = px.scatter(temp_dff, x=temp_dff['time_stamp'], y=temp_dff['temperature'], color=temp_dff['Name'])
        
        temp_figure = go.Figure()
        temp_figure = px.line(
            data_frame=temp_dff,
            x=temp_dff['time_stamp'],
            y=temp_dff['temperature'],
            labels={'time_stamp': '\nDate', 'temperature':'Temperauture (F)'}, #the keys are the df col names, not x or y for the axis names
            title='Temperature over 2023',
            markers=True,
            color=temp_dff['Name']
        )
        #Update Plot sizing
        temp_figure.update_layout(
            width = 1000,
            height = 600,
            autosize = False,
            margin = dict(t=100, b=0, l=0, r=0),
            template = "plotly_white"
        )
    return temp_figure

def create_humidity(monitor):
    '''
    This function creates a humidity and temperature graph vs time. 
    '''
    temp_df=data.query(f"Name == '{monitor}' ")

    humid_figure=go.Figure()
    humid_figure = make_subplots(specs=[[{"secondary_y": True}]])
    humid_figure.add_trace(
        go.Line(
            #data_frame=temp_df,
            x=temp_df['time_stamp'],
            y=temp_df['humidity'],
            name='Avg Relative Humidity (%)',
            #labels={'x':'Date', 'y': 'Avg Relative Humidity (%)'},
        ),
        secondary_y=True
    )
    humid_figure.add_trace(
        go.Line(
            #data_frame=temp_df,
            x=temp_df['time_stamp'],
            y=temp_df['temperature'],
            name='Temperature (F)',
        ),
        secondary_y=False
    ),
    humid_figure.update_yaxes(
        title_text='date',
        secondary_y=False,
    ),
    humid_figure.update_layout(
        title_text = 'Humidity and Temp v. Time',
        height     = 700,
        template   = 'plotly',
        legend     = dict(
            orientation ='h',
            xanchor ='center',
            x       = .5,
            yanchor = 'top',
            y       = 1.09
        )
    )
    return humid_figure


## Web App Layout
app = Dash(__name__)

app.layout = html.Div([
    html.H1( #this puts in the lcp logo
        html.A(#href="https://www.twitter.com/username",
                children=[
                    html.Img(#alt="Link to my twitter", # alt (string; optional): Alternative text in case an image can't be displayed.
                             #src="twitterlogo.png",
                             src = "https://loudounclimate.org/wp-content/uploads/2020/07/Loudoun-Climate_1.3C-228x95.png", #src (string; optional): The URL of the embeddable content.
                    )
                ]
        )        
    ),

    html.H2(id = 'airquality',
            children = "Air Quality in Loudoun County",
            style = {
                'textAlign': "center",
                'color': 'black'
            },
    ),

    # possibly put into html.Div()
    dcc.Dropdown(
        id = 'monitor_dropdown',
        #options=[{"label":str(i),"value":str(i).lower()} for i in monitors], # could loop through set of monitors from df
        options= data["Name"].unique(), # THIS IS WHAT FIXED CALLBACK ERROR???
        value = 'Lansdowne', # default value
        placeholder = "Select a monitor",
        clearable = False,
        style = {'width': '50%'},
    ),

    html.Div([
        dcc.Graph(
            id = 'pm25_scatter',
            #figure=create_pm25(monitor)
        ),
        #style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'}),
        
        dcc.Markdown(
        '''
        **What is considered high?** \n
        The EPA's 24-hour fine particle standard is 35 $µg/m^3$ . An area meets the 24-hour standard if the 
        98th percentile of 24-hour PM2.5 concentrations in one year, averaged over three years, is less than or 
        equal to 35 $μg/m^3$. In this scatter plot, the red values are the measurements for days where the PM2.5 concentrations are above 35.

        You can learn more about Particulate Matter here: [EPA website](https://www.epa.gov/pm-pollution/particulate-matter-pm-basics)
        
        Learn more about the Paticulate Matter trends nationwide: [National Trends](https://www.epa.gov/air-trends/particulate-matter-pm25-trends)
        ''',mathjax=True # this enables LaTeX i think
        ),
        html.Br(),
        html.Br(),
    ]),
    
    html.Div(
        children=[
            dcc.Dropdown(
                id='temp_dropmulti', # for temp line graph 
                options= pd.unique(data["Name"]), #data["Name"].unique(), # lsit of monitors
                value=['Lansdowne'], # needs to be list for multiselect i think. also 
                placeholder='Select monitors',
                clearable=True,
                multi=True,
            ),
            dcc.Graph(
                id = 'temp_fig',
            )],
    ),

    html.Div(
        children=[
            dcc.Dropdown(
                id='humid_drop', 
                options= pd.unique(data["Name"]), 
                value='Lansdowne', 
                placeholder='Select monitor',
                clearable=True,
            ),
            dcc.Graph(
                id='humid_fig'
            ),
        ]
    )
  
])


## Callbacks
##############################
@app.callback(
    Output(component_id='pm25_scatter', component_property='figure'), # pm2.5 scatter plot - choosing which monitor
    Input(component_id='monitor_dropdown', component_property='value')
)
def update_pm25(monitor):
    return create_pm25(monitor)

##############################    
@app.callback(
    Output(component_id='temp_fig', component_property='figure'), # pm2.5 scatter plot - choosing which monitor
    Input(component_id='temp_dropmulti', component_property='value'),
    #Input(component_id='temp_dropmulti', component_property='value')]
)
def update_temp(monitors):
    # print(monitors)
    # if len(monitors) == 0:
    #     return dash.no_update
    # else:
    #     temp_dff=data[data['Name'].isin(monitors)]
    #     temp_fig = px.scatter(temp_dff, x=temp_dff['time_stamp'], y=temp_dff['temperature'], color=temp_dff['Name'])
        
    return create_temp(monitors)#temp_fig#create_temp(monitors)

##############################
@app.callback(
    Output(component_id='humid_fig', component_property='figure'),
    Input(component_id='humid_drop', component_property='value')
)
def update_humidity(monitor):
    return create_humidity(monitor)





if __name__ == "__main__":
    app.run_server(debug=True, port=8051,jupyter_mode="external") #jupyter_mode="external" gives link to external webpage
