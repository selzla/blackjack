import plotly.offline as offline
import plotly.express as px
import plotly.graph_objs as go

import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from blackjack import Blackjack
import pandas as pd
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.P("""
    This is a blackjack simulator. Using basic strategy (deviations based off count coming later), the server will play a number of rounds of blackjack and record the
    total money earned over time. It will repeat this process for a number of playing sessions, and the results of all the sessions will be shown in the following charts
    and stats. Parameters you can change are the number of decks, the count system (will add custom counting system feature later), the number of rounds per session,
    the number of sessions, and the amount to bet for each case of the value of the current true count. Keep in mind that the time it takes to load the result is
    proportional to the total amount of rounds (rounds per session times the number of sessions). If this value is above 2000000, the number of sessions will be adjusted
    so that the total amount of rounds is equal to 2000000. The maximum plays per session is 2000000, and the maximum number of sessions is 1000. If a higher number
    than these values is entered, it will adjust to its corresponding maximum value.
    """),
    html.Div([
        html.Div([
            html.H6('Number of Decks'),
            dcc.Dropdown(
                id='n_decks',
                options=[{'label': i, 'value': i} for i in range(1,7)],
                value='1'
            )], style={'left':'0%', 'position':'absolute'}),
        html.Div([
            html.H6('Count System'),
            dcc.Dropdown(
                id='count_system',
                options=[{'label': 'highlow', 'value': 'highlow'}],
                value='highlow'
            )], style={'left':'15%', 'position':'absolute'}),
        html.Div([
            html.H6('Rounds Per Session'),
            dcc.Input(
                id='plays_per_session',
                type='number',
                value=1000
            )], style={'left':'28%', 'position':'absolute'}),
        html.Div([
            html.H6('Number of Sessions'),
            dcc.Input(
                id='number_of_sessions',
                type='number',
                value=20
            )], style={'left':'45%', 'position':'absolute'}),
        ], style={'top':'20%','position':'absolute', 'width':'100%'}),
    html.Div([
        html.Div([
            html.H6('True Count < 1'),
            dcc.Input(
                id='true_count < 1',
                type='number',
                value=1
            )], style={'left':'0%', 'position':'absolute'}),
        html.Div([
            html.H6('1 < True Count < 3'),
            dcc.Input(
                id='1 < true_count < 3',
                type='number',
                value=1
            )], style={'left':'17%', 'position':'absolute'}),
        html.Div([
            html.H6('3 < True Count < 5'),
            dcc.Input(
                id='3 < true_count < 5',
                type='number',
                value=1
            )], style={'left':'34%', 'position':'absolute'}),
        html.Div([
            html.H6('5 < True Count < 7'),
            dcc.Input(
                id='5 < true_count < 7',
                type='number',
                value=1
            )], style={'left':'51%', 'position':'absolute'}),
        html.Div([
            html.H6('True Count > 7'),
            dcc.Input(
                id='true_count > 7',
                type='number',
                value=1
            )], style={'left':'68%', 'position':'absolute'})
        ], style={'top':'30%','position':'absolute', 'width':'100%'}),
    html.Div([
        html.Button(id='submit-button', n_clicks=0, children='Submit'),
    ], style={'top':'42%','position':'absolute'}),
    html.Div([
        dcc.Graph(id='indicator-graphic'),
        dcc.Graph(id='overall-hist')
    ], style={'top':'50%','position':'absolute', 'width':'100%'}),
    html.Div([
        html.Div([
            html.Table([
                html.Tr('Stats'),
                html.Tr([html.Td('Overall'), html.Td('')]),
                html.Tr([html.Td('Mean of final values'), html.Td(id='mean_fv')]),
                html.Tr([html.Td('Stdev of final values'), html.Td(id='std_fv')]),
                html.Tr([html.Td('Stdev of mean final values'), html.Td(id='std_mean_fv')]),
                html.Tr([html.Td('Mean winnings per round'), html.Td(id='mean_wpr')]),
                html.Tr([html.Td('Stdev winnings per round'), html.Td(id='std_wpr')]),
                html.Tr([html.Td('Stdev of mean winnings per round'), html.Td(id='std_mean_wpr')]),
            ])
        ], style={'top':'0%', 'left':'0%', 'width':'18%', 'position':'absolute'}),
        html.Div([
            html.Table([
                html.Tr([html.Td('True Count < 1'), html.Td('')]),
                html.Tr([html.Td('Mean winnings per round'), html.Td(id='mean_wpr1')]),
                html.Tr([html.Td('Stdev winnings per round'), html.Td(id='std_wpr1')]),
                html.Tr([html.Td('Stdev of mean winnings per round'), html.Td(id='std_mean_wpr1')]),
            ])
        ], style={'top':'0%', 'left':'20%', 'width':'14%', 'position':'absolute'}),
        html.Div([
            html.Table([
                html.Tr([html.Td('1 < True Count < 3'), html.Td('')]),
                html.Tr([html.Td('Mean winnings per round'), html.Td(id='mean_wpr2')]),
                html.Tr([html.Td('Stdev winnings per round'), html.Td(id='std_wpr2')]),
                html.Tr([html.Td('Stdev of mean winnings per round'), html.Td(id='std_mean_wpr2')]),
            ])
        ], style={'top':'0%', 'left':'36%', 'width':'14%', 'position':'absolute'}),
        html.Div([
            html.Table([
                html.Tr([html.Td('3 < True Count < 5'), html.Td('')]),
                html.Tr([html.Td('Mean winnings per round'), html.Td(id='mean_wpr3')]),
                html.Tr([html.Td('Stdev winnings per round'), html.Td(id='std_wpr3')]),
                html.Tr([html.Td('Stdev of mean winnings per round'), html.Td(id='std_mean_wpr3')]),
            ])
        ], style={'top':'0%', 'left':'52%', 'width':'14%', 'position':'absolute'}),
        html.Div([
            html.Table([
                html.Tr('5 < True Count < 7'),
                html.Tr([html.Td('Mean winnings per round'), html.Td(id='mean_wpr4')]),
                html.Tr([html.Td('Stdev winnings per round'), html.Td(id='std_wpr4')]),
                html.Tr([html.Td('Stdev of mean winnings per round'), html.Td(id='std_mean_wpr4')]),
            ])
        ], style={'top':'0%', 'left':'68%', 'width':'14%', 'position':'absolute'}),
        html.Div([
            html.Table([
                html.Tr([html.Td('True Count > 7'), html.Td('')]),
                html.Tr([html.Td('Mean winnings per round'), html.Td(id='mean_wpr5')]),
                html.Tr([html.Td('Stdev winnings per round'), html.Td(id='std_wpr5')]),
                html.Tr([html.Td('Stdev of mean winnings per round'), html.Td(id='std_mean_wpr5')]),
            ])
        ], style={'top':'0%', 'left':'84%', 'width':'14%', 'position':'absolute'}),
    ], style={'top':'155%','position':'absolute', 'width':'100%'}),
    # html.Div([
    #     dcc.Graph(id='overall-hist')
    # ], style={'top':'70%','position':'absolute','width':'100%'})
])

