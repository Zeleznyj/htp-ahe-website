from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table
from dash_table.Format import Format, Scheme
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import h5py

#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from app import app
from common import Navbar, column_names, inv_column_names

df = pd.read_json('data/paper_database.json')
dfs = df[['formula','id','norm_g','Hall_angle','spacegroup','magnetic_symmetry','cond_xx',
          'gamma_convergence','k_convergence','total_magnetization']]
gammas = [0.0001, 0.0005, 0.001, 0.005, 0.01]

def create_cond_figure(X,offdiag=False):

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=gammas, y=X[0,:,0,0,0],
                        mode='lines',
                        name='xx'
                        ))
    fig.add_trace(go.Scatter(x=gammas, y=X[0,:,0,1,1],
                        mode='lines',
                        name='yy'))
    fig.add_trace(go.Scatter(x=gammas, y=X[0,:,0,2,2],
                        mode='lines',
                        name='zz'))
    if offdiag:
        fig.add_trace(go.Scatter(x=gammas, y=X[0,:,0,0,1],
                            mode='lines',
                            name='xy'))
        fig.add_trace(go.Scatter(x=gammas, y=X[0,:,0,0,2],
                            mode='lines',
                            name='xz'))
        fig.add_trace(go.Scatter(x=gammas, y=X[0,:,0,1,2],
                            mode='lines',
                            name='xz'))
    fig.update_xaxes(type="log")
    if not offdiag:
        fig.update_yaxes(type="log")

    fig.update_layout(
        autosize=False,
        width=800,
        height=600,
    )
    fig.update_xaxes(title_text=r'$\Gamma\  \text{[eV]}$')
    fig.update_yaxes(title_text=r'Conductivity [S/cm]')

    return fig

def create_cond_offdiag_figure(X):

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=gammas, y=X[0,:,0,0,1],
                             mode='lines',
                             name='xy'))
    fig.add_trace(go.Scatter(x=gammas, y=X[0,:,0,0,2],
                             mode='lines',
                             name='xz'))
    fig.add_trace(go.Scatter(x=gammas, y=X[0,:,0,1,2],
                             mode='lines',
                             name='xz'))

    fig.update_xaxes(type="log")

    fig.update_layout(
        autosize=False,
        width=800,
        height=600,
    )
    fig.update_xaxes(title_text=r'$\Gamma\  \text{[eV]}$')
    fig.update_yaxes(title_text=r'Conductivity [S/cm]')

    return fig

def create_AHE_figure(X):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=gammas, y=X[1,:,0,0,1],
                        mode='lines',
                        name='xy'))
    fig.add_trace(go.Scatter(x=gammas, y=X[1,:,0,0,2],
                        mode='lines',
                        name='xz'))
    fig.add_trace(go.Scatter(x=gammas, y=X[1,:,0,1,2],
                        mode='lines',
                        name='xz'))
    fig.update_xaxes(type="log")

    fig.update_layout(
        autosize=False,
        width=800,
        height=600,
    )
    fig.update_xaxes(title_text=r'$\Gamma\  \text{[eV]}$')
    fig.update_yaxes(title_text=r'AHE [S/cm]')

    return fig

def plot_bands(idd):

    filepath = 'data/bands_all/band-{}.hdf5'.format(idd)

    if not path.isfile(filepath):
        return None

    with h5py.File(filepath, 'r') as f:
        kdists = np.array(f['kdists'])
        kdists2 = np.array(f['kdists2'])
        erg = np.array(f['erg'])
        erg2 = np.array(f['erg2'])
        points = list(f['points'])

    fig = go.Figure()
    for b in range(erg.shape[0]):
        fig.add_trace(go.Scatter(x=kdists,y=erg[b,:],line={'color':'black','width':5}))
        fig.add_trace(go.Scatter(x=kdists2,y=erg2[b,:],line={'color':'red','dash':'dash'}))
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = [float(points[i][1].decode()) for i in range(len(points))],
            ticktext = [points[i][0].decode() for i in range(len(points))]
        )
    )
    fig.update_layout(showlegend=False)
    fig.update_layout(
        autosize=False,
        width=800,
        height=600,)

    #fig.update_yaxes(title_text=r'$E - E_F \  \text{[eV]}$')
    fig.update_yaxes(title_text=r'E - E_F [eV]')

    return fig

