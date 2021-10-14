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

from app import app,server
from common import Navbar
import material_explorer.me_app as me_app
import nodal_lines.index_nl as index_nl
import statistics.stat_app as stat_app
import homepage

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
import dash_defer_js_import as dji
mathjax_script = dji.Import(src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/latest.js?config=TeX-AMS-MML_SVG")

navbar = Navbar()
app.layout = dbc.Container([navbar, html.Div(id="material-content")])
app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content'),
    mathjax_script
])


@app.callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/material_explorer':
        return me_app.create_layout()
    elif pathname == '/nodal_lines':
        return index_nl.create_layout()
    elif pathname == '/statistics':
        return stat_app.create_layout()
    else:
        return homepage.create_layout()



if __name__ == '__main__':
    app.run_server(debug=True)

