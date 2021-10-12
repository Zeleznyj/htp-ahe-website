import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
from numpy.linalg import norm
import json_tricks


from app import app
from utils import Header
from interpolate import interpolate_to_new_grid,plotly_plane,add_plane,create_3d_plot,show_planes,hide_planes,plot_bands,add_circle,add_line



colors = px.colors.qualitative.G10
prefix = 'Eu2SeO2'
data_dir = 'data/Eu2SeO2/'

a = 0.5487316940540308
c = 0.3121912684686448

def plot_3d_cb(i):
    debug = False
    if debug == False:
        fig3d = create_3d_plot(data_dir + 'Xkd_i30.json',isomin=1e3,isomax=1e4)

        opacity = 0.3
        add_plane(fig3d,[a*2,a*2,0],[0,0,c*2],shift=[-a,-a,-c],color=colors[1],opacity=opacity,
                name='[1-10] plane',visible='legendonly')
        add_plane(fig3d,[a*2,-a*2,0],[0,0,c*2],shift=[-a,a,-c],color=colors[1],opacity=opacity,
                name='[110] plane',visible='legendonly')
        add_plane(fig3d,[2*a,0,0],[0,2*a,0],shift=[-a,-a,0],color=colors[2],opacity=opacity,
                name='[001] plane',visible='legendonly')
        add_plane(fig3d,[2*a,0,0],[0,2*a,0],shift=[-a,-a,-c],color=colors[2],opacity=opacity,
                name='[001] plane shifted',visible='legendonly')
        add_plane(fig3d,[0,a*2,0],[0,0,c*2],shift=[0,-a,-c],color=colors[3],opacity=opacity,
                name='[100] plane',visible='legendonly')
        add_plane(fig3d,[2*a,0,0],[0,0,c*2],shift=[-a,0,-c],color=colors[3],opacity=opacity,
                name='[010] plane',visible='legendonly')
    else:
        fig3d = go.Figure()
    return fig3d

fig3d = plot_3d_cb(30)

figp2 = plotly_plane(data_dir + 'plane2.json',bands=[1,2])
add_line(figp2,y0=0.5,name='line 1',dash='dash')
add_line(figp2,y0=0.15,name='line 2',dash='dot')

figb2_1 = plot_bands(data_dir + 'bands_2_1.json',title='Bands and Berry curvature along line 1',ylim=(-0.2,0.2))
add_circle(figb2_1,0.2,-0.06,color=colors[3])
add_circle(figb2_1,0.323,-0.17,color=colors[2])

figb2_2 = plot_bands(data_dir + 'bands_2_2.json',title='Bands and Berry curvature along line 2',ylim=(-0.2,0.2))
add_circle(figb2_2,0.175,0.037,color=colors[3])
add_circle(figb2_2,0.5,-0.0114,color=colors[2])

figp3 = plotly_plane(data_dir + 'plane3.json',bands=[1,2])
add_line(figp3,y0=0.38,name='line 1',dash='dash')
add_line(figp3,y0=0.5,name='line 2',dash='dot')

figb3_1 = plot_bands(data_dir + 'bands_3_1.json',title='Bands and Berry curvature along line 1',ylim=(-0.2,0.2))
add_circle(figb3_1,0.0505,-0.008,color=colors[3])
add_circle(figb3_1,0.11,-0.024,color=colors[3])

figb3_2 = plot_bands(data_dir + 'bands_3_2.json',title='Bands and Berry curvature along line 2',ylim=(-0.2,0.2))
add_circle(figb3_2,0.03,-0.023,color=colors[3])
add_circle(figb3_2,0.185,-0.007,color=colors[3])

figp4 = plotly_plane(data_dir + 'plane4.json',bands=[1,2])
add_line(figp4,y0=0.6,name='line 1',dash='dash')
add_line(figp4,y0=0.5,name='line 2',dash='dot')

figb4_1 = plot_bands(data_dir + 'bands_4_1.json',title='Bands and Berry curvature along line 1',ylim=(-0.2,0.2))
add_circle(figb4_1,0.04,-0.011,color=colors[3])
add_circle(figb4_1,0.353,-0.0035,color=colors[3])
add_circle(figb4_1,0.42,0.025,color=colors[3])

figb4_2 = plot_bands(data_dir + 'bands_4_2.json',title='Bands and Berry curvature along line 2',ylim=(-0.2,0.2))
add_circle(figb4_2,0.056,-0.021,color=colors[3])
add_circle(figb4_2,0.454,0.034,color=colors[2])
add_circle(figb4_2,0.46,0.05,color=colors[3])

figp1 = plotly_plane(data_dir + 'plane1.json',bands=[1,2])

layout =  html.Div([
    html.H2('Eu2SeO2'),
    dcc.Link('Material at Materials Project', href='https://materialsproject.org/materials/mp-753314/'),
    html.P("""In this material some hotspots are located in [110] and [1-10] mirror planes and are thus likely
    related to symmetry. Some of these hotspots can be attributed to nodal lines, although not all. This may be
    because spin-orbit coupling in this material is very large and thus the relativistic bands sometimes significantly
    deviate from the nonrelativistic bands.

    Other hotspots likely originate from nodal lines in [001] planes. These are hotposts, which have small dispersion
    along the z direction and have a tubular shape. We have not identified a nodal line along the direction 
    of the tube there are nodal lines in the [001] planes that intersect the tube at the top and bottom of the Brillouin zone
    as well as in the middle.

    """),

    html.Div([
    dbc.Checklist(options=[{'label' : 'High resolution plot', 'value' : 1}],id=prefix+'button_prec',switch=True),
    dbc.Alert("""The high resolution plot shows the Berry curvature distribution more clearly,
    but can be slow to load or even unstable!""", color="warning"),],style={'display':'none'}),

    html.H3('3D plot of the Berry curvature distribution in the Brillouin zone'),
    html.P("""The following plot shows the distribution of the Berry curvature in the Brillouin zone.
    The plot is given in cartesian coordinates scaled by \u03C0/a,
    where a is the length of the first primitive reciprocal lattice vector."""),

    dbc.Button("Show mirror planes", outline=True, color="primary", className="mr-1", id=prefix+"button_show"),
    dbc.Button("Hide mirror planes", outline=True, color="primary", className="mr-1", id=prefix+"button_hide"),
    dbc.Alert("You can also show or hide individual planes by clicking on the legend.", color="info"),

    dbc.Container(
    dcc.Graph(
        id=prefix+'fig_3d',
        figure=fig3d
        )
    ),


    html.H3('Berry curvature distribution in the [1-10] plane'),
    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane2',
            figure=figp2
            )
        ),

    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands2_1',
            figure=figb2_1
            )
        ),

    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands2_2',
            figure=figb2_2
            )
        ),

    html.H3('Berry curvature distribution in the [001] plane'),
    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane3',
            figure=figp3
            )
        ),

    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands3_1',
            figure=figb3_1
            )
        ),

    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands3_2',
            figure=figb3_2
            )
        ),

    html.H3('Berry curvature distribution in the shifted [001] plane'),
    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane4',
            figure=figp4
            )
        ),

    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands4_1',
            figure=figb4_1
            )
        ),

    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands4_2',
            figure=figb4_2
            )
        ),

    html.H3('Berry curvature distribution in the [100] plane'),
    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane1',
            figure=figp1
            )
        ),


])

@app.callback(
    Output(prefix+'fig_3d','figure'),
    [
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

