import numpy as np
from scipy.interpolate import RegularGridInterpolator
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json_tricks

def interpolate_to_new_grid(Xkd,nk):
    shape = Xkd.shape
    xyz = tuple([np.linspace(0,1,shape[i],endpoint=False) for i in range(3)])
    intp = RegularGridInterpolator(xyz,Xkd)
    kpts = []
    for i in range(nk):
        for j in range(nk):
            for k in range(nk):
                kpts.append(np.array([float(i),float(j),float(k)])/nk)
    return np.array(kpts),intp(kpts)

def create_3d_plot(fname,isomin=1e3,isomax=1e4,surface_count=17):

    #Xkd = np.load('Eu2SeO2.npy')
    #kpts,Xkdi = interpolate_to_new_grid(Xkd,30)

    try:
        with open(fname,'r') as f:
            inp = json_tricks.load(f)
            kpts = inp['kpts']
            Xkdi = inp['Xkdi']
            ran = inp['ran']
    except:
        with open(fname,'r') as f:
            kpts,Xkdi = json_tricks.load(f)
        ran = None

    #fig = go.Figure(layout={'height': 800, 'width': 800, 'title': 'Berry curvature distribution'})
    #layout = {'height': 800, 'width': 1000, 'title': 'Berry curvature distribution'}
    layout = {'autosize': True, 'height': 800,}
    fig = go.Figure(layout=layout)
    fig.add_volume(
        x=kpts[:,0],
        y=kpts[:,1],
        z=kpts[:,2],
        value=np.abs(Xkdi),
        isomin=isomin,
        isomax=isomax,
        opacity=0.1, # needs to be small to see through all surfaces
        surface_count=surface_count, # needs to be a large number for good volume rendering
        name='Berry curvature',
        visible=True
        )

    fig.update_traces(showlegend=True)
    fig.update_layout(legend=dict(yanchor="top", y=1, x=0))
    if ran is None:
        fig.update_layout(scene=dict(
            xaxis=dict(range=[0,1]),
            yaxis=dict(range=[0,1]),
            zaxis=dict(range=[0,1]),
            ))
        fig.update_layout(scene_aspectmode='cube')
    else:
        fig.update_layout(scene=dict(
            xaxis=dict(range=ran[0]),
            yaxis=dict(range=ran[1]),
            zaxis=dict(range=ran[2]),
            ))

    return fig

def plotly_plane(fname,vmax=None,vmax_sf=3,bands=None,legend=True,width=3,
        legendonlybands=None):

    with open(fname) as f:
        Xkd_p,crossing_ks_p = json_tricks.load(f)

    if vmax is None:
        vmax = np.max(np.abs(Xkd_p))/vmax_sf

    fig = px.imshow(np.abs(Xkd_p.T),origin='lower',color_continuous_scale='blues',zmax=vmax,
                x=np.linspace(0,1,Xkd_p.shape[1],endpoint=False),y=np.linspace(0,1,Xkd_p.shape[0],endpoint=False))

    colors = px.colors.qualitative.G10

    if bands is None:
        bands = range(len(crossing_ks_p))

    if legendonlybands is None:
        legendonlybands = []

    bands_vis = []
    for b in bands:
        if b in legendonlybands:
            bands_vis.append('legendonly')
        else:
            bands_vis.append(True)

    for i,b in enumerate(bands):
        fig.add_scattergl(x=crossing_ks_p[b][:,0],y=crossing_ks_p[b][:,1],mode='markers'
                ,name='nodal line {}'.format(b),visible=bands_vis[i],
                marker={'color':colors[b+1],'size':width})
    fig.update_xaxes(range=[0,1],autorange=False,constrain="domain")
    fig.update_yaxes(range=[0,1],autorange=False)
    if legend:
        fig.update_layout(coloraxis_colorbar=dict(yanchor="top", y=1, x=-0.05))
    fig.update_layout(height=600,autosize=True)
    fig.update_xaxes(automargin=True)
    #if aspect_ratio is not None:
    #    fig.update_layout(yaxis=dict(scaleanchor="x", scaleratio=aspect_ratio))
    fig.update_layout(margin=dict(
        l=0,
    )),

    return fig

def show_planes(fig):
    fig.update_traces(visible=True,selector=dict(type='surface'))
    return fig

def hide_planes(fig):
    fig.update_traces(visible='legendonly',selector=dict(type='surface'))
    return fig

