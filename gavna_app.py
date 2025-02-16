from datetime import datetime
import dash
import pandas as pd
from dash import dcc, html, Dash
from dash.dependencies import Input, Output
from plotly import graph_objects
import yfinance
import numpy as np

app = Dash(__name__)
server = app.server

TIME_DELTA = 260# 140last T hours of data are looked into as per insert time

COLORS = [
    "#1e88e5",
    "#7cb342",
    "#fbc02d",
    "#ab47bc",
    "#26a69a",
    "#5d8aa8",
]

def now() -> datetime:
    return datetime.now()-timedelta(hours=TIME_DELTA)
def squish():
    squish = pd.read_csv("https://www.dropbox.com/scl/fi/h4er7csx9mh6zby8uc65k/gamma_range_summ_squish_0dte.csv?rlkey=f8hudxdwdu0w2um3h1o4aubpg&dl=1",index_col=0)
    squish = squish.iloc[3:]
    squish['red'] = pd.to_numeric(squish['red'])
    squish['blue'] = pd.to_numeric(squish['blue'])
    return squish
    
def boundaryes():

    
    test = pd.read_csv("https://www.dropbox.com/scl/fi/suid506qym5gfijvm3usv/vanna_range_summ_result_test_0dte.csv?rlkey=f416z6d5osw0oybxuzbg9ipls&dl=1",index_col=0) # 
    test_7dte = pd.read_csv("https://www.dropbox.com/scl/fi/c3qd9wv4ltbb3t8neobu1/vanna_range_summ_result_test_7dte.csv?rlkey=y2fngkjtqrjhs4rbs8tu8hhgv&dl=1",index_col=0) # 
    gamma = pd.read_csv("https://www.dropbox.com/scl/fi/5v4ozyzzef0z0hxfsh9t6/gamma_range_summ_result_test_0dte.csv?rlkey=e64rjorrp8yq520covmyce80u&dl=1",index_col=0) # 
    gamma_7dte = pd.read_csv("https://www.dropbox.com/scl/fi/wc92bzd29se8wv4rzam7w/gamma_range_summ_result_test_7dte.csv?rlkey=lf4pwojnlwq91jc1cfyhnuwa9&dl=1",index_col=0)# 
    
    test['date'] = pd.to_datetime(test['date'], format='mixed')#'%Y-%m-%d %H-%M'
    test['date'] = test['date'].apply(lambda x: x -timedelta(hours=8))
    test.index = test['date']
    test_7dte['date'] = pd.to_datetime(test_7dte['date'], format='mixed')#'%Y-%m-%d %H-%M'
    test_7dte['date'] = test_7dte['date'].apply(lambda x: x -timedelta(hours=8))
    test_7dte.index = test_7dte['date']
    
    gamma['date'] = pd.to_datetime(gamma['date'], format='mixed')#'%Y-%m-%d %H-%M'
    gamma['date'] = gamma['date'].apply(lambda x: x -timedelta(hours=8))
    gamma.index = gamma['date']
    gamma_7dte['date'] = pd.to_datetime(gamma_7dte['date'], format='mixed')#'%Y-%m-%d %H-%M'
    gamma_7dte['date'] = gamma_7dte['date'].apply(lambda x: x -timedelta(hours=8))
    gamma_7dte.index = gamma_7dte['date']
    
    full_df = pd.concat([gamma_7dte['zero'],gamma_7dte['low'],test_7dte['minVanna'],test_7dte['maxVanna'],test_7dte['zero'],gamma['zero'],test_7dte['puts'],test_7dte['calls']],axis=1,keys = ['zero','low','minVanna','maxVanna','vanna_zero','gamma_zero_0dte','puts','calls'])
    full_df = full_df[full_df.index >= '2025-01-26']
    return full_df.ffill().bfill()

def boundaryes_vix():
    test = pd.read_csv("https://www.dropbox.com/scl/fi/wn5fikd5anjqmwnz2uch6/vanna_range_summ_result_test_7dte_VIX.csv?rlkey=toi3x3p6wln53byb0akj7zmae&dl=1",index_col=0) # 
    test['date'] = pd.to_datetime(test['date'], format='mixed')#'%Y-%m-%d %H-%M'
    test['date'] = test['date'].apply(lambda x: x -timedelta(hours=9))
    test.index = test['date']

    test = test[test.index >= '2025-01-26']
    return test.ffill().bfill()