@app.callback(
    [Output('indicator-graphic', 'figure'),
    Output('overall-hist', 'figure'),
    Output('mean_fv', 'children'),
    Output('std_fv', 'children'),
    Output('std_mean_fv', 'children'),
    Output('mean_wpr', 'children'),
    Output('std_wpr', 'children'),
    Output('std_mean_wpr', 'children'),
    Output('mean_wpr1', 'children'),
    Output('std_wpr1', 'children'),
    Output('std_mean_wpr1', 'children'),
    Output('mean_wpr2', 'children'),
    Output('std_wpr2', 'children'),
    Output('std_mean_wpr2', 'children'),
    Output('mean_wpr3', 'children'),
    Output('std_wpr3', 'children'),
    Output('std_mean_wpr3', 'children'),
    Output('mean_wpr4', 'children'),
    Output('std_wpr4', 'children'),
    Output('std_mean_wpr4', 'children'),
    Output('mean_wpr5', 'children'),
    Output('std_wpr5', 'children'),
    Output('std_mean_wpr5', 'children'),
    ],
    [Input('submit-button', 'n_clicks'),
     # Input('n_decks', 'value'),
     # Input('count_system', 'value'),
     # Input('plays_per_session', 'value'),
     # Input('number_of_sessions', 'value'),
     # Input('true_count < 1', 'value'),
     # Input('1 < true_count < 3', 'value'),
     # Input('3 < true_count < 5', 'value'),
     # Input('5 < true_count < 7', 'value'),
     # Input('true_count > 7', 'value'),
     ],
    [State('n_decks', 'value'),
     State('count_system', 'value'),
     State('plays_per_session', 'value'),
     State('number_of_sessions', 'value'),
     State('true_count < 1', 'value'),
     State('1 < true_count < 3', 'value'),
     State('3 < true_count < 5', 'value'),
     State('5 < true_count < 7', 'value'),
     State('true_count > 7', 'value'),
     ])
