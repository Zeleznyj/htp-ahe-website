import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json_tricks
import dash_bootstrap_components as dbc

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from app import app
from common import Navbar

from .materials import Eu2SeO2,GdTmRh2,U2PN2,Ni,MnCoPt2,CeTe2
from .utils import Header
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
def create_layout():
    layout = dbc.Container([Navbar(),Header(app), html.Div(id="material-content")])
    return layout

@app.callback(dash.dependencies.Output("material-content","children"),
        [dash.dependencies.Input('materials-selection','value')])
def update(value):
    if value == 'Eu2SeO2':
        return Eu2SeO2.create_layout()
    elif value == 'GdTmRh2':
        return GdTmRh2.create_layout()
    elif value == 'U2PN2':
        return U2PN2.create_layout()
    elif value == 'Ni':
        return Ni.create_layout()
    elif value == 'MnCoPt2':
        return MnCoPt2.create_layout()
    elif value == 'CeTe2':
        return CeTe2.create_layout()
    else:
        print('nevim')

#Eu2SeO2.create_layout(app)