def get_stock_data(start: datetime, stock_symbol: str):
    def format_date(dt: datetime) -> str:
        return dt.isoformat(timespec="microseconds") + "Z"

    query = f"SELECT * FROM quotes WHERE ts BETWEEN '{format_date(start)}' AND "
    if stock_symbol:
        query += f" AND stock_symbol = '{stock_symbol}' "
    tick = yfinance.Ticker(stock_symbol)
    return tick.history(start=start,interval = "5m")

def get_stock_data_vix(start: datetime):
    def format_date(dt: datetime) -> str:
        return dt.isoformat(timespec="microseconds") + "Z"
    tick = yfinance.Ticker('^VIX')
    return tick.history(start=start,interval = "5m")
    
# df = get_stock_data(now() - timedelta(hours=TIME_DELTA), "^SPX")


app = dash.Dash(
    __name__,
    title="Real-time GAVNA changes",
    assets_folder="../assets",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H4("Stock market changes", className="app__header__title"),

                    ],
                    className="app__header__desc",
                ),
            ],
            className="app__header",
        ),
        html.Div(
            [
                html.P("Select a stock symbol"),
                dcc.Dropdown(
                    id="stock-symbol",
                    searchable=True,
                    options=["^SPX"],value="^SPX"
                ),
            ],
            className="app__selector",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [html.H6("SPX GAVNA", className="graph__title")]
                        ),
                        dcc.Graph(id="stock-graph"),
                    ],
                    className="one-half column",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.H6("squish", className="graph__title")]
                        ),
                        dcc.Graph(id="squish-change"),
                    ],
                    className="one-half column",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.H6("VIX GAVNA", className="graph__title")]
                        ),
                        dcc.Graph(id="stock-graph-percent-change"),
                    ],
                    className="one-half column",
                ),
                
            ],
            className="app__content",
        ),
        dcc.Interval(
            id="stock-graph-update",
            interval=int(10000),
            n_intervals=0,
        ),
    ],
    className="app__container",
)
@app.callback(
    Output("stock-graph", "figure"),
    [Input("stock-symbol", "value"), 
     Input("stock-graph-update", "n_intervals")],
)


def generate_stock_graph(selected_symbol, _):
    data = []
    data_boundary = boundaryes()
    filtered_df = get_stock_data(now() - timedelta(hours=TIME_DELTA), selected_symbol)
    data_frame = filtered_df
    

    
    trace1 = graph_objects.Scatter(
        x=data_boundary.index,
        y=data_boundary['zero'],
        marker=dict(color=COLORS[len(data)]),
        name="gamma_zero",line_width=0.5,yaxis='y1'
    )
    data.append(trace1)
    
    trace2 = graph_objects.Scatter(
        x=data_boundary.index,
        y=data_boundary['low'],
        marker=dict(color=COLORS[len(data)]),
        name="gamma_low",line_width=0.5,yaxis='y1'
    )
    data.append(trace2)
    
    

    trace5 = graph_objects.Scatter(
                 x=data_boundary.index,
                 y=data_boundary['maxVanna'],
                 name="maxVanna",line_width=1,yaxis='y1')
    data.append(trace5)

    trace6 = graph_objects.Scatter(
                 x=data_boundary.index,
                 y=data_boundary['vanna_zero'],
                 name="vanna_zero",line_width=1,yaxis='y1')
    data.append(trace6)

    
    # trace3 = graph_objects.Scatter(x=data_frame.index,y=data_frame['Close'],name="Close",line_width=3)
    trace3 = graph_objects.Candlestick(x=data_frame.index,
                open=data_frame['Open'],
                high=data_frame['High'],
                low=data_frame['Low'],
                close=data_frame['Close'],yaxis='y1')
    data.append(trace3)

    trace7 = graph_objects.Scatter(
        x=data_boundary.index,
        y=data_boundary['gamma_zero_0dte'],
        name="gamma_zero_0dte",line_width=1,yaxis='y1'
    )
    data.append(trace7)

    trace8 = graph_objects.Bar(
                 x = data_boundary.index,
                 y = ((data_boundary['puts'] - data_boundary['calls'])/(data_boundary['puts'] + data_boundary['calls']))-1,
                 name="minVanna",opacity = 0.8,yaxis='y2')
    data.append(trace8)

    
    layout = graph_objects.Layout(height=900, width=1900,xaxis_rangeslider_visible=False,
        xaxis={"title": "Time"},
        yaxis={"title": "Price"},
        yaxis2=dict(title='Moddel Difference',overlaying='y',side='right'),
        margin={"l": 70, "b": 70, "t": 70, "r": 70},
        hovermode="closest",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"color": "#aaa"},showlegend=False
    )

    figure = graph_objects.Figure(data=data, layout=layout)
    figure.update_yaxes(gridwidth=0.1)
    figure.update_xaxes(rangebreaks=[
            dict(bounds=["sat", "mon"]),
            dict(bounds=[16, 7.5], pattern="hour"),
        ],showgrid=False,gridwidth=0.3
    )



    return figure