def update_fig(n_clicks, n_decks, count_system, plays_per_session, number_of_sessions,
               count1, count2, count3, count4, count5):
    if plays_per_session == 0:
        plays_per_session = 1
    if number_of_sessions == 0:
        number_of_sessions = 1
    if plays_per_session > 2000000:
        plays_per_session = 2000000
    if number_of_sessions > 1000:
        number_of_sessions = 1000
    if plays_per_session * number_of_sessions > 2000000:
        plays_per_session = int(2000000/number_of_sessions)
    bjack = Blackjack(n_decks = int(n_decks))
    ncards = len(bjack.deck)
    bjack.load_rules('rules.csv')
    portfolios = []
    end_vals = []
    changes = []
    changes_1 = []
    changes_2 = []
    changes_3 = []
    changes_4 = []
    changes_5 = []
    for i in range(int(number_of_sessions)):
        bjack.reset_deck()
        bjack.money = 0
        money = [0]
        for i in range(int(plays_per_session)):
            true_count = bjack.count / (bjack.n_decks * (ncards - bjack.dealt_cards) / ncards)
            try:
                if true_count < 1:
                    bjack.play_round(bet=float(count1))
                    changes_1.append(bjack.money - money[-1])
                elif true_count < 3:
                    bjack.play_round(bet=float(count2))
                    changes_2.append(bjack.money - money[-1])
                elif true_count < 5:
                    bjack.play_round(bet=float(count3))
                    changes_3.append(bjack.money - money[-1])
                elif true_count < 7:
                    bjack.play_round(bet=float(count4))
                    changes_4.append(bjack.money - money[-1])
                else:
                    bjack.play_round(bet=float(count5))
                    changes_5.append(bjack.money - money[-1])
            except IndexError:
                bjack.reset_deck()
            # print(bjack.player_hand, bjack.excess_hands, bjack.dealer_hand, bjack.money)
            # print()
            money.append(bjack.money)
            changes.append(money[-1] - money[-2])
            if len(bjack.deck) < ncards / 3:
                bjack.reset_deck()
        portfolios.append(money)
        end_vals.append(money[-1])
    ######STATS#########
    mean_fv = np.mean(np.array(end_vals))
    std_fv = np.std(np.array(end_vals))
    std_mean_fv = std_fv / np.sqrt(len(end_vals))
    changes = np.array(changes)
    mean_wpr = np.mean(changes)
    std_wpr = np.std(changes)
    std_mean_wpr = std_wpr / np.sqrt(len(changes))

    mean_wpr1 = np.mean(changes_1)
    std_wpr1 = np.std(changes_1)
    std_mean_wpr1 = std_wpr1 / np.sqrt(len(changes_1))

    mean_wpr2 = np.mean(changes_2)
    std_wpr2 = np.std(changes_2)
    std_mean_wpr2 = std_wpr2 / np.sqrt(len(changes_2))

    mean_wpr3 = np.mean(changes_3)
    std_wpr3 = np.std(changes_3)
    std_mean_wpr3 = std_wpr3 / np.sqrt(len(changes_3))

    mean_wpr4 = np.mean(changes_4)
    std_wpr4 = np.std(changes_4)
    std_mean_wpr4 = std_wpr4 / np.sqrt(len(changes_4))

    mean_wpr5 = np.mean(changes_5)
    std_wpr5 = np.std(changes_5)
    std_mean_wpr5 = std_wpr / np.sqrt(len(changes_5))
    fig = go.Figure()
    for money in portfolios:
        fig.add_trace(go.Scatter(x=np.arange(int(plays_per_session)), y=np.array(money), mode='lines'))
    fig.update_layout(title='Amount of Money Over Many Rounds for Different Sessions',
                   xaxis_title='Number of Rounds',
                   yaxis_title='Total Money',
                   showlegend=False)
    bins = int(np.sqrt(len(end_vals)))
    fig2 = go.Figure(data=go.Histogram(x=np.array(end_vals), xbins=dict( # bins used for histogram
        start=min(end_vals),
        end=max(end_vals),
        size=(max(end_vals) - min(end_vals)) // bins
    ),))
    fig2.update_layout(title='Distribution Over All Sessions of Final Money Values',
                   xaxis_title='Final Money Value',
                   yaxis_title='Counts')
    return fig, fig2, round(mean_fv,5), round(std_fv,5), round(std_mean_fv,5), round(mean_wpr,5), round(std_wpr,5), round(std_mean_wpr,5), round(mean_wpr1,5), round(std_wpr1,5), round(std_mean_wpr1,5), round(mean_wpr2,5), round(std_wpr2,5), round(std_mean_wpr2,5), round(mean_wpr3,5), round(std_wpr3,5), round(std_mean_wpr3,5), round(mean_wpr4,5), round(std_wpr4,5), round(std_mean_wpr4,5), round(mean_wpr5,5), round(std_wpr5,5), round(std_mean_wpr5,5)

server = app.server

if __name__ == '__main__':

    app.run_server(debug=True)
