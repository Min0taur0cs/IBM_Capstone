# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# TASK 1: Add a dropdown list to enable Launch Site selection
# The default select value is for ALL sites
# Define the layout within an html.Div
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 50}),
    # Task 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                 ],
                 value='ALL',  # Default value
                 placeholder="Select a Launch Site",
                 searchable=True  # Enable search
                 ),
    html.Br(),

    # Add a label for the payload slider
    html.P("Select Payload Mass (kg):", style={'textAlign': 'center'}),
    dcc.RangeSlider(
     id='payload-slider',
     min=0,
     max=10000,
     step=1000,
     marks={0: '0', 10000: '10000'},
     value=[min_payload, max_payload]
    ),

    # Placeholder for the pie chart component
    dcc.Graph(id='success-pie-chart', style={'border': '1px solid blue'}),

    # Placeholder for the scatter chart component
    dcc.Graph(id='success-payload-scatter-chart', style={'border': '1px solid blue'}),

    # Placeholder for the markdown component and text divs
    dcc.Markdown(id='answer-placeholder', style={'color': '#503D36', 'font-size': 16, 'textAlign': 'center'}),
    # Add border to each text element
    html.Div(id='best-site-success-text', children="Best Site Success % = (KSC LC-39A) 0.77%", style={'border': '1px solid green', 'padding': '5px'}),
    html.Div(id='best-site-text', children="Best Site = KSC LC-39A", style={'border': '1px solid green', 'padding': '5px'}),
    html.Div(id='best-payload-range-success-text', children="Best Payload Range Success = 362.00 to 9600.00", style={'border': '1px solid green', 'padding': '5px'}),
    html.Div(id='worst-payload-range-success-text', children="Worst Payload Range Success = 500.00 to 9600.00", style={'border': '1px solid green', 'padding': '5px'}),
    html.Div(id='best-booster-version-text', children="Best Booster Version = B5", style={'border': '1px solid green', 'padding': '5px'}),


], style={'border': '2px solid black', 'padding': '10px'})  # Border for the entire dashboard

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output('success-pie-chart', 'figure'),
              Input('site-dropdown', 'value'))
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Calculate the count of successful and failed launches for all sites
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='Success')
        failure_counts = spacex_df[spacex_df['class'] == 0].groupby('Launch Site').size().reset_index(name='Failure')

        # Merge the success and failure counts
        merged_counts = pd.merge(success_counts, failure_counts, on='Launch Site', how='outer').fillna(0)

        # Calculate the success rate for each site
        merged_counts['Success Rate'] = (merged_counts['Success'] / (merged_counts['Success'] + merged_counts['Failure'])) * 100

        # Create a pie chart showing the success rate for all sites
        fig = px.pie(merged_counts, names='Launch Site', values='Success Rate',
                     title='Success Rate for All Sites')
    else:
        # Calculate the count of successful launches (class = 1) for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_count = filtered_df[filtered_df['class'] == 1]['class'].count()
        failure_count = filtered_df[filtered_df['class'] == 0]['class'].count()

        # Calculate the success rate for the selected site
        success_rate = (success_count / (success_count + failure_count)) * 100

        # Create a pie chart showing the success rate for the selected site
        fig = px.pie(names=['Success', 'Failure'], values=[success_rate, 100 - success_rate],
                     title=f'Success Rate at {selected_site}')

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output('success-payload-scatter-chart', 'figure'),
              [Input('site-dropdown', 'value'),
               Input('payload-slider', 'value')])
def update_scatter_chart(selected_site, selected_payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= selected_payload_range[1])]
        title = f'Successful Launches by Payload Mass (All Sites)'
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == selected_site) &
                                (spacex_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= selected_payload_range[1])]
        title = f'Successful Launches by Payload Mass at {selected_site}'

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title=title,
                     labels={'class': 'Success'})
    return fig

# Callback to answer the question

@app.callback([Output('best-site-success-text', 'children'),
               Output('best-site-text', 'children'),
               Output('best-payload-range-success-text', 'children'),
               Output('worst-payload-range-success-text', 'children'),
               Output('best-booster-version-text', 'children')],
              [Input('site-dropdown', 'value')])
def answer_question(selected_site):
    if selected_site == 'ALL':
        # Calculate the success rate for each launch site
        site_success_rate = spacex_df.groupby('Launch Site')['class'].mean()
        success_rate = site_success_rate.max()
        best_sites = site_success_rate[site_success_rate == success_rate].index
        best_site = ', '.join(best_sites)

        # Filter DataFrame for successful launches and get the payloads, excluding 0
        successful_launches = spacex_df[(spacex_df['class'] == 1) & (spacex_df['Payload Mass (kg)'] > 0)]
        best_payload_range_successful = f"{successful_launches['Payload Mass (kg)'].min():.2f} to {successful_launches['Payload Mass (kg)'].max():.2f}"

        # Filter DataFrame for failed launches and get the payloads, excluding 0
        failed_launches = spacex_df[(spacex_df['class'] == 0) & (spacex_df['Payload Mass (kg)'] > 0)]
        worst_payload_range_failed = f"{failed_launches['Payload Mass (kg)'].min():.2f} to {failed_launches['Payload Mass (kg)'].max():.2f}"

        # Calculate the best booster version
        best_booster_version = spacex_df.groupby('Booster Version Category')['class'].mean().idxmax()

        return f"Best Site Success % = ({best_site}) {success_rate:.2f}%", \
               f"Best Site = {best_site}", \
               f"Best Payload Range Success = {best_payload_range_successful}", \
               f"Worst Payload Range Success = {worst_payload_range_failed}", \
               f"Best Booster Version = {best_booster_version}"
    else:
        return '', '', '', '', ''

#====================================================

if __name__ == '__main__':
    app.run_server(debug=True)
    