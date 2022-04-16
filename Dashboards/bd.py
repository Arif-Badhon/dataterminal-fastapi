import dash
import dash_core_components as dcc
import dash_html_components as html
# from dash import dcc, html
import pymongo
import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import dash_auth
import flask
import os

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

def business_dashboard(requests_pathname_prefix: str = None) -> dash.Dash:

    server = flask.Flask(__name__)
    server.secret_key = os.environ.get('secret_key', 'secret')

    app = dash.Dash(__name__, server=server, requests_pathname_prefix=requests_pathname_prefix, external_stylesheets=external_stylesheets,     meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],title='Business Dashboard')

    client = pymongo.MongoClient("mongodb+srv://Badhon:arf123bdh@dataterminal1.gc4xk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client["DATATERMINAL"]
    collection = db["Business Dashboard"]
    collection = collection.find()
    collection = pd.DataFrame(collection)
    collection.drop('_id', inplace=True, axis=1)

    sector_name = sorted(collection['Sector'].unique())

    app.layout = html.Div([
        html.Div([
            html.H1("Welcome To DATA TERMINAL", style={'textAlign':'center'}, className="app-header--title"),
            html.H6("BUSINESS DASHBOARD", style={'textAlign':'center'}, className="app-header--title")
        ]),
        html.Br(),
        html.Br(),
        html.Div([
            html.Div([html.H6("Select Sector"), dcc.Dropdown(id="Sector", options=[{'label':i, 'value': i} for i in sector_name], value='Select')], className="six columns"),
            html.Div([html.H6("Select Company"), dcc.Dropdown(id='company')], className="six columns")
        ], className='row'),
        html.Br(),
        html.Div([
            html.Div([html.H6("Select Indicator"), dcc.Dropdown(id='indicator')], className="six columns"),
            html.Div([html.H6("Select Timeline"), dcc.Dropdown(id='type')], className="six columns")
        ], className='row'),
        html.Br(),
        html.Div([
            html.Div([dcc.Graph(id='graph', figure = {}, config={"displaylogo": False, 'modeBarButtonsToRemove':['toImage', 'pan2d', 'select2d', 'lasso2d']})])
        ])
    ])

    @app.callback(
        Output('company', 'options'),
        Input('Sector', 'value'))
    def select_company(Sector):
        data = collection[collection['Sector'] == Sector]
        company = data['Company']
        return [{'label': i, 'value': i} for i in np.unique(company)]

    @app.callback(
        Output('indicator', 'options'),
        Input('Sector', 'value'),
        Input('company', 'value'))
    def select_indicator(Sector, company):
        data = collection[collection['Sector'] == Sector]
        data = data[data['Company'] == company]
        indicator = data['Indicator']
        return [{'label': i, 'value': i} for i in np.unique(indicator)]

    @app.callback(
        Output('type', 'options'),
        Input('indicator', 'value'),
        Input('Sector', 'value'),
        Input('company', 'value'))
    def select_indicator(indicator, Sector, company):
        data = collection[collection['Sector'] == Sector]
        data = data[data['Company'] == company]
        data = data[data['Indicator'] == indicator]

        CalenderYearData = data[~data['Calendar Value'].isnull()]
        BudgetYearData = data[~data['Budget Value'].isnull()]
        MonthlyData = data[~data['Year'].isnull() & data['Calendar Value'].isnull()]
        Type =[]
        if not CalenderYearData.empty:
            Type.append("Yearly")
        if not BudgetYearData.empty:
            Type.append("Budget Yearly")
        if not MonthlyData.empty:
            Type.append("Monthly")
        return [{'label': i, 'value': i} for i in Type]
    
    @app.callback(
        Output('graph', 'figure'),
        Input('type', 'value'),
        Input('indicator', 'value'),
        Input('Sector', 'value'),
        Input('company', 'value'))
    def graph_build(type, indicator, Sector, company):
        data = collection[collection['Sector'] == Sector]
        data = data[data['Company'] == company]
        data = data[data['Indicator'] == indicator]

        CalenderYearData = data[~data['Calendar Value'].isnull()]
        BudgetYearData = data[~data['Budget Value'].isnull()]
        MonthlyData = data[~data['Year'].isnull() & data['Calendar Value'].isnull()]
        
        if type == 'Yearly':
            cdata = CalenderYearData[['Year', 'Calendar Value']]
            cdata = cdata.sort_values('Year')
            cdata['Year'] = cdata['Year'].map(str)
            figure = px.bar(cdata, x='Year', y='Calendar Value', text="Calendar Value")
            figure.update_layout(title={'text':indicator + " by " + company,  'y':.93,
                'x':0.5,'xanchor':'center', 'yanchor':'top'}, xaxis_title="Source: " + str(np.unique(CalenderYearData['Source'])[0]) + "                                  " + "Unit of Measurement: " + str(np.unique(CalenderYearData['Unit'])[0]), yaxis_title="")
            for data in figure.data:
                data["width"] = 0.5
            #figure.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            #figure.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
            return figure
        elif type == 'Budget Yearly':
            cdata = BudgetYearData[['Budget Year', 'Budget Value']]
            cdata = cdata.sort_values('Budget Year')
            figure = px.bar(cdata, x='Budget Year', y='Budget Value', text="Budget Value")
            figure.update_layout(title={'text':indicator + " by " + company,  'y':0.93,
            'x':0.5,'xanchor':'center', 'yanchor':'top'}, xaxis_title="Source: " + str(np.unique(BudgetYearData['Source'])[0]) + "                                  " + "Unit of Measurement: " + str(np.unique(BudgetYearData['Unit'])[0]), yaxis_title="")
            for data in figure.data:
                data["width"] = 0.5
            return figure

        else:
            cdata = MonthlyData[["Year", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
            cdata = cdata.sort_values('Year')
            cdata['Year'] = cdata['Year'].map(str)
            Year = cdata["Year"]
            January = cdata["Jan"]
            February = cdata["Feb"]
            March = cdata["Mar"]
            April = cdata["Apr"]
            May = cdata["May"]
            June = cdata["Jun"]
            July = cdata["Jul"]
            August = cdata["Aug"]
            September = cdata["Sep"]
            October = cdata["Oct"]
            November = cdata["Nov"]
            December = cdata["Dec"]

            figure = go.Figure(data=[
                go.Bar(name='January', x=Year, y=January),
                go.Bar(name='February', x=Year, y=February),
                go.Bar(name='March', x=Year, y=March),
                go.Bar(name='April', x=Year, y=April),
                go.Bar(name='May', x=Year, y=May),
                go.Bar(name='June', x=Year, y=June),
                go.Bar(name='July', x=Year, y=July),
                go.Bar(name='August', x=Year, y=August),
                go.Bar(name='September', x=Year, y=September),
                go.Bar(name='October', x=Year, y=October),
                go.Bar(name='November', x=Year, y=November),
                go.Bar(name='December', x=Year, y=December)
            ])
            figure.update_layout(barmode='group')
            figure.update_layout(title={'text':indicator + " by " + company,  'y':0.93,
            'x':0.5,'xanchor':'center', 'yanchor':'top'}, xaxis_title="Source: " + str(np.unique(MonthlyData['Source'])[0]) + "                                  " + " Unit of Measurement: " + str(np.unique(MonthlyData['Unit'])[0]), yaxis_title="")
            return figure
    return app