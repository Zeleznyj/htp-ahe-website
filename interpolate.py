import numpy as np
from scipy.interpolate import RegularGridInterpolator
import plotly.express as px
import plotly.graph_objects as go

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

def plotly_plane(Xkd_p,crossing_ks_p=None,vmax=None,vmax_sf=3,bands=None,legend=True):
    if vmax is None:
        vmax = np.max(np.abs(Xkd_p))/vmax_sf

    fig = px.imshow(np.abs(Xkd_p.T),origin='lower',color_continuous_scale='blues',zmax=vmax,
                x=np.linspace(0,1,100,endpoint=False),y=np.linspace(0,1,100,endpoint=False))

    if bands is None:
        bands = range(len(crossing_ks_p))
    for b in bands:
        fig.add_scattergl(x=crossing_ks_p[b][:,0],y=crossing_ks_p[b][:,1],mode='markers',name='band {}'.format(b))
    fig.update_xaxes(range=[0,1],autorange=False)
    fig.update_yaxes(range=[0,1],autorange=False)
    if legend:
        fig.update_layout(coloraxis_colorbar=dict(yanchor="top", y=1, x=0))

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

def add_plane(fig,a1,a2,shift=None,nps=5,color='#636EFA',opacity=0.5,name=''):
    pts = create_plane(a1,a2,shift,nps)
    colorscale = [[0, color], [1, color]]
    fig.add_surface(x=pts[:,:,0],y=pts[:,:,1],z=pts[:,:,2],surfacecolor=np.zeros((nps,nps)),
                opacity=opacity,showscale=False,colorscale=colorscale,name=name)
