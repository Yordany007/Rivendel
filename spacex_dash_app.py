# Import required libraries
import pandas as pd
import dash
from dash import dcc
#import dash_core_components as dcc
from dash import html
#import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("/home/yordany/Documents/data/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites = spacex_df["Launch Site"].unique()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                html.Div([
                                    # Create an division for adding dropdown helper text for report type
                                    html.Div(
                                        [
                                        html.H2('Launch Site:', style={'margin-right': '2em'}),
                                        ]
                                    ),
                                    # TODO2: Add a dropdown
                                    dcc.Dropdown(id='site-dropdown',
                                                      options=[
                                                         {'label': 'All Sites', 'value': 'ALL'},
                                                         {'label': launch_sites[0], 'value': launch_sites[0]},
                                                         {'label': launch_sites[1], 'value': launch_sites[1]},
                                                         {'label': launch_sites[2], 'value': launch_sites[2]},
                                                         {'label': launch_sites[3], 'value': launch_sites[3]}
                                                         ],
                                                      value='ALL',
                                                      placeholder='Select a launch site',
                                                      searchable=True,
                                                      style={'width': '80%', 'padding':'3px', 'font-size': '20px', 'textAlign': 'center'}
                                    ),
                                # Place them next to each other using the division style
                                ], style={'display':'flex'}),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000, marks={0: '0', 100: '100'}, value=[min_payload, max_payload]
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):        
    if entered_site == 'ALL':
        filtered_df = spacex_df[["Launch Site", "class"]]
        success_df = filtered_df.groupby("class").count().reset_index()
        
        fig = px.pie(success_df, values='Launch Site', names="class", title='Total success launches')
    
        return fig
    
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == str(entered_site)]
        filtered_df = filtered_df[["Launch Site", "class"]]
        success_df = filtered_df.groupby("class").count().reset_index()
        
        fig = px.pie(success_df, values='Launch Site', names="class", title='Success launches')
        
        return fig

# return the outcomes piechart for a selected site
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), 
               Input(component_id='payload-slider', component_property='value')])

def get_scatter_plot(entered_site, entered_payload):
    
    spacex_df[["Payload Mass (kg)"]] = spacex_df[["Payload Mass (kg)"]].astype("int")
    
    if entered_site == 'ALL':
        filtered_df = spacex_df[spacex_df["Payload Mass (kg)"] >= int(entered_payload[0])]
        filtered_df = filtered_df[["Launch Site", "Payload Mass (kg)", "Booster Version Category", "class"]]
        
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title='Success payload launches')
    
        return fig
    
    else:
        filtered_df = spacex_df[(spacex_df["Launch Site"] == str(entered_site)) & (spacex_df["Payload Mass (kg)"] >= int(entered_payload[0]))]
        filtered_df = filtered_df[["Launch Site", "Payload Mass (kg)", "Booster Version Category", "class"]]
        
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title='Success payload launches')
        
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
