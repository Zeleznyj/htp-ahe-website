from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from common import Navbar

def create_layout():
    layout = dbc.Container(html.Div([
        Navbar(),
        html.H3('High-troughput study of the anomalous Hall effect'),
        html.P(["""
            This page contains results of high-throughput calculations of the intrinsic 
            anomalous Hall effect in 2871 materials from the Materials Project. See paper [1]
            for the full description of the  calculations.
            Here you can find the detailed results of the calculations for all the materials (""",
            html.A('Materials Explorer',href ='material_explorer'),
            """), interactive plots demonstrating the statistical relation
            between various properties (""",
            html.A("Statistics",href='statistics'),
            """) and analysis of the relation of the 
            origin of the large Anomalous Hall effect and nodal lines in the non-relativistic 
            electronic structure (""",
            html.A("Nodal line analysis",href='nodal_lines'),
            ")"
            ]),
        dbc.Alert(
            """
            Please cite [1] when using the data given here!
            """,
            color="warning"),
        html.A("[1] J. Zelezny et al., npj Computational Materials 9, 151 (2023)",href="https://www.nature.com/articles/s41524-023-01113-5"),
        html.Img(src="assets/FZU-L-EN-RGB.png",alt="Institute of Physics of the Czech Academy of Sciences")
        ]))
    return layout