def get_data_type(name):
    if name in ['norm_g','spacegroup','magnetic_symmetry','Hall_angle','total_magnetization',
                'gamma_convergence','k_convergence']:
        return 'numeric'
    else:
        return 'text'

def get_data_format(name):
    if name in ['cond_xx','norm_g','cond_xx','total_magnetization','gamma_convergence','k_convergence']:
        return Format(precision=2, scheme=Scheme.fixed)
    elif name in ['Hall_angle']:
        return Format(precision=3, scheme=Scheme.fixed)
    else:
        return None

def create_layout():

    fig = go.Figure()
    fig_AHE = go.Figure()

    layout = dbc.Container([
        html.Div(
        [
            Navbar(),
            html.H2('Materials Explorer',style={"margin-top": "10px"}),
            html.Div(['Search by elements (separate by space):',dcc.Input(
                id="input_search",
                type="search",
                placeholder="",
                )]),
            dbc.Alert('Select material to show more detailed results. The table also supports sorting and filtering'
                      '(you can use operators such as =, > or <). ',
                      color="primary",
                      style={"margin-top": "10px"}),
            dash_table.DataTable(
                id='table',
                columns=[{"name": inv_column_names[i], "id": i,
                          "format": get_data_format(i),
                          "type": get_data_type(i)} for i in dfs.columns],
                data=dfs.to_dict('records'),
                page_action='native',
                page_current= 0,
                page_size= 10,
                sort_action="native",
                filter_action="native",
                sort_mode='multi',
                row_selectable='single',
                fill_width=False,
                sort_by = [{'column_id':'norm_g','direction':'desc'}]
                ),
            html.Div([

                html.H2(id='material_name',style={"margin-top": "80px"}),

                
                dbc.Alert(["Visit ", html.A('Materials Project',
                    id='materials_project_link',href='.')," for information about structure, stability, etc."],
                    color="primary"),

                html.H4("Bandstructure"),
                html.Div(
                    dbc.Alert("Bands not available!", color="warning",),
                    id='band_alert',hidden=True
                ),
                dbc.Container([
                dcc.Graph(
                    id='fig_bands',
                    figure=go.Figure()
                    ),
                html.P('Black lines denote the FPLO bands, red bands are the bands of the Wannier Hamiltonian.')
                ]),

                html.H4("AHE Gamma dependence"),
                dbc.Container(
                dcc.Graph(
                    id='fig_AHE',
                    figure=fig_AHE
                    )
                ),

                html.H4("Conductivity Gamma dependence"),
                dbc.Container(
                dcc.Graph(
                    id='fig_cond',
                    figure=fig
                    )
                ),

                html.H4("Offdiagonal Conductivity Gamma dependence"),
                dbc.Container(
                    dcc.Graph(
                        id='fig_cond_offdiag',
                        figure=fig
                    )
                ),
            ],id='material_div',hidden=True)
        ])
        ])

    return layout

@app.callback(
    Output('table', 'data'),
    Input('input_search', 'value')
)
def update_table(value):
    def contains(row):
        for ele in value.split():
            print(value.split())
            if ele not in row['formula']:
                return False
        return True
        
    if value == '' or value is None:
        return dfs.to_dict('records')
    return dfs[dfs.apply(contains,axis=1)].to_dict('records')

@app.callback(
    Output('fig_cond', 'figure'),
    Output('fig_cond_offdiag', 'figure'),
    Output('fig_AHE', 'figure'),
    Output('fig_bands', 'figure'),
    Output('material_name','children'),
    Output('materials_project_link','href'),
    Output('material_div','hidden'),
    Output('band_alert','hidden'),
    Input('table', 'selected_row_ids')
)
def test_row(selected_rows_ids):
    if selected_rows_ids is None:
        return (go.Figure(),
                go.Figure(),
               go.Figure(),
               go.Figure(),
               'Material',
               '.',
               True,
               True
               )
    else:
        idd = selected_rows_ids[0]
        row = df[df['id'] == idd].iloc[0]
        X = np.array(row['X-250-final'])
        band_plot = plot_bands(idd)
        if band_plot is None:
            band_plot = go.Figure()
            band_warning = False
        else:
            band_warning = True
        return (create_cond_figure(X),
                create_cond_offdiag_figure(X),
               create_AHE_figure(X),
                band_plot,
               row['formula'],
               'https://materialsproject.org/materials/{}/'.format(idd),
               False,
               band_warning,
               )
