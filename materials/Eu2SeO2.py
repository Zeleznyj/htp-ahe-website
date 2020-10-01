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

prefix = 'Eu2SeO2'
data_dir = 'data/Eu2SeO2/'

debug = False
if debug == False:
    fig3d = create_3d_plot(data_dir + 'Xkd_i30.json')

    opacity = 0.3
    colors = px.colors.qualitative.Vivid
    add_plane(fig3d,[1,1,0],[0,0,1],color=colors[0],opacity=opacity,name='[1-10] plane',visible='legendonly',legendgroup='planes')
    add_plane(fig3d,[1,-1,0],[0,0,1],shift=[0,1,0],color=colors[0],opacity=opacity,name='[110] plane',visible='legendonly',legendgroup='planes')
    add_plane(fig3d,[1,0,0],[0,0,1],shift=[0,0.5,0],color=colors[2],opacity=opacity,name='[010] plane',visible='legendonly',legendgroup='planes')
    add_plane(fig3d,[0,1,0],[0,0,1],shift=[0.5,0,0],color=colors[2],opacity=opacity,name='[100] plane',visible='legendonly',legendgroup='planes')
else:
    fig3d = go.Figure()


colors = px.colors.qualitative.G10

fig2 = plotly_plane(data_dir + 'plane3.json')
fig2.update_layout(autosize=True)
add_line(fig2,y0=0.45,name='line 1',dash='dash')
add_line(fig2,y0=0.2,name='line 2',dash='dot')

figb3_1 = plot_bands(data_dir + 'bands_3_1.json',title='Bands and Berry curvature along line 1')
add_circle(figb3_1,0.325,-0.02,color=colors[3])
add_circle(figb3_1,0.09,-0.1,color=colors[2])

figb3_2 = plot_bands(data_dir + 'bands_3_2.json',title='Bands and Berry curvature along line 2')
add_circle(figb3_2,0.33,-0.05,color=colors[3])
add_circle(figb3_2,0.18,-0.16,color=colors[2])

fig3 = plotly_plane(data_dir + 'plane2.json')
fig3.update_layout(autosize=True)

figb2_1 = plot_bands(data_dir + 'bands_2_1.json',ylim=(-0.1,0.2),title='Bands and Berry curvature along line 1')
add_circle(figb2_1,0.13,-0.005,color=colors[2])


layout =  html.Div([
    html.H2('Eu2SeO2'),
    dcc.Link('Material at Materials Project', href='https://materialsproject.org/materials/mp-753314/'),
    html.P('In this material the hotspots are centered at high symmetry planes related to [100], '
        '[010], [110] and [-110] mirror symmetry operations. However we do not find a clear correlation between the hotspots and'
        'non-relativistic nodal lines, possibly because of the strong spin-orbit coupling in this material.'),

    html.H3('3D plot of the Berry curvature distribution in the Brillouin zone'),
    html.P('The following plot shows the distribution of the Berry curvature in the Brillouin zone. The plot is given in coordinates of\
        the reciprocal lattice vectors of the conventional lattice.'),
    html.P('Double click the plane in the legend to show the relevant high-symmetry planes.'),
    dbc.Checklist(options=[{'label' : 'Show symmetry planes', 'value' : 1}],id=prefix+'show_planes_button',switch=True),
    dbc.Container(
    dcc.Graph(
        id=prefix+'fig_3d',
        figure=fig3d
        )
    ),

    html.H3('Berry curvature distribution in the [1-10] plane'),
    html.P('Several nodal lines exist in this plane, but it is not easy to clearly attribute all the hotspots to the nodal lines.'),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane3',
            figure=fig2
            )
        ),

    dbc.Container(
        dcc.Graph(
            id=prefix+'bands3_1',
            figure=figb3_1
            )
        ),

    dbc.Container(
        dcc.Graph(
            id=prefix+'bands3_2',
            figure=figb3_2
            )
        ),

    html.H3('Berry curvature distribution in the [100] plane'),
    html.P('In this plane we have not found clear nodal lines.'),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane2',
            figure=fig3
            )
        ),

    html.P('The highlighted apparent crossing is actually an anti-crossing and does not seem to be associated with a nodal line.'),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands2_1',
            figure=figb2_1
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

