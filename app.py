import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json_tricks

#from plotly.express.colors.qualitative import vivid

from interpolate import interpolate_to_new_grid,plotly_plane,add_plane

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

#Xkd = np.load('Eu2SeO2.npy')
#kpts,Xkdi = interpolate_to_new_grid(Xkd,30)

with open('Xkd.json','r') as f:
    kpts,Xkdi = json_tricks.load(f)

fig = go.Figure(layout={'height': 800, 'width': 800, 'title': 'Berry curvature distribution'})
fig.add_volume(
    x=kpts[:,0],
    y=kpts[:,1],
    z=kpts[:,2],
    value=np.abs(Xkdi),
    isomin=1e3,
    isomax=1e4,
    opacity=0.1, # needs to be small to see through all surfaces
    surface_count=17, # needs to be a large number for good volume rendering
    name='Berry curvature'
    )

opacity = 0.3
colors = px.colors.qualitative.Vivid
add_plane(fig,[1,1,0],[0,0,1],color=colors[0],opacity=opacity,name='[1-10] plane')
add_plane(fig,[1,-1,0],[0,0,1],shift=[0,1,0],color=colors[0],opacity=opacity,name='[110] plane')
add_plane(fig,[1,0,0],[0,0,1],shift=[0,0.5,0],color=colors[2],opacity=opacity,name='[010] plane')
add_plane(fig,[0,1,0],[0,0,1],shift=[0.5,0,0],color=colors[2],opacity=opacity,name='[100] plane')
fig.update_traces(showlegend=True)
#fig.update_layout(coloraxis_colorbar=dict(yanchor="top", y=1, x=0))
fig.update_layout(legend=dict(yanchor="top", y=1, x=0))


with open('plane3.json') as f:
    Xkd_p,cr_p = json_tricks.load(f)

fig2 = plotly_plane(Xkd_p,cr_p)
fig2.update_layout(height=600,width=900,title='[1-10] plane')

app.layout = html.Div(children=[
    html.H1(children='Eu2SeO2'),

#    html.Div(children='''
#        Berry curvature in k-space:.
#    '''),

    dcc.Graph(
        id='3d',
        figure=fig
    ),

    dcc.Graph(
        id='plane3',
        figure=fig2
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
