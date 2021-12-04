# Import required libraries
import pandas as pd
import numpy as np
import dash
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


# file rotating handler
rotatingHandler = logging.handlers.RotatingFileHandler(filename=os.path.join(os.path.dirname(os.path.realpath(__file__)),"spacex_dash_app.log"), maxBytes=100000, backupCount=5)
rotatingHandler.setLevel(logging.INFO)

# stdout handler
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(logging.INFO)

logging.basicConfig(handlers=[
                        rotatingHandler,
                        consoleHandler
                    ], format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                options=[
                                    {'label': 'All Sites', 'value': 'ALL'},
                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'}
                                ],
                                value='ALL',
                                placeholder="place holder here",
                                searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                min=0, max=10000, step=1000,
                                marks={0: '0',
                                       2500: '2500',
                                       5000: '5000',
                                       7500: '7500',
                                       10000: '10000'
                                       },
                                value=[0, 10000]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output('success-pie-chart', 'figure'),
              [Input('site-dropdown', 'value')])
def get_pie_chart(entered_site):
    filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    app.logger.info("entered site: " + str(entered_site))
    print("entered site: " + str(entered_site))
    if entered_site == 'ALL':
        fig_all = px.pie(spacex_df, values='class', 
        names='Launch Site', 
        title='Total Success Launches By Site')
        return fig_all
    else:
        filtered_df = filtered_df.groupby(['class']).size().reset_index(name='counts')
        fig_site = px.pie(filtered_df, values='counts',  
        names='class', 
        title='Total Success Launches for site ' + str(entered_site))
        return fig_site
        # return the outcomes piechart for a selected site
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output('success-payload-scatter-chart', 'figure'),
             [Input('site-dropdown', 'value'), Input("payload-slider", "value")])
def get_scatter_plot_chart(entered_site,payload_value):
    filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_value[0]) & (filtered_df['Payload Mass (kg)'] <= payload_value[-1])]
    app.logger.info("entered site: " + str(entered_site))
    print("entered site: " + str(entered_site))
    print("range slider value:" + str(payload_value))
    if entered_site == 'ALL':
        spacex_rg_filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_value[0]) & (spacex_df['Payload Mass (kg)'] <= payload_value[-1])]
        fig = px.scatter(spacex_rg_filtered_df, 
                         x=spacex_rg_filtered_df['Payload Mass (kg)'], 
                         y=spacex_rg_filtered_df['class'], 
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for all Sites')
        return fig
    else:
        fig = px.scatter(filtered_df, 
                         x=filtered_df['Payload Mass (kg)'], 
                         y=filtered_df['class'], 
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for ' + str(entered_site))
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port=8080,host='0.0.0.0',debug=True)
    app.logger.info("app started")
