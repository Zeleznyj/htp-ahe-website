import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import json_tricks

from app import app
from ..utils import Header
from interpolate import interpolate_to_new_grid,plotly_plane,add_plane,create_3d_plot,show_planes,hide_planes,plot_bands,add_circle,add_line

colors = px.colors.qualitative.G10
prefix = 'GdTmRh2'
data_dir = 'nodal_lines/data/GdTmRh2/'

def create_layout():

    def plot_3d_cb(i):
        debug = False
        if debug == False:
            fig3d = create_3d_plot(data_dir + 'Xkd_i{}.json'.format(i),isomin=5e3,isomax=1e5,
                    surface_count=14)

            opacity = 0.3
            add_plane(fig3d,[0,2,0],[0,0,2],shift=[0,-1,-1],color=colors[1],opacity=opacity,name='[100] plane',visible='legendonly')
            add_plane(fig3d,[0,2,0],[0,0,2],shift=[1,-1,-1],color=colors[1],opacity=opacity,name='[100] shifted plane',visible='legendonly')
            add_plane(fig3d,[0,2,0],[0,0,2],shift=[-1,-1,-1],color=colors[1],opacity=opacity,name='[100] shifted2 plane',visible='legendonly')
            add_plane(fig3d,[2,0,0],[0,0,2],shift=[-1,0,-1],color=colors[1],opacity=opacity,name='[010] plane',visible='legendonly')
            add_plane(fig3d,[2,0,0],[0,0,2],shift=[-1,1,-1],color=colors[1],opacity=opacity,name='[010] shifted plane',visible='legendonly')
            add_plane(fig3d,[2,0,0],[0,0,2],shift=[-1,-1,-1],color=colors[1],opacity=opacity,name='[010] shifted2 plane',visible='legendonly')
        else:
            fig3d = go.Figure()
        return fig3d

    fig3d = plot_3d_cb(30)

    figp1 = plotly_plane(data_dir + 'plane1.json',bands=[1,2,3,4],legendonlybands=[2])
    add_line(figp1,y0=0.12,name='line 1',dash='dash')
    add_line(figp1,y0=0.55,name='line 2',dash='dot')

    figb1_1 = plot_bands(data_dir + 'bands1_1.json',title='Bands and Berry curvature along line 1',ylim=(-0.2,0.2))
    add_circle(figb1_1,0.11,-0.13,color=colors[2])
    add_circle(figb1_1,0.223,-0.11,color=colors[2])

    figb1_2 = plot_bands(data_dir + 'bands1_2.json',title='Bands and Berry curvature along line 2',ylim=(-0.1,0.05))
    add_circle(figb1_2,0.447,-0.059,color=colors[4])
    add_circle(figb1_2,0.448,-0.068,color=colors[5])

    layout = html.Div([
        html.H1(children='GdTmRh2'),
        dcc.Link('Link to Materials Project', href='https://materialsproject.org/materials/mp-1184489'),

        html.P("""In this material the hotspots are strongly centered in [100] and [010] mirror planes. 
        Many nodal lines exist within these planes. The hotspots are likely connected to the nodal lines,
        although clear attribution of the individual nodal lines to the hotspots is made complicated by
        the large number of bands in this material and strong spin-orbit coupling.
        """),

        html.H3('3D plot of the Berry curvature distribution in the Brillouin zone'),
        html.P("""The following plot shows the distribution of the Berry curvature in the Brillouin zone.
        The plot is given in cartesian coordinates scaled by \u03C0/a,
        where a is the length of the first primitive reciprocal lattice vector.
        Note that this material is FCC and its Brillouin zone is thus not rectangular. Since the 3d plot uses
        a rectangular mesh, it at some places extends from the first Brillouin zone.
        """),


        dbc.Checklist(options=[{'label' : 'High resolution plot', 'value' : 1}],id=prefix+'button_prec',switch=True),
        dbc.Alert("""The high resolution plot shows the Berry curvature distribution more clearly,
        but can be slow to load or even unstable!""", color="warning"),

        dbc.Button("Show mirror planes", outline=True, color="primary", className="mr-1", id=prefix+"button_show"),
        dbc.Button("Hide mirror planes", outline=True, color="primary", className="mr-1", id=prefix+"button_hide"),
        dbc.Alert("You can also show or hide individual planes by clicking on the legend.", color="info"),

        dbc.Container(
        dcc.Graph(
            id=prefix+'fig_3d',
            figure=fig3d
            )
        ),

        html.P("""
        All of the [100] and [010] mirros in this material are equivalent and thus in the following we explore only
        one of them in detail. Note that in the above plot, the shifted planes do not appear to be equivalent to the
        ones that go through the [0,0,0] point. This is because the k-mesh is not fine enough. Switching to high-precision
        plot makes the equivalency much more apparent.
        """),

        html.H3('Berry curvature distribution in the [100] plane'),
        html.P(""""""),
        dbc.Container(
            dcc.Graph(
                id=prefix+'plane1',
                figure=figp1
                )
            ),

        html.P("""The hotspots along line 1 are likely related to nodal line 1, although this cannot be said for sure
                without deeper analysis."""),
        dbc.Container(
            dcc.Graph(
                id=prefix+'bands1_1',
                figure=figb1_1
                )
            ),

        html.P("""The main circular hotspot close to the center is likely due to the two nearby nodal lines."""),
        dbc.Container(
            dcc.Graph(
                id=prefix+'bands1_2',
                figure=figb1_2
                )
            ),
    ])
    return layout


@app.callback(
    Output(prefix+'fig_3d','figure'),
    inputs = [
    Input(prefix+'button_show','n_clicks'),
    Input(prefix+'button_hide','n_clicks'),
    Input(prefix+'button_prec','value')
    ],
    state=[State(prefix+'fig_3d','figure')],
    prevent_initial_call=True)
def show_hide_planes(value0,value1,prec,fig3d):
    ctx = dash.callback_context
    if fig3d is None:
        raise PreventUpdate
    if not ctx.triggered:
        raise PreventUpdate
    elif 'prec' in ctx.triggered[0]['prop_id']:
        value = ctx.triggered[0]['value']
        if len(value) == 0:
            return plot_3d_cb(30)
        elif len(value) == 1:
            return plot_3d_cb(60)
        else:
            print('Oh no!')
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == prefix+'button_show':
            fig3d = go.Figure(fig3d)
            fig = show_planes(fig3d)
            return fig
        else:
            fig3d = go.Figure(fig3d)
            fig = hide_planes(fig3d)
            return fig

