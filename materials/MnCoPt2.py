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
import json_tricks

from app import app
from utils import Header
from interpolate import interpolate_to_new_grid,plotly_plane,add_plane,create_3d_plot,show_planes,hide_planes,plot_bands,add_circle,add_line

colors = px.colors.qualitative.G10
prefix = 'MnCoPt2'
data_dir = 'data/MnCoPt2/'

def plot_3d_cb(i):
    debug = False
    if debug == False:
        fig3d = create_3d_plot(data_dir + 'Xkd_i{}.json'.format(i),isomin=1e3,isomax=3e4,
                surface_count=14)

        opacity = 0.3
        add_plane(fig3d,[1,1,0],[0,0,1],shift=[0,0,0],color=colors[1],opacity=opacity,name='[110] plane',visible='legendonly')
        add_plane(fig3d,[1,-1,0],[0,0,1],shift=[0,1,0],color=colors[1],opacity=opacity,name='[1-10] plane',visible='legendonly')
        add_plane(fig3d,[1,0,0],[0,0,1],shift=[0,0,0],color=colors[2],opacity=opacity,name='[010] plane',visible='legendonly')
        add_plane(fig3d,[1,0,0],[0,0,1],shift=[0,1,0],color=colors[2],opacity=opacity,name='[010] plane',visible='legendonly')
        add_plane(fig3d,[0,1,0],[0,0,1],shift=[0,0,0],color=colors[2],opacity=opacity,name='[100] plane',visible='legendonly')
        add_plane(fig3d,[0,1,0],[0,0,1],shift=[1,0,0],color=colors[2],opacity=opacity,name='[100] plane',visible='legendonly')
    else:
        fig3d = go.Figure()
    return fig3d

fig3d = plot_3d_cb(30)

figp1 = plotly_plane(data_dir + 'plane1.json',bands=[1,2,3])
figp1.update_layout(title='Spin-down bands')
add_line(figp1,y0=0.38,name='line 1',dash='dash')
add_line(figp1,x0=0.5,x1=0.5,y0=0,y1=1,name='line 2',dash='dashdot')

figp1_0 = plotly_plane(data_dir + 'plane1_ms=0.json',bands=[5,6])
figp1_0.update_layout(title='Spin-up bands')
add_line(figp1_0,y0=0.5,name='line 1',dash='dot')

figb1_1 = plot_bands(data_dir + 'bands1_1.json',title='Bands and Berry curvature along line 1',ylim=(-0.1,0.1))
add_circle(figb1_1,0.393,0.08,color=colors[4])
add_circle(figb1_1,0.606,0.08,color=colors[4])

figb1_2 = plot_bands(data_dir + 'bands1_2.json',title='Bands and Berry curvature along line 1',ylim=None)
add_circle(figb1_2,0.,-0.049,color=colors[7])
add_circle(figb1_2,1.,-0.049,color=colors[7])
add_circle(figb1_2,0.247,-0.015,color=colors[6])
add_circle(figb1_2,0.756,-0.015,color=colors[6])

figb1_3 = plot_bands(data_dir + 'bands1_3.json',title='Bands and Berry curvature along line 2',ylim=None)
add_circle(figb1_3,0.36,0.181,color=colors[3])
add_circle(figb1_3,0.36,0.181,size=18,color=colors[2])
add_circle(figb1_3,0.64,0.181,color=colors[3])
add_circle(figb1_3,0.64,0.181,size=18,color=colors[2])

figp2 = plotly_plane(data_dir + 'plane2_ms1.json',bands=[1])
figp2.update_layout(title='Spin-down bands')
add_line(figp2,y0=0.9,name='line 1',dash='dash')

figp2_0 = plotly_plane(data_dir + 'plane2_ms0.json',bands=[2,4])
figp2_0.update_layout(title='Spin-up bands')
add_line(figp2_0,y0=0.75,name='line 1',dash='dash')
add_line(figp2_0,y0=0.5,name='line 2',dash='dot')

figb2_1 = plot_bands(data_dir + 'bands2_1.json',title='Bands and Berry curvature along line 1',ylim=None)
add_circle(figb2_1,0.452,-0.032,color=colors[2])
add_circle(figb2_1,0.547,-0.032,color=colors[2])

figb2_2 = plot_bands(data_dir + 'bands2_2.json',title='Bands and Berry curvature along line 1',ylim=None)
add_circle(figb2_2,0.482,0.078,color=colors[3])
add_circle(figb2_2,0.518,0.078,color=colors[3])

figb2_3 = plot_bands(data_dir + 'bands2_3.json',title='Bands and Berry curvature along line 2',ylim=None)
add_circle(figb2_3,0.,-0.049,color=colors[5])
add_circle(figb2_3,1.,-0.049,color=colors[5])
add_circle(figb2_3,0.036,-0.01,color=colors[5])
add_circle(figb2_3,1-0.036,-0.01,color=colors[5])


layout = html.Div([
    html.H1(children='MnCoPt2'),
    dcc.Link('Link to Materials Project', href='https://materialsproject.org/materials/mp-1221704'),

    html.P("""
    In this material most of the hotspots are located in [110], [-110], [100] and [010] mirror planes,
    although some hotspots also lie outside of the planes. Many of the hotspots can be connected to 
    nodal lines, however, this is not always completely clear since many bands exist in this material
    close to the Fermi level and many nodal lines exist in the mirror planes. In addition spin-orbit coupling
    is fairly large in this material, which means the relativistic bands can differ significantly from the
    non-relativistic ones.
    """),

    html.H3('3D plot of the Berry curvature distribution in the Brillouin zone'),
    html.P("""
    The following plot shows the distribution of the Berry curvature in the reciprocal space. The plot is given in
    coordinates of the reciprocal lattice vectors of the primitive lattice. The plot does not show the first Brillouin
    zone, but rather a unit cell spanned by the reciprocal lattice vectors. This system is tetragonal, which means that
    this cell differs from the first Brillouin zone only by translation.
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
    Two nonequivalent planes exist in this material: [100] and [010].    """),

    
    html.H3('Berry curvature distribution in the [100] plane'),
    html.P(""" 
            Both spin-up and spin-down nodal lines are important in this material
            and thus we show both separately.
        """),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane1',
            figure=figp1
            )
        ),
    html.P("""
            The largest hotspot along this line is associated with nodal line. The other hotspots
            along this line are less clear.
            """),
    
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands1_1',
            figure=figb1_1
            )
        ),

   html.P("""The main hotspot along line 2 correspond to a triple crossing point, since one of the bands
            is degenerate along this line.
            """),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands1_3',
            figure=figb1_3
            )
        ),
     
    html.P(""" 
    """),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane1_0',
            figure=figp1_0
            )
        ),


    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands1_2',
            figure=figb1_2
            )
        ),

    html.H3('Berry curvature distribution in the [100] plane'),
    html.P(""" 
            Both spin-up and spin-down nodal lines are important in this material
            and thus we show both separately.
        """),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane2',
            figure=figp2
            )
        ),

    html.P("""
            The largest hotspot along this line is associated with nodal line.
            """),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands2_1',
            figure=figb2_1
            )
        ),

    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane2_0',
            figure=figp2_0
            )
        ),

    html.P("""
            The main hotspots along lines 1 and 2 are also likely connected to the highlighted nodal lines.
            """),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands2_2',
            figure=figb2_2
            )
        ),

    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands2_3',
            figure=figb2_3
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

