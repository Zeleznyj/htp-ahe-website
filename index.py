import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json_tricks
import dash_bootstrap_components as dbc

from app import app
from materials import Eu2SeO2,GdTmRh2
from utils import Header
#from plotly.express.colors.qualitative import vivid

from interpolate import interpolate_to_new_grid,plotly_plane,add_plane

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app = dash.Dash(
#    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
#)
#app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#server = app.server

#app.layout = html.Div([html.Div(id='material-content')])
#app.layout = html.Div(
#    [Header(app), html.Div(id="material-content")]
#)
app.layout = dbc.Container([Header(app), html.Div(id="material-content")])

@app.callback(dash.dependencies.Output("material-content","children"),
        [dash.dependencies.Input('materials-selection','value')])
def update(value):
    if value == 'Eu2SeO2':
        print('Eu2SeO2')
        return Eu2SeO2.layout
    elif value == 'GdTmRh2':
        print('GdTmRh2')
        return GdTmRh2.layout
    else:
        print('nevim')

#Eu2SeO2.create_layout(app)



if __name__ == '__main__':
    app.run_server(debug=True)

