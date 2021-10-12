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
prefix = 'U2PN2'
data_dir = 'data/U2PN2/'

debug = False
if debug == False:
    fig3d = create_3d_plot(data_dir + 'Xkd_i30.json',isomin=1e3,isomax=1e4)

    opacity = 0.3
    add_plane(fig3d,[1,0,0],[0,0,1],color=colors[1],opacity=opacity,name='[010] plane',visible='legendonly',legendgroup='planes')
    add_plane(fig3d,[0,1,0],[0,0,1],color=colors[1],opacity=opacity,name='[100] plane',visible='legendonly',legendgroup='planes')
    add_plane(fig3d,[1,0,0],[0,0,1],shift=[0,1,0],color=colors[1],opacity=opacity,name='[010] plane',visible='legendonly',legendgroup='planes')
    add_plane(fig3d,[0,1,0],[0,0,1],shift=[1,0,0],color=colors[1],opacity=opacity,name='[100] plane',visible='legendonly',legendgroup='planes')
    add_plane(fig3d,[1,-1,0],[0,0,1],shift=[0,1,0],color=colors[1],opacity=opacity,name='[110] plane',visible='legendonly',legendgroup='planes')
    add_plane(fig3d,[1,1,0],[0,0,1],color=colors[3],opacity=opacity,name='[1-10] plane',visible='legendonly',legendgroup='planes')
else:
    fig3d = go.Figure()

figp1 = plotly_plane(data_dir + 'plane1.json',bands=[0,1,2])
figp1.update_layout(autosize=True)
add_line(figp1,y0=0.836,name='line 1',dash='dash')
add_line(figp1,y0=0.6,name='line 2',dash='dot')

figb1_1 = plot_bands(data_dir + 'bands1_1.json',title='Bands and Berry curvature along line 1')
add_circle(figb1_1,0.05,0.02,color=colors[1])
add_circle(figb1_1,0.926,0.046,color=colors[2])
add_circle(figb1_1,0.926,0.046,size=18,color=colors[3])

figb1_2 = plot_bands(data_dir + 'bands1_2.json',title='Bands and Berry curvature along line 2')
add_circle(figb1_2,0.76,-0.05,color=colors[2])
add_circle(figb1_2,0.24,-0.03,color=colors[2])

figp2 = plotly_plane(data_dir + 'plane2.json',bands=[0,1,2])
figp2.update_layout(autosize=True)
add_line(figp2,y0=0.71,name='line 1',dash='dash')
add_line(figp2,y0=0.95,name='line 2',dash='dot')

figb2_1 = plot_bands(data_dir + 'bands2_1.json',title='Bands and Berry curvature along line 1')
add_circle(figb2_1,1.0/3,-0.068,color=colors[1])
add_circle(figb2_1,1.0/3,-0.068,size=18,color=colors[2])
add_circle(figb2_1,0,0.023,color=colors[2])

figb2_2 = plot_bands(data_dir + 'bands2_2.json',title='Bands and Berry curvature along line 2')
add_circle(figb2_2,1.0/3,-0.04,color=colors[2])

layout =  html.Div([
    html.H2(prefix),
    dcc.Link('Material at Materials Project', href='https://materialsproject.org/materials/mp-5381/'),

    html.H3('3D plot of the Berry curvature distribution in the Brillouin zone'),

    html.P("""In this material all the hotspots are clearly centered in high-symmetry planes and lines. Due to it's large spin-orbit
        coupling the hotspots are quite delocalized, and thus extend to large part of the Brillouin zone. All the main hotpots are
        connected to nodal lines in the non-relativistic structure, which are protected either by mirror or rotation symmetry."""),
    html.P("""The following plot shows the distribution of the Berry curvature in the Brillouin zone.
                The plot is given in coordinates of the reciprocal lattice vectors of the conventional lattice.
                Note that in this material is hexagonal and thus the reciprocal lattice vectors are hexagonal as well!"""),

    dbc.Checklist(options=[{'label' : 'Show symmetry planes', 'value' : 1}],id=prefix+'show_planes_button',switch=True),
    dbc.Container(
    dcc.Graph(
        id=prefix+'fig_3d',
        figure=fig3d
        )
    ),
    html.P("""Three mirror planes exist in this material: [100], [010] and [110]. Due to symmetry the Berry curvature distribution is the
        same in all of the planes and thus we show only one of those in the following. Note that the [1-10] plane, which is also highlighted
        in the above
        plot is not a mirror plane! It contains nodal lines due to rotation symmetry, however. Interestingly, the main hotspot is actually
        connected with a crossing of two nodal lines (nodal lines 1 and 2) and thus to a triple degeneracy point."""),

    html.H3('Berry curvature distribution in the [100] plane'),
    html.P("""The hotspots are likely connected with the nodal lines. They do not overlap exactly, because the spin-orbit coupling in this
        material is very large and the relativistic bands thus deviate significantly from the non-relativistic bands."""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane1',
            figure=figp1
            )
        ),


    html.P("""The double circle shows the triple degeneracy point."""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands1_1',
            figure=figb1_1
            )
        ),

    dbc.Container(
        dcc.Graph(
            id=prefix+'bands1_2',
            figure=figb1_2
            )
        ),

    html.H3('Berry curvature distribution in the [1-10] plane'),
    html.P("""This plane is not a mirror plane. The nodal lines in this plane are not connected to a mirror symmetry, bur rather rotation
            symmetry. Also in this plane the main hotspots are connected to a triple degeneracy point, which in this case corresponds to
            crossing of nodal lines 0 and 1."""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane2',
            figure=figp2
            )
        ),

    dbc.Container(
        dcc.Graph(
            id=prefix+'bands2_1',
            figure=figb2_1
            )
        ),

    dbc.Container(
        dcc.Graph(
            id=prefix+'bands2_2',
            figure=figb2_2
            )
        ),


])

@app.callback(
    Output(prefix+'fig_3d','figure'),
    [Input(prefix+'show_planes_button','value')],state=[State(prefix+'fig_3d','figure')],
    prevent_initial_call=True)
def toggle_planes(value,fig3d):
    print(value,type(fig3d))
    if fig3d is None:
        raise PreventUpdate
    if len(value) == 0:
        fig3d = go.Figure(fig3d)
        fig = hide_planes(fig3d)
        print(type(fig))
        return fig
    elif len(value) == 1:
        fig3d = go.Figure(fig3d)
        fig = show_planes(fig3d)
        print(type(fig))
        return fig
    else:
        print(value)
        raise PreventUpdate

