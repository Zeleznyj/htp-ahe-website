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
prefix = 'CeTe2'
data_dir = 'data/CeTe2/'

def plot_3d_cb(i):
    debug = False
    if debug == False:
        fig3d = create_3d_plot(data_dir + 'Xkd_i{}.json'.format(i),isomin=1e3,isomax=3e4,
                surface_count=14)

        opacity = 0.3
        add_plane(fig3d,[0,1,0],[0,0,1],shift=[0.5,0,0],color=colors[1],opacity=opacity,name='[100] plane',visible='legendonly')
        add_plane(fig3d,[1,0,0],[0,0,1],shift=[0,0.5,0],color=colors[1],opacity=opacity,name='[010] plane',visible='legendonly')
        add_plane(fig3d,[1,1,0],[0,0,1],shift=[0,0,0],color=colors[2],opacity=opacity,name='[-110] plane',visible='legendonly')
        add_plane(fig3d,[1,-1,0],[0,0,1],shift=[0,1,0],color=colors[2],opacity=opacity,name='[110] plane',visible='legendonly')
    else:
        fig3d = go.Figure()
    return fig3d

fig3d = plot_3d_cb(30)

figp1 = plotly_plane(data_dir + 'plane1.json',bands=[])
add_line(figp1,y0=0.5,name='line 1',dash='dash')

figb1_1 = plot_bands(data_dir + 'bands_1_1.json',title='Bands and Berry curvature along line 1',ylim=(-0.1,0.1))
add_circle(figb1_1,0.2323,0.01280,color=colors[3])
add_circle(figb1_1,0.7676,0.01280,color=colors[3])

with open(data_dir + 'deg_bands.json') as f:
    Es = json_tricks.load(f)
fig_bands_plane = plotly_plane(data_dir + 'deg_bands.json',bands=[])

#fig_bands_plane = px.imshow(1/np.abs(Es.T),origin='lower',
#        color_continuous_scale='blues',x=np.linspace(0,1,50,endpoint=False),y=np.linspace(0,1,50,endpoint=False))
#fig_bands_plane.update_xaxes(range=[0,1],autorange=False)
#fig_bands_plane.update_yaxes(range=[0,1],autorange=False)
#fig_bands_plane.update_layout(coloraxis_colorbar=dict(yanchor="top", y=1, x=0))

layout = html.Div([
    html.H1(children='CeTe2'),
    dcc.Link('Link to Materials Project', href='https://materialsproject.org/materials/mp-505536'),

    html.P("""

    """),

    html.H3('3D plot of the Berry curvature distribution in the Brillouin zone'),
    html.P("""
    The following plot shows the distribution of the Berry curvature in the reciprocal space. The plot is given in
    coordinates of the reciprocal lattice vectors of the primitive lattice. The plot does not show the first Brillouin
    zone, but rather a unit cell spanned by the reciprocal lattice vectors. This system is tetragonal, which means that
    this cell differs from the first Brillouin zone only by translation.
    """),
    html.P("""
    We find that in this material the hotspots are mostly localized in the [100], [010], [110], [-110] mirror planes.
    Here the [100], [010] mirror planes associated with the hotspots are planes that do not go through the Gamma point,
    but are instead located at the edge of brillouin zone. In this material these mirror planes are peculiar since 
    all the bands are degenerate everywhere within these planes both with and without spin-orbit coupling. Unusually,
    the hotspots appear to be associated with crossing of bands with opposite spin.
    """),
    html.P("""
    The hotspots in the [110] and [-110] planes are possibly connected to nodal lines, however the interepretation is
    not very clear here due to large number of bands and a large spin-orbit coupling, which causes significant differences
    between the relativistic and non-relativistic bands."""),

    html.Div([
    dbc.Checklist(options=[{'label' : 'High resolution plot', 'value' : 1}],id=prefix+'button_prec',switch=True),
    dbc.Alert("""The high resolution plot shows the Berry curvature distribution more clearly,
    but can be slow to load or even unstable!""", color="warning"),]),

    dbc.Button("Show mirror planes", outline=True, color="primary", className="mr-1", id=prefix+"button_show"),
    dbc.Button("Hide mirror planes", outline=True, color="primary", className="mr-1", id=prefix+"button_hide"),
    dbc.Alert("You can also show or hide individual planes by clicking on the legend.", color="info"),

    dbc.Container(
    dcc.Graph(
        id=prefix+'fig_3d',
        figure=fig3d
        )
    ),

    html.H3('Berry curvature distribution in the [010] plane'),
    html.P(""""""),
    dbc.Container(
        dcc.Graph(
            id=prefix+'plane1',
            figure=figp1
            )
        ),

    html.P("""Within this plane all the bands are double degenerate both with and without spin-orbit coupling.
              The degenerate bands have the same spin. The hotspots appear to be related to crossing of two bands
              (each double degenerate) with opposite spin. Such crossings happen commonly without spin-orbit coupling
              and are split by the spin-orbit coupling, similarly to the nodal lines. They typically don't lead to large
              Berry curvature, however. It is possible that in this case the fact that the bands are double degenerate plays 
              an important role.
              """),
    dbc.Container(
        dcc.Graph(
            id=prefix+'bands1_1',
            figure=figb1_1
            )
        ),
    html.P("""The green circles denote the crossing associated with the hotspots.
              """),

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

