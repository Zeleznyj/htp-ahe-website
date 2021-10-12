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
prefix = 'Ni'
data_dir = 'data/Ni/'


def plot_3d_cb(i):
    debug = False
    if debug == False:
        fig3d = create_3d_plot(data_dir + 'Xkd_i{}.json'.format(i),isomin=1e3,isomax=1e4,
                surface_count=7)

        opacity = 0.3
        add_plane(fig3d,[1,0,0],[0,1,0],color=colors[1],opacity=opacity,name='[110] plane',visible='legendonly')
        add_plane(fig3d,[1,0,0],[0,0,1],color=colors[1],opacity=opacity,name='[101] plane',visible='legendonly')
        add_plane(fig3d,[0,1,0],[0,0,1],color=colors[1],opacity=opacity,name='[011] plane',visible='legendonly')
        add_plane(fig3d,[0,1,0],[1,0,1],color=colors[1],opacity=opacity,name='[-101] plane',visible='legendonly')
        add_plane(fig3d,[1,0,0],[0,1,1],color=colors[1],opacity=opacity,name='[01-1] plane',visible='legendonly')
        add_plane(fig3d,[0,0,1],[1,1,0],color=colors[1],opacity=opacity,name='[1-10] plane',visible='legendonly')
        add_plane(fig3d,[1,0,1],[1,1,0],color=colors[2],opacity=opacity,name='[100] plane',visible='legendonly')
        add_plane(fig3d,[0,1,1],[1,1,0],color=colors[2],opacity=opacity,name='[010] plane',visible='legendonly')
        add_plane(fig3d,[0,1,1],[1,0,1],color=colors[2],opacity=opacity,name='[001] plane',visible='legendonly')
    else:
        fig3d = go.Figure()
    return fig3d

fig3d = plot_3d_cb(30)


figp1 = plotly_plane(data_dir + 'plane1.json',bands=None)
figp1.update_layout(autosize=True)
add_line(figp1,y0=0.635,name='line 1',dash='dash')
add_line(figp1,y0=0.8,name='line 2',dash='dot')
add_line(figp1,y0=0.5,name='line 3',dash='dashdot')

figb1_1 = plot_bands(data_dir + 'bands1_1.json',title='Bands and Berry curvature along line 1',ylim=(-0.15,0.1))
add_circle(figb1_1,0,-0.070,color=colors[3])
add_circle(figb1_1,0,-0.070,size=18,color=colors[2])
add_circle(figb1_1,0.635,-0.12,color=colors[3])
add_circle(figb1_1,0.75,-0.042,color=colors[3])
add_circle(figb1_1,1,-0.076,color=colors[3])
add_circle(figb1_1,1,-0.076,size=18,color=colors[2])

figb1_2 = plot_bands(data_dir + 'bands1_2.json',title='Bands and Berry curvature along line 2',ylim=(-0.1,0.1))
add_circle(figb1_2,0.15,-0.04,color=colors[3])

figb1_3 = plot_bands(data_dir + 'bands1_3.json',title='Bands and Berry curvature along line 3',ylim=(-0.1,0.1))
add_circle(figb1_3,0.07,-0.022,color=colors[1])
add_circle(figb1_3,0.929,-0.022,color=colors[1])

figp7 = plotly_plane(data_dir + 'plane7.json',bands=None)
add_line(figp7,y0=0.2,name='line 1',dash='dash')

figb7_1 = plot_bands(data_dir + 'bands7_1.json',title='Bands and Berry curvature along line 1',ylim=(-0.1,0.1))
add_circle(figb7_1,0.452,-0.001,color=colors[1])
add_circle(figb7_1,0.547,-0.001,color=colors[1])


layout =  html.Div([
    html.H2(prefix),
    dcc.Link('Material at Materials Project', href='https://materialsproject.org/materials/mp-23/'),

    html.H3('3D plot of the Berry curvature distribution in the Brillouin zone'),

    html.P("""In this material the AHE comes from sharp well defined hotspots. """),
    html.P("""The following plot shows the distribution of the Berry curvature in the Brillouin zone.
                The plot is given in coordinates of the reciprocal lattice vectors of the primitive lattice.
                Note that Ni has a FCC lattice and thus the reciprocal lattice vectors are not orthogonal!
                The naming of the mirrors is, however, based on the conventional lattice vectors. That is, for example,
                the [100] mirror corresponds to the mirror plane which is orthogonal to the [100] direction in the
                conventional lattice."""),

    html.Div(style={'padding': 10}),

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
    html.P("""This material contains 9 mirrors. These can be split into two groups, which each contain mirror planes
    that are equivalent (and thus have same Berry curvature distributions). The first group contains mirror planes:
    [110], [101], [011], [-101], [01-1], [1-10]. The second group contains mirror planes [100], [010] and [001]. """),

    html.H3('Berry curvature distribution in the [-101] plane'),
    html.P("""This plane contains all the major hotspots, which can all be clearly attributed to nodal lines."""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane1',
            figure=figp1
            )
        ),

    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands1_1',
            figure=figb1_1
            )
        ),

    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands1_2',
            figure=figb1_2
            )
        ),

    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands1_3',
            figure=figb1_3
            )
        ),

    html.H3('Berry curvature distribution in the [001] plane'),
    html.P("""This plane does not contain many hotspots. The hotspots close to the edges of the plane are actually due to nodal line in
            different planes, as this is where this plane interests other mirror planes. Only the circular hotspots in the middle can be
            attributed to a nodal line in this plane."""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane7',
            figure=figp7
            )
        ),

    dbc.Container(
        dcc.Graph(
            id=prefix+'bands7_1',
            figure=figb7_1
            )
        ),
    html.P("""Note that the first crossing in this plot corresponds to a nodal line located in a different plane.
            Only the highlighted crossings correspond to this plane."""),

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