def create_plane(a1,a2,shift=None,nps=5):
    a1 = np.array(a1)
    a2 = np.array(a2)
    nps = 5
    pps = np.linspace(0,1,nps)
    pts = np.zeros((nps,nps,3))
    if shift is None:
        shift = np.array([0,0,0])
    else:
        shift = np.array(shift)
    for i,a in enumerate(pps):
        for j,b in enumerate(pps):
            pts[i,j,:] = a1 * a + a2 * b + shift
    return pts

def add_plane(fig,a1,a2,shift=None,nps=5,color='#636EFA',opacity=0.5,name='',visible=None,legendgroup=None):
    pts = create_plane(a1,a2,shift,nps)
    colorscale = [[0, color], [1, color]]
    fig.add_surface(x=pts[:,:,0],y=pts[:,:,1],z=pts[:,:,2],surfacecolor=np.zeros((nps,nps)),
                opacity=opacity,showscale=False,colorscale=colorscale,name=name,visible=visible,
                legendgroup=legendgroup)

    fig.update_traces(showlegend=True)

def plot_bands(fname,title=None,ylim=None):
    with open(fname) as f:
        bands_data = json_tricks.load(f)

    fig = make_subplots(rows=2, cols=1, 
                    shared_xaxes=True, 
                    vertical_spacing=0.01)

    nbands0 = bands_data['Eks0'].shape[1]
    for b in range(nbands0):
        if b == 0:
            name = 'non-rel spin-up'
            showlegend = True
        else:
            name = 'band{}'.format(b)
            showlegend = False
        fig.add_scatter(x=bands_data['xdata'],y=bands_data['Eks0'][:,b],name=name,
                        line={'dash':'dot','color':'black'},row=1, col=1,
                       showlegend=showlegend)
        
    nbands1 = bands_data['Eks1'].shape[1]
    for b in range(nbands0):
        if b == 0:
            name = 'non-rel spin-down'
            showlegend = True
        else:
            name = 'band{}'.format(b)
            showlegend = False
        fig.add_scatter(x=bands_data['xdata'],y=bands_data['Eks1'][:,b],name=name,
                        line={'dash':'dash','color':'black'},row=1, col=1,
                       showlegend=showlegend)
        
    nbands = bands_data['Eksr'].shape[1]
    for b in range(nbands):
        if b == 0:
            name = 'rel'
            showlegend = True
        else:
            name = 'band{}'.format(b)
            showlegend = False
        fig.add_scatter(x=bands_data['xdata'],y=bands_data['Eksr'][:,b],name=name,
                        line={'color':'black'},row=1, col=1,showlegend=showlegend)        

    if ylim is None:
        ylim = bands_data['ylim']
    fig.update_yaxes(range=ylim,autorange=False,title='Ev [meV]',row=1,col=1)
    xran = [np.amin(bands_data['xdata']),np.amax(bands_data['xdata'])]
    fig.update_xaxes(range=xran)

    fig.add_shape(
            dict(
            type="line",
            x0=0,
            y0=0,
            x1=1,
            y1=0,
            line=dict(
                color="black",
                width=1
            )
    ))
        
    fig.add_scatter(x=bands_data['xdata'],y=bands_data['bc'][:,2],line={'color':px.colors.qualitative.Vivid[1]},row=2, col=1,
            name='Berry curvature')

    fig.update_yaxes(title='Berry curvature [?]',row=2,col=1)
        

    fig.update_layout(title=title,height=600,autosize=True)

    return fig

def add_circle(fig,x,y,size=15,width=3,color="LightSeaGreen",name=None):
    fig.add_shape(
        # unfilled circle
        dict(
            type="circle",
            xsizemode='pixel',
            ysizemode='pixel',
            xref="x",
            yref="y",
            xanchor = x,
            yanchor = y,
            x0=-size,
            y0=-size,
            x1=size,
            y1=size,
            line=dict(
                color=color,
                width=width
            )
        ))
    if name is not None:
        fig.add_scatter(x=[0],y=[-10],line=dict(color=color),name=name)

def add_line(fig,x0=0,x1=1,y0=0.5,y1=None,name=None,dash='dash'):

    if y1 is None:
        y1 = y0

    line=dict(
        color="gray",
        width=3,
        dash=dash
    )

    if name is None:
        showlegend=False
    else:
        showlegend=True
    fig.add_scatter(x=[x0,x1],y=[y0,y1],line=line,mode="lines",name=name,showlegend=showlegend)


