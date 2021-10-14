from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from common import Navbar

def create_layout():
    layout = dbc.Container(html.Div([Navbar(),html.H3('Home')]))
    return layout
