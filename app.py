# Import required libraries
import os
import datetime as dt

import numpy as np
import pandas as pd
import plotly.plotly as py
import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

from data_fetcher import get_time_delta, get_raw_data, get_filtered_data


# Setup app
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(__name__, server=server, url_base_pathname='/dash/gallery/volatility-surface', csrf_protect=False)

external_css = ["https://fonts.googleapis.com/css?family=Overpass:300,300i",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/dab6f937fd5548cebf4c6dc7e93a10ac438f5efb/dash-technical-charting.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


# Tickers
sp500 = ['AAPL', 'ABT', 'ABBV', 'ACN', 'ACE', 'ADBE', 'ADT', 'AAP', 'AES',
         'AET', 'AFL', 'AMG', 'A', 'GAS', 'ARE', 'APD', 'AKAM', 'AA', 'AGN',
         'ALXN', 'ALLE', 'ADS', 'ALL', 'ALTR', 'MO', 'AMZN', 'AEE', 'AAL',
         'AEP', 'AXP', 'AIG', 'AMT', 'AMP', 'ABC', 'AME', 'AMGN', 'APH', 'APC',
         'ADI', 'AON', 'APA', 'AIV', 'AMAT', 'ADM', 'AIZ', 'T', 'ADSK', 'ADP',
         'AN', 'AZO', 'AVGO', 'AVB', 'AVY', 'BHI', 'BLL', 'BAC', 'BK', 'BCR',
         'BXLT', 'BAX', 'BBT', 'BDX', 'BBBY', 'BRK.B', 'BBY', 'BLX', 'HRB',
         'BA', 'BWA', 'BXP', 'BSX', 'BMY', 'BRCM', 'BF.B', 'CHRW', 'CA',
         'CVC', 'COG', 'CAM', 'CPB', 'COF', 'CAH', 'HSIC', 'KMX', 'CCL',
         'CAT', 'CBG', 'CBS', 'CELG', 'CNP', 'CTL', 'CERN', 'CF', 'SCHW',
         'CHK', 'CVX', 'CMG', 'CB', 'CI', 'XEC', 'CINF', 'CTAS', 'CSCO', 'C',
         'CTXS', 'CLX', 'CME', 'CMS', 'COH', 'KO', 'CCE', 'CTSH', 'CL',
         'CMCSA', 'CMA', 'CSC', 'CAG', 'COP', 'CNX', 'ED', 'STZ', 'GLW',
         'COST', 'CCI', 'CSX', 'CMI', 'CVS', 'DHI', 'DHR', 'DRI', 'DVA',
         'DE', 'DLPH', 'DAL', 'XRAY', 'DVN', 'DO', 'DTV', 'DFS', 'DISCA',
         'DISCK', 'DG', 'DLTR', 'D', 'DOV', 'DOW', 'DPS', 'DTE', 'DD', 'DUK',
         'DNB', 'ETFC', 'EMN', 'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA',
         'EMC', 'EMR', 'ENDP', 'ESV', 'ETR', 'EOG', 'EQT', 'EFX', 'EQIX',
         'EQR', 'ESS', 'EL', 'ES', 'EXC', 'EXPE', 'EXPD', 'ESRX', 'XOM',
         'FFIV', 'FB', 'FAST', 'FDX', 'FIS', 'FITB', 'FSLR', 'FE', 'FISV',
         'FLIR', 'FLS', 'FLR', 'FMC', 'FTI', 'F', 'FOSL', 'BEN', 'FCX',
         'FTR', 'GME', 'GPS', 'GRMN', 'GD', 'GE', 'GGP', 'GIS', 'GM',
         'GPC', 'GNW', 'GILD', 'GS', 'GT', 'GOOGL', 'GOOG', 'GWW', 'HAL',
         'HBI', 'HOG', 'HAR', 'HRS', 'HIG', 'HAS', 'HCA', 'HCP', 'HCN',
         'HP', 'HES', 'HPQ', 'HD', 'HON', 'HRL', 'HSP', 'HST', 'HCBK',
         'HUM', 'HBAN', 'ITW', 'IR', 'INTC', 'ICE', 'IBM', 'IP', 'IPG',
         'IFF', 'INTU', 'ISRG', 'IVZ', 'IRM', 'JEC', 'JBHT', 'JNJ',
         'JCI', 'JOY', 'JPM', 'JNPR', 'KSU', 'K', 'KEY', 'GMCR', 'KMB',
         'KIM', 'KMI', 'KLAC', 'KSS', 'KRFT', 'KR', 'LB', 'LLL', 'LH',
         'LRCX', 'LM', 'LEG', 'LEN', 'LVLT', 'LUK', 'LLY', 'LNC', 'LLTC',
         'LMT', 'L', 'LOW', 'LYB', 'MTB', 'MAC', 'M', 'MNK', 'MRO', 'MPC',
         'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MAT', 'MKC', 'MCD', 'MCK',
         'MJN', 'MMV', 'MDT', 'MRK', 'MET', 'KORS', 'MCHP', 'MU', 'MSFT',
         'MHK', 'TAP', 'MDLZ', 'MON', 'MNST', 'MCO', 'MS', 'MOS', 'MSI',
         'MUR', 'MYL', 'NDAQ', 'NOV', 'NAVI', 'NTAP', 'NFLX', 'NWL',
         'NFX', 'NEM', 'NWSA', 'NEE', 'NLSN', 'NKE', 'NI', 'NE', 'NBL',
         'JWN', 'NSC', 'NTRS', 'NOC', 'NRG', 'NUE', 'NVDA', 'ORLY',
         'OXY', 'OMC', 'OKE', 'ORCL', 'OI', 'PCAR', 'PLL', 'PH', 'PDCO',
         'PAYX', 'PNR', 'PBCT', 'POM', 'PEP', 'PKI', 'PRGO', 'PFE',
         'PCG', 'PM', 'PSX', 'PNW', 'PXD', 'PBI', 'PCL', 'PNC', 'RL',
         'PPG', 'PPL', 'PX', 'PCP', 'PCLN', 'PFG', 'PG', 'PGR', 'PLD',
         'PRU', 'PEG', 'PSA', 'PHM', 'PVH', 'QRVO', 'PWR', 'QCOM',
         'DGX', 'RRC', 'RTN', 'O', 'RHT', 'REGN', 'RF', 'RSG', 'RAI',
         'RHI', 'ROK', 'COL', 'ROP', 'ROST', 'RLD', 'R', 'CRM', 'SNDK',
         'SCG', 'SLB', 'SNI', 'STX', 'SEE', 'SRE', 'SHW', 'SPG', 'SWKS',
         'SLG', 'SJM', 'SNA', 'SO', 'LUV', 'SWN', 'SE', 'STJ', 'SWK',
         'SPLS', 'SBUX', 'HOT', 'STT', 'SRCL', 'SYK', 'STI', 'SYMC', 'SYY',
         'TROW', 'TGT', 'TEL', 'TE', 'TGNA', 'THC', 'TDC', 'TSO', 'TXN',
         'TXT', 'HSY', 'TRV', 'TMO', 'TIF', 'TWX', 'TWC', 'TJX', 'TMK',
         'TSS', 'TSCO', 'RIG', 'TRIP', 'FOXA', 'TSN', 'TYC', 'UA',
         'UNP', 'UNH', 'UPS', 'URI', 'UTX', 'UHS', 'UNM', 'URBN', 'VFC',
         'VLO', 'VAR', 'VTR', 'VRSN', 'VZ', 'VRTX', 'VIAB', 'V', 'VNO',
         'VMC', 'WMT', 'WBA', 'DIS', 'WM', 'WAT', 'ANTM', 'WFC', 'WDC',
         'WU', 'WY', 'WHR', 'WFM', 'WMB', 'WEC', 'WYN', 'WYNN', 'XEL',
         'XRX', 'XLNX', 'XL', 'XYL', 'YHOO', 'YUM', 'ZBH', 'ZION', 'ZTS']

etf = ['SPY', 'XLF', 'GDX', 'EEM', 'VXX', 'IWM', 'UVXY', 'UXO', 'GDXJ', 'QQQ']

tickers = sp500 + etf
tickers = [dict(label=str(ticker), value=str(ticker))
           for ticker in tickers]


# Make app layout
app.layout = html.Div(
    [
        html.Div([
            html.H1(
                'Volatility Surface Explorer',
                className='eight columns',
            ),
            html.Img(
                src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png",
                className='one columns',
                style={
                    'height': '60',
                    'width': '135',
                    'float': 'right',
                    'position': 'relative',
                },
            ),
        ],
            className='row'
        ),
        html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
        html.Div([
            html.Div([
                html.Label('Select ticker:'),
                dcc.Dropdown(
                    id='ticker_dropdown',
                    options=tickers,
                    value='SPY',
                ),
            ],
                className='six columns',
            ),
            html.Div([
                html.Label('Option settings:'),
                dcc.RadioItems(
                    id='option_selector',
                    options=[
                        {'label': 'Call', 'value': 'call'},
                        {'label': 'Put', 'value': 'put'},
                    ],
                    value='call',
                    labelStyle={'display': 'inline-block'},
                ),
                dcc.RadioItems(
                    id='market_selector',
                    options=[
                        {'label': 'Market', 'value': 'market'},
                        {'label': 'Last', 'value': 'last'},
                    ],
                    value='market',
                    labelStyle={'display': 'inline-block'},
                ),
            ],
                className='two columns',
            ),
            html.Div([
                html.Div([
                    html.Label('Price threshold:'),
                    dcc.Slider(
                        id='price_slider',
                        min=0,
                        max=200,
                        value=200,
                    ),
                ]),
                html.Div([
                    html.Label('Volume threshold:'),
                    dcc.Slider(
                        id='volume_slider',
                        min=0,
                        max=10,
                        value=1,
                    )
                ]),
            ],
                className='four columns'
            ),
        ],
            className='row',
            style={'margin-bottom': '10'}
        ),
        html.Div([
            html.Div([
                html.Label('Implied volatility settings:'),
                html.Div([
                    dcc.RadioItems(
                        id='iv_selector',
                        options=[
                            {'label': 'Calculate IV ', 'value': True},
                            {'label': 'Use given IV ', 'value': False},
                        ],
                        value=True,
                        labelStyle={'display': 'inline-block'},
                    ),
                    dcc.RadioItems(
                        id='calendar_selector',
                        options=[
                            {'label': 'Trading calendar ', 'value': True},
                            {'label': 'Annual calendar ', 'value': False},
                        ],
                        value=True,
                        labelStyle={'display': 'inline-block'},
                    )
                ],
                    style={'display': 'inline-block', 'margin-right': '10', 'margin-bottom': '10'}
                ),
                html.Div([
                    html.Div([
                        html.Label('Risk-free rate (%)'),
                        dcc.Input(
                            id='rf_input',
                            placeholder='Risk-free rate',
                            type='number',
                            value='0.0',
                            style={'width': '125'}
                        )
                    ],
                        style={'display': 'inline-block'}
                    ),
                    html.Div([
                        html.Label('Dividend rate (%)'),
                        dcc.Input(
                            id='div_input',
                            placeholder='Dividend interest rate',
                            type='number',
                            value='0.0',
                            style={'width': '125'}
                        )
                    ],
                        style={'display': 'inline-block'}
                    ),
                ],
                    style={'display': 'inline-block', 'position': 'relative', 'bottom': '10'}
                )
            ],
                className='six columns',
                style={'display': 'inline-block'}
            ),
            html.Div([
                html.Label('Chart settings:'),
                dcc.RadioItems(
                    id='log_selector',
                    options=[
                        {'label': 'Log', 'value': 'log'},
                        {'label': 'Linear', 'value': 'linear'},
                    ],
                    value='log',
                    labelStyle={'display': 'inline-block'}
                ),
                dcc.Checklist(
                    id='graph_toggles',
                    options=[
                        {'label': 'Flat shading', 'value': 'flat'},
                        {'label': 'Discrete contour', 'value': 'discrete'},
                        {'label': 'Lock camera', 'value': 'lock'}
                    ],
                    values=['flat', 'lock'],
                    labelStyle={'display': 'inline-block'}
                )
            ],
                className='six columns'
            ),
        ],
            className='row'
        ),
        html.Hr(style={'margin': '0', 'margin-bottom': '10'}),
        html.Div([
            dcc.Graph(id='iv_surface', style={'max-height': '600', 'height': '60vh'}),
        ],
            className='row',
            style={'margin-bottom': '20'}
        ),
        html.Div([
            html.Div([
                dcc.Graph(id='iv_heatmap', style={'max-height': '350', 'height': '35vh'}),
            ],
                className='five columns'
            ),
            html.Div([
                dcc.Graph(id='iv_scatter', style={'max-height': '350', 'height': '35vh'}),
            ],
                className='seven columns'
            )
        ],
            className='row'
        ),
        # Temporary hack for live dataframe caching
        # 'hidden' set to 'loaded' triggers next callback
        html.P(
            hidden='',
            id='raw_container',
            style={'display': 'none'}
        ),
        html.P(
            hidden='',
            id='filtered_container',
            style={'display': 'none'}
        )
    ],
    style={
        'width': '85%',
        'max-width': '1200',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'font-family': 'overpass',
        'background-color': '#F3F3F3',
        'padding': '40',
        'padding-top': '20',
        'padding-bottom': '20',
    },
)


# Cache raw data
@app.callback(Output('raw_container', 'hidden'),
              [Input('ticker_dropdown', 'value')])
def cache_raw_data(ticker):

    global raw_data
    raw_data = get_raw_data(ticker)
    print('Loaded raw data')

    return 'loaded'


# Cache filtered data
@app.callback(Output('filtered_container', 'hidden'),
              [Input('raw_container', 'hidden'),
               Input('option_selector', 'value'),
               Input('market_selector', 'value'),
               Input('price_slider', 'value'),
               Input('volume_slider', 'value'),
               Input('iv_selector', 'value'),
               Input('calendar_selector', 'value'),
               Input('rf_input', 'value'),
               Input('div_input', 'value')])  # To be split
def cache_filtered_data(hidden, call_or_put, market,
                        above_below, volume_threshold,
                        calculate_iv, trading_calendar,
                        rf_interest_rate, dividend_rate):

    if hidden == 'loaded':

        if call_or_put == 'call':
            s, p, i = get_filtered_data(raw_data, calculate_iv=calculate_iv,
                                        call=True, put=False,
                                        above_below=float(above_below),
                                        volume_threshold=float(volume_threshold),
                                        rf_interest_rate=float(rf_interest_rate),
                                        dividend_rate=float(dividend_rate),
                                        trading_calendar=trading_calendar,
                                        market=market)
        else:
            s, p, i = get_filtered_data(raw_data, calculate_iv=calculate_iv,
                                        call=False, put=True,
                                        above_below=float(above_below),
                                        volume_threshold=float(volume_threshold),
                                        rf_interest_rate=float(rf_interest_rate),
                                        dividend_rate=float(dividend_rate),
                                        trading_calendar=trading_calendar,
                                        market=market)

        df = pd.DataFrame([s, p, i]).T

        global filtered_data
        filtered_data = df[df[2] > 0.0001]  # Filter invalid calculations with abnormally low IV
        print('Loaded filtered data')

        return 'loaded'


# Make main surface plot
@app.callback(Output('iv_surface', 'figure'),
              [Input('filtered_container', 'hidden'),
               Input('ticker_dropdown', 'value'),
               Input('log_selector', 'value'),
               Input('graph_toggles', 'values')],
              [State('graph_toggles', 'values'),
               State('iv_surface', 'relayoutData')])
def make_surface_plot(hidden, ticker, log_selector, graph_toggles,
                      graph_toggles_state, iv_surface_layout):

    if hidden == 'loaded':

        if 'flat' in graph_toggles:
            flat_shading = True
        else:
            flat_shading = False

        trace1 = {
            "type": "mesh3d",
            'x': filtered_data[0],
            'y': filtered_data[1],
            'z': filtered_data[2],
            'intensity': filtered_data[2],
            'autocolorscale': False,
            "colorscale": [
                [0, "rgb(244,236,21)"], [0.3, "rgb(249,210,41)"], [0.4, "rgb(134,191,118)"], [
                    0.5, "rgb(37,180,167)"], [0.65, "rgb(17,123,215)"], [1, "rgb(54,50,153)"],
            ],
            "lighting": {
                "ambient": 1,
                "diffuse": 0.9,
                "fresnel": 0.5,
                "roughness": 0.9,
                "specular": 2
            },
            "flatshading": flat_shading,
            "reversescale": True,
        }

        layout = {
            "title": "{} Volatility Surface | {}".format(ticker, str(dt.datetime.now())),
            'margin': {
                'l': 10,
                'r': 10,
                'b': 10,
                't': 60,
            },
            'paper_bgcolor': '#FAFAFA',
            "hovermode": "closest",
            "scene": {
                "aspectmode": "manual",
                "aspectratio": {
                    "x": 2,
                    "y": 2,
                    "z": 1
                },
                'camera': {
                    'up': {'x': 0, 'y': 0, 'z': 1},
                    'center': {'x': 0, 'y': 0, 'z': 0},
                    'eye': {'x': 2, 'y': 2, 'z': 2},
                },
                "xaxis": {
                    "title": "Strike ($)",
                },
                "yaxis": {
                    "title": "Expiry (days)",
                },
                "zaxis": {
                    "rangemode": "tozero",
                    "title": "IV (σ)",
                    "type": log_selector
                }
            },
        }

        if (iv_surface_layout is not None and 'lock' in graph_toggles_state):
            up = iv_surface_layout['scene']['up']
            center = iv_surface_layout['scene']['center']
            eye = iv_surface_layout['scene']['eye']
            layout['scene']['camera']['up'] = up
            layout['scene']['camera']['center'] = center
            layout['scene']['camera']['eye'] = eye

        data = [trace1]
        figure = dict(data=data, layout=layout)
        return figure


# Make side heatmap plot
@app.callback(Output('iv_heatmap', 'figure'),
              [Input('filtered_container', 'hidden'),
               Input('ticker_dropdown', 'value'),
               Input('log_selector', 'value'),
               Input('graph_toggles', 'values')],
              [State('graph_toggles', 'values'),
               State('iv_heatmap', 'relayoutData')])
def make_surface_plot(hidden, ticker, log_selector, graph_toggles,
                      graph_toggles_state, iv_heatmap_layout):

    if hidden == 'loaded':

        if 'discrete' in graph_toggles:
            shading = 'contour'
        else:
            shading = 'heatmap'

        trace1 = {
            "type": "contour",
            'x': filtered_data[0],
            'y': filtered_data[1],
            'z': filtered_data[2],
            'connectgaps': True,
            'line': {'smoothing': '1'},
            'contours': {'coloring': shading},
            'autocolorscale': False,
            "colorscale": [
                [0, "rgb(244,236,21)"], [0.3, "rgb(249,210,41)"], [0.4, "rgb(134,191,118)"], [
                    0.5, "rgb(37,180,167)"], [0.65, "rgb(17,123,215)"], [1, "rgb(54,50,153)"],
            ],
            # Add colorscale log
            "reversescale": True,
        }

        layout = {
            'margin': {
                'l': 60,
                'r': 10,
                'b': 60,
                't': 10,
            },
            'paper_bgcolor': '#FAFAFA',
            "hovermode": "closest",
            "xaxis": {
                "title": "Strike ($)",
            },
            "yaxis": {
                "title": "Expiry (days)",
            },
        }

        # if (iv_heatmap_layout is not None and 'lock' in graph_toggles_state):
        #     up = iv_surface_layout['scene']['up']
        #     center = iv_surface_layout['scene']['center']
        #     eye = iv_surface_layout['scene']['eye']
        #     layout['scene']['camera']['up'] = up
        #     layout['scene']['camera']['center'] = center
        #     layout['scene']['camera']['eye'] = eye

        data = [trace1]
        figure = dict(data=data, layout=layout)
        return figure


# Make side scatter plot
@app.callback(Output('iv_scatter', 'figure'),
              [Input('filtered_container', 'hidden'),
               Input('ticker_dropdown', 'value'),
               Input('log_selector', 'value'),
               Input('graph_toggles', 'values')],
              [State('graph_toggles', 'values'),
               State('iv_scatter', 'relayoutData')])
def make_scatter_plot(hidden, ticker, log_selector, graph_toggles,
                      graph_toggles_state, iv_heatmap_layout):

    if hidden == 'loaded':

        if 'discrete' in graph_toggles:
            shading = 'contour'
        else:
            shading = 'heatmap'

        trace1 = {
            'x': filtered_data[1],
            'y': filtered_data[2],
            # 'connectgaps': True,
            # 'line': {'smoothing': '1'},
            # 'contours': {'coloring': shading},
            # 'autocolorscale': False,
            # "colorscale": [
            #     [0, "rgb(244,236,21)"], [0.3, "rgb(249,210,41)"], [0.4, "rgb(134,191,118)"], [
            #         0.5, "rgb(37,180,167)"], [0.65, "rgb(17,123,215)"], [1, "rgb(54,50,153)"],
            # ],
            # # Add colorscale log
            # "reversescale": True,
            'mode': 'markers',
            "type": "scatter",
        }

        layout = {
            'margin': {
                'l': 60,
                'r': 10,
                'b': 60,
                't': 10,
            },
            'paper_bgcolor': '#FAFAFA',
            "hovermode": "closest",
            "xaxis": {
                "title": "Expiry (days)",
            },
            "yaxis": {
                "rangemode": "tozero",
                "title": "IV (σ)",
            },
        }

        # if (iv_heatmap_layout is not None and 'lock' in graph_toggles_state):
        #     up = iv_surface_layout['scene']['up']
        #     center = iv_surface_layout['scene']['center']
        #     eye = iv_surface_layout['scene']['eye']
        #     layout['scene']['camera']['up'] = up
        #     layout['scene']['camera']['center'] = center
        #     layout['scene']['camera']['eye'] = eye

        data = [trace1]
        figure = dict(data=data, layout=layout)
        return figure


# In[]:
# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
