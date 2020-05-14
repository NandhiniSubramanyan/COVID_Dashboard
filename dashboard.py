# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 07:42:40 2020

@author: NandhiniSubramanyan
"""
#%%
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output

#%%
confirmed_global = pd.read_csv("time_series_covid19_confirmed_global.csv")
deaths_global = pd.read_csv("time_series_covid19_deaths_global.csv")
recovered_global = pd.read_csv("time_series_covid19_recovered_global.csv")
country_accumulated_confirmed = confirmed_global.groupby('Country/Region', as_index=False).sum()
country_accumulated_death = deaths_global.groupby('Country/Region', as_index=False).sum()
country_accumulated_recovered = recovered_global.groupby('Country/Region', as_index=False).sum()
final_df = country_accumulated_confirmed.iloc[:, 0:3]
final_df['Confirmed'] = country_accumulated_confirmed.iloc[:, -1]
final_df['Deaths'] = country_accumulated_death.iloc[:, -1]
final_df['Recovered'] = country_accumulated_recovered.iloc[:, -1]
final_df['Active'] = final_df['Confirmed'] - final_df['Recovered'] - final_df['Deaths']
sorted_active = final_df.drop(['Lat', 'Long'], axis=1)
sorted_active = sorted_active.sort_values(by=sorted_active.columns[-1], ascending= (False))
sorted_active_transpose = (country_accumulated_confirmed.sort_values(by=country_accumulated_confirmed.columns[-1], ascending=False)).transpose()

#%%
import plotly.express as px
import plotly.graph_objects as go
fig = go.Figure(data=go.Scattergeo(
        lon = final_df['Long'],
        lat = final_df['Lat'],
        text = final_df['Active'],
        mode = 'markers',
        marker= dict(
                opacity=0.8,
                reversescale=True,
                autocolorscale=False,
                line = dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            colorscale = 'Blues',
            cmin = 0,
            color = final_df['Confirmed'],
            cmax = final_df['Confirmed'].max(),
            colorbar_title="Confirmed cases"
                ),
        locationmode='country names',
        locations=final_df['Country/Region'],
        hovertext=final_df["Confirmed"],
        ))

fig.update_layout(
        title = 'Confirmed cases across countries',
    )

#%%
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {
    'background': '#FFFFFF',
    'text': '#7FDBFF'
}
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H4(children='COVID-19 (Global Status)',
            style={
            'textAlign': 'center',
            'color': colors['text']
        }),
    html.Div(children='Top 10 affected countries', style={
        'textAlign': 'left',
        'color': colors['text']
    }),
    dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in sorted_active.columns],
    data=sorted_active.iloc[0:10, :].to_dict('records'),
    style_cell={'textAlign': 'left',
                'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white'},
    style_header={
        'backgroundColor': 'rgb(50, 50, 50)',
        'fontWeight': 'bold'
    },
    style_data_conditional=[
            {
            'if':{'filter_query': '{Active} > 50000'},
            'backgroundColor': 'rgb(0, 0, 255)',
            'color': 'white',}]
    ),
    dcc.Graph(
            id='confirmed_cases',
        figure={
            'data': [
                {'x': sorted_active['Country/Region'][0:20], 'y': sorted_active['Confirmed'][0:20], 'type': 'bar', 'name': 'Confirmed'},
                {'x': sorted_active['Country/Region'][0:20], 'y': sorted_active['Deaths'][0:20], 'type': 'bar', 'name': 'Deaths'},
                {'x': sorted_active['Country/Region'][0:20], 'y': sorted_active['Recovered'][0:20], 'type': 'bar', 'name': 'Recovered'},
            ],
            'layout': {
                'title': 'Confirmed across countries'
            }
        }),
    dcc.Graph(
            id='world map',
            figure=fig),
    html.Table([
        html.Tr([html.Td(['Country'], style={'color' : 'blue', 'fontWeight': 'bold'}), html.Td(id='Country', style = {'color' : 'blue'})]),
        html.Tr([html.Td(['Confirmed'], style={'color' : 'orange', 'fontWeight': 'bold'}), html.Td(id='Confirmed' , style={'color' : 'orange'})]),
        html.Tr([html.Td(['Deaths'], style={'color' : 'red', 'fontWeight': 'bold'}), html.Td(id='Deaths', style={'color' : 'red'})]),
        html.Tr([html.Td(['Recovered'], style={'color' : 'green', 'fontWeight': 'bold'}), html.Td(id='Recovered', style={'color' : 'green'})]),
        html.Tr([html.Td(['Active'], style={'color' : 'purple', 'fontWeight': 'bold'}), html.Td(id='Active', style={'color' : 'purple'})]),
    ])
])

@app.callback(
[Output('Country','children'),
Output('Confirmed','children'),
Output('Deaths','children'),
Output('Recovered','children'),
Output('Active','children')],
[Input('world map', 'hoverData')]
)
def update_output_div(input_value):
    for i in input_value['points']:
        info = sorted_active[sorted_active['Country/Region'] == i['location']]
    return info['Country/Region'].values, info['Confirmed'].values, info['Deaths'].values, info['Recovered'].values, info['Active'].values
if __name__ == '__main__':
    app.run_server(debug=False, port=8051)
    
