from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from app import app
from common import Navbar, column_names, inv_column_names

df = pd.read_json('data/paper_database.json')

columns =  [
    'Total Magnetization',
    'Average Magnetization',
    'Maximum Z',
    'Number of mirrors',
    'Number of symmetries',
    'AHE magnitude',
    'Conductivity xx'
    ]
axis_options = [{'label': c, 'value': column_names[c]} for c in columns]

def create_hist_plot(x,y,z,grange=None):

    if grange is None:
        dff = df
    else:
        dff = df[ (df['norm_h'] > grange[0]) &  (df['norm_h'] < grange[1]) ] 

    if z is None:
        dfz = None
    else:
        dfz = dff[z]

    if x is None:
        raise Exception('Need at least value for the x axis')
    dfx = dff[x]

    if z is None:
        histfunc = None
    else:
        histfunc = "avg"

    if y is None:
        fig = px.histogram(x=dfx,y=dfz,histfunc=histfunc)
        fig.update_xaxes(title_text=inv_column_names[x])
        if z is None:
            fig.update_yaxes(title_text='count')
        else:
            fig.update_yaxes(title_text='avg of {}'.format(inv_column_names[z]))
    else:
        dfy = dff[y]
        fig = px.density_heatmap(dff,x=x, y=y, z=z, histfunc=histfunc,
                                 marginal_x="violin", marginal_y="violin",
                                 labels=inv_column_names)
        fig.update_layout(
        autosize=False,
        width=600,
        height=600,)

        #fig.update_xaxes(title_text=inv_column_names[x])
        #fig.update_yaxes(title_text=inv_column_names[y])
        if z is None:
            fig.update_coloraxes(colorbar_title={'text':'count'})
        else:
            #fig.update_coloraxes(colorbar_title={'text': 'avg of {}'.format(inv_column_names[z])})
            fig.update_coloraxes(colorbar_title={'text': 'avg of {}'.format(inv_column_names[z]),'side':'right'})
    return fig

def create_layout():
    fig_hist = create_hist_plot('total_magnetization','maxZ','norm_h')
    layout = dbc.Container(html.Div([
        Navbar(),

        html.H2('Statistics',style={"margin-top": "10px"}),
        html.P('Select up to three variables to plot their relationship.'),

        html.Ul([html.Li('If only x is specified, then a simple histogram is plotted.'),
            html.Li('If x and the averaging quantity is specified then the value in '
                    'each bin gives the average value of the averaging quantity.'
                    'The plot then shows the relation between x and the averaging quantity.'),
            html.Li('If x and y are specified then a 2D histogram is plotted. '
                    'The 2D histogram also shows the distribution of each variable using a violin plot'),
            html.Li('If x,y and averaging quantity are specified then a 2D histogram is plotted,'
                    'where the value in each bin corresponds to the average value of the averaging quantity.'),
                 ]),

        html.P('It is also possible to filter by AHE magnitude,'
               ' i.e. if the filtering is used only materials with AHE within the given range'
               ' will be used for plotting.'),

        html.Div(['X axis:',
              dcc.Dropdown(
                  id='dropdown_hist2d_x',
                  options=axis_options,
                  value='total_magnetization'
              )], style={"width": "30%"}),

        html.Div(['Y axis:',
              dcc.Dropdown(
                  id='dropdown_hist2d_y',
                  options=axis_options,
                  value='maxZ',
              )], style={"width": "30%"}),

        html.Div(['Averaging:',
              dcc.Dropdown(
                  id='dropdown_hist2d_z',
                  options=axis_options,
                  value='norm_h',
              )], style={"width": "30%"}),
        html.H4('Filter AHE magnitude:',style={"margin-top": "10px"}),
        html.Div([
            dcc.RangeSlider(
                id='norm_g-range-slider',
                min=0,
                max=df['norm_h'].max(),
                step=1,
                # marks = {i:str(int(i)) for i in np.linspace(0,5000,5,endpoint=True)},
                marks={0: '0', 1000: '1000', 2000: '2000', 3000: '3000', 4000: '4000', 5000: '5000'},
                value=[0, df['norm_h'].max()]
            ),
            html.Div(id='output-container-range-slider')
        ], style={"width": "50%"}),

        dbc.Container(
            dcc.Graph(
                id='fig-hist2d',
                figure=fig_hist
                )
            ),


        ]))

    return layout

@app.callback(
    Output('fig-hist2d', 'figure'),
    Input('dropdown_hist2d_x', 'value'),
    Input('dropdown_hist2d_y', 'value'),
    Input('dropdown_hist2d_z', 'value'),
    Input('norm_g-range-slider','value')
)
def update_histogram(value_x,value_y,value_z,grange):
    return create_hist_plot(value_x,value_y,value_z,grange)
    
@app.callback(
    Output('output-container-range-slider', 'children'),
    Input('norm_g-range-slider', 'value'))
def update_range_output(value):
    return 'Selected range: {}'.format(value)