@app.callback(
    Output("stock-graph-percent-change", "figure"),
    [
        Input("stock-symbol", "value"),
        Input("stock-graph-update", "n_intervals"),
    ],
)


def generate_stock_graph_percentage(selected_symbol, _):
    data = []
    data_boundary = boundaryes_vix()
    filtered_df = get_stock_data_vix(now() - timedelta(hours=TIME_DELTA))
    data_frame = filtered_df

    trace1 = graph_objects.Candlestick(x=data_frame.index,
                open=data_frame['Open'],
                high=data_frame['High'],
                low=data_frame['Low'],
                close=data_frame['Close'],yaxis='y1')
    data.append(trace1)
    
    trace1 = graph_objects.Scatter(
        x = data_boundary.index,
        y = data_boundary['maxVanna'],
        marker=dict(color=COLORS[len(data)]),
        name="group2",line_width=3,yaxis='y1'
    )
    data.append(trace1)

    trace2 = graph_objects.Scatter(
        x = data_boundary.index,
        y = data_boundary['zero'],
        marker=dict(color=COLORS[len(data)]),
        name="group2",line_width=3,yaxis='y1'
    )
    data.append(trace2)

    trace3 = graph_objects.Scatter(
        x = data_boundary.index,
        y = data_boundary['minVanna'],
        marker=dict(color=COLORS[len(data)]),
        name="group2",line_width=3,yaxis='y1'
    )
    data.append(trace3)

    trace4 = graph_objects.Scatter(
        x = data_boundary.index,
        y = data_boundary['low'],
        marker=dict(color=COLORS[len(data)]),
        name="group2",line_width=3,yaxis='y1'
    )
    data.append(trace4)

    trace5 = graph_objects.Bar(
        x = data_boundary.index,
        y = ((data_boundary['puts'] - data_boundary['calls'])/(data_boundary['puts'].abs() + data_boundary['calls'].abs()))+1,
        marker=dict(color=COLORS[len(data)]),
        name="group2",opacity = 0.4,yaxis='y2'
    )
    data.append(trace5)

    



    layout = graph_objects.Layout(height=900, width=1900,xaxis_rangeslider_visible=False,
        xaxis={"title": "Time"},
        yaxis={"title": "Price"},
        yaxis2=dict(title='Moddel Difference',overlaying='y',side='right'),
        margin={"l": 70, "b": 70, "t": 70, "r": 70},
        hovermode="closest",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"color": "#aaa"},showlegend=False
    )


    
    figure = graph_objects.Figure(data=data, layout=layout)
    figure.update_yaxes(gridwidth=0.1)
    figure.update_xaxes(rangebreaks=[
            dict(bounds=["sat", "mon"]),
            dict(bounds=[16, 7.5], pattern="hour"),
        ],showgrid=False,gridwidth=0.3
    )
 
    return figure
    
@app.callback(
    Output("squish-change", "figure"),
    [
        Input("stock-symbol", "value"),
        Input("stock-graph-update", "n_intervals"),
    ],
)
def generate_stock_graph_squish(selected_symbol, _):
    data = []
    data_frame = squish()

    trace1 = graph_objects.Scatter(
        x = data_frame.index,
        y = data_frame['red'],
        name="group2",line_width=3
    )
    data.append(trace1)

    trace2 = graph_objects.Scatter(
        x = data_frame.index,
        y = data_frame['blue'],
        name="group2",line_width=3
    )
    data.append(trace2)

    layout = graph_objects.Layout(height=900, width=1900,xaxis_rangeslider_visible=False,
        xaxis={"title": "Time"},
        yaxis={"title": "Price"},
        margin={"l": 70, "b": 70, "t": 70, "r": 70},
        hovermode="closest",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"color": "#aaa"},showlegend=False
    )


    
    figure = graph_objects.Figure(data=data, layout=layout)
    figure.update_yaxes(gridwidth=0.1)
    figure.update_xaxes(rangebreaks=[
            dict(bounds=["sat", "mon"]),
            dict(bounds=[16, 7.5], pattern="hour"),
        ],showgrid=False,gridwidth=0.3
    )
 
    return figure



if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)



