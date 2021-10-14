try:
    from aiida.orm import load_node
    aiida_available = True
except:
    aiida_available = False

import numpy as np
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt

import plotly.graph_objects as go
import plotly.express as px

try:
    from analyze_res import read_k_resolved
    analyze_res_available = True
except:
    analyze_res_available = False


from htp.analysis.crossings_finder import get_Eks,get_slabify_path,get_hamdata_path,get_conv2prim_T

def get_Xkd(pk):
    if not aiida_available:
        raise Exception("Need aiid")
    if not analyze_res_available:
        raise Exception("Need analyze_res")
    n = load_node(pk)
    Xk = read_k_resolved(n.outputs.retrieved._repository._get_base_folder().get_abs_path('k_resolved.out'))
    Xkd = Xk[:,:,:,0,1,5].data
    return Xkd

def plot_k_contribution(Xkd,maxt=None):
    
    Xkdl = Xkd.reshape(Xkd.shape[0]**3)
    sums = []
    lengths = []
    
    if maxt is None:
        maxt = np.max(np.abs(Xkdl))
    tres = np.logspace(1,np.log10(maxt),200) 
    
    tot_sum = np.sum(Xkdl)
    tot_length = Xkdl.shape[0]
    
    for i in tres:
        Xkdl_s = Xkdl[np.abs(Xkdl) < i]
        sums.append(np.sum(Xkdl_s)/tot_sum)
        lengths.append(float(Xkdl_s.shape[0])/tot_length)
    plt.figure()
    plt.plot(tres,sums)
    plt.plot(tres,lengths)
    plt.xscale('log')

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

def get_plane_coordinates(k1,k2,shift,T,k):
    if T is not None:
        k = np.dot(np.linalg.inv(T),k)
    A = np.column_stack([k1,k2,np.cross(k1,k2)])
    k_p = np.linalg.solve(A,k-shift)
    if abs(k_p[2]) > 1e-12:
        raise Exception('k-point does not lie in the plane')
    return k_p[0:2]

def interpolate_to_plane(Xkd,crossing_ks=None,k1=None,k2=None,shift=np.array([0,0,0]),T=None,nk=100):

    intp = get_interpolator(Xkd)    

    Xkd_p = np.zeros((nk,nk))
    for i in range(nk):
        for j in range(nk):
            k_ij = (float(i)/nk)*k1 + (float(j)/nk)*k2 + shift
            if T is not None:
                k_ij = np.dot(T,k_ij)
            k_ij = [x % 1 for x in k_ij]
            Xkd_p[i,j] = intp(k_ij)

    if crossing_ks is not None:
        crossing_ks_p = []
        for i in range(len(crossing_ks)):
            crossing_ks_p.append([])
            for j in range(len(crossing_ks[i])):
                crossing_ks_p[i].append(get_plane_coordinates(k1,k2,shift,T,crossing_ks[i][j]))
            crossing_ks_p[i] = np.array(crossing_ks_p[i])
    else:
        crossing_ks_p = None

    return Xkd_p,crossing_ks_p

def plot_plane(Xkd,crossing_ks=None,k1=None,k2=None,shift=np.array([0,0,0]),T=None,
        nk=100,bands=None,color=None,s=5,alpha=0.5,vmax=None,vmax_sf=3,legend=True):
    
    Xkd_p,crossing_ks_p = interpolate_to_plane(Xkd,crossing_ks,k1,k2,shift,T,nk)
        
    plt.figure()
    ax = plt.gca()
    if vmax is None:
        vmax = np.max(np.abs(Xkd_p))/vmax_sf
    p = ax.imshow(np.abs(Xkd_p.T),extent=(0,1,0,1),origin='lower',cmap=plt.get_cmap('Blues'),
                  vmin=0,vmax=vmax)
    plt.colorbar(p)

    if crossing_ks is not None:
        colors = ['C1','C2','C3','C5','C6']
        if bands is None:
            bands = range(len(crossing_ks_p))
        for i,b in enumerate(bands):
            plt.scatter(crossing_ks_p[b][:,0],crossing_ks_p[b][:,1],label=str(b),s=s,alpha=alpha,color=colors[i])

    if legend:
        plt.legend()
    
    return Xkd_p,crossing_ks_p

def plotly_plane(Xkd_p,crossing_ks_p=None,vmax=None,vmax_sf=3,bands=None,legend=True):
    if vmax is None:
        vmax = np.max(np.abs(Xkd_p))/vmax_sf

    fig = px.imshow(np.abs(Xkd_p.T),origin='lower',color_continuous_scale='blues',zmax=vmax,
                x=np.linspace(0,1,100,endpoint=False),y=np.linspace(0,1,100,endpoint=False))

    for b in [0,1,2,3,4,5,6]:
        fig.add_scattergl(x=crossing_ks_p[b][:,0],y=crossing_ks_p[b][:,1],mode='markers',name='band {}'.format(b))
    fig.update_xaxes(range=[0,1],autorange=False)
    fig.update_yaxes(range=[0,1],autorange=False)
    if legend:
        fig.update_layout(coloraxis_colorbar=dict(yanchor="top", y=1, x=0))

    return fig

def plot_hist(Xkd,bins=1000):

    nk = Xkd.shape[0]
    
    vals,bins,patches = plt.hist(np.abs(Xkd.reshape(nk*nk*nk)),bins=bins)
    plt.yscale('log')
    
    int_vals = []
    bins_middle = []
    sum_int_vals1 = []
    sum_int_vals2 = []
    for i in range(len(vals)):
        bm = bins[i]+ (bins[i+1]-bins[i])/2
        bins_middle.append(bm)
        int_vals.append(bm * vals[i])
    for i in range(len(int_vals)):
        sum_int_vals1.append(sum(int_vals[:i]))
        sum_int_vals2.append(sum(int_vals[i:]))
    plt.figure()
    plt.plot(bins_middle,int_vals)
    plt.yscale('log')
    plt.figure()
    plt.xscale('log')
    plt.plot(bins_middle,sum_int_vals1)
    plt.plot(bins_middle,sum_int_vals2)

def get_slabify_pk(pk):
    return get_slabify_path(get_hamdata_path(pk))

def get_reciprocal_lattice(B):
    V = np.dot(B[:,0],np.cross(B[:,1],B[:,2]))
    C = np.zeros((3,3))
    C[:,0] = 2 * np.pi * np.cross(B[:,1],B[:,2]) / V
    C[:,1] = 2 * np.pi * np.cross(B[:,2],B[:,0]) / V
    C[:,2] = 2 * np.pi * np.cross(B[:,0],B[:,1]) / V
    return C



def get_interpolator(Xkd):
    shape = Xkd.shape
    shape2 = [s+1 for s in shape]
    Xkd2 = np.zeros(shape2)
    Xkd2[:shape[0],:shape[1],:shape[2]] = Xkd
    Xkd2[-1,:shape[1],:shape[2]] = Xkd[0,:,:]
    Xkd2[:shape[0],-1,:shape[2]] = Xkd[:,0,:]
    Xkd2[:shape[0],:shape[1],-1] = Xkd[:,:,0]
    
    xyz = tuple([np.linspace(0,1,shape2[i],endpoint=True) for i in range(3)])
    intp = RegularGridInterpolator(xyz,Xkd2)
    
    return intp

def plot_bands(s=None,sr=None,ks=None,convert=False,k_min=0,k_max=1,k_endpoint=True,ylim=(-0.2,0.2),Xkd=None,berry=False):

    if ks is None:
        raise Exception('ks must be specified')

    if convert:
        T = get_conv2prim_T(sr)
        ks_c = []
        for k in ks:
            k2 = np.dot(T,k)
            k2_1 = [x % 1 for x in k2]
            ks_c.append(k2_1)
                    
        ks = ks_c

    if s is not None:
        Eks0 = get_Eks(s,ks,ms=0)
        Eks1 = get_Eks(s,ks,ms=1)

    if sr is not None:
        if not berry:
            Eksr = get_Eks(sr,ks)
        else:
            Eksr,bcs = get_Eks(sr,ks,berry=True)

            bcf = np.zeros(bcs.shape)
            for i in range(bcs.shape[0]):
                for j in range(bcs.shape[2]):
                    if Eksr[i,j] < 0:
                        bcf[i,:,j] = bcs[i,:,j]
                    else:
                        bcf[i,:,j] = 0

    nk = len(ks)

    n_plots = 1
    if Xkd is not None:
        n_plots +=1
    if berry:
        n_plots +=1

    plot_i = 1

    plt.subplot(n_plots,plot_i,1)

    if s is not None:
        plt.plot(np.linspace(k_min,k_max,nk,endpoint=k_endpoint),Eks0,ls='dotted')
        plt.plot(np.linspace(k_min,k_max,nk,endpoint=k_endpoint),Eks1,ls='--')
    if sr is not None:
        plt.plot(np.linspace(k_min,k_max,nk,endpoint=k_endpoint),Eksr,ls='-')
    plt.hlines(0,k_min,k_max)
    plt.ylim(ylim)

    if Xkd is not None:

        plot_i += 1
        intp = get_interpolator(Xkd)

        ks_b = intp(ks)

        plt.subplot(n_plots,1,plot_i)
        plt.plot(np.linspace(k_min,k_max,nk,endpoint=k_endpoint),ks_b)

    if berry:
        plot_i += 1
        plt.subplot(n_plots,1,plot_i)
        bcf_tot = np.sum(bcf,axis=2)
        plt.plot(np.linspace(k_min,k_max,nk,endpoint=k_endpoint),bcf_tot[:,2])

def relk_to_fplok(s,k):
    Rcell = s.hamdataRCell()*s.kscale
    b1 = Rcell[:,0]
    b2 = Rcell[:,1]
    b3 = Rcell[:,2]
    return b1 * k[0] + b2 * k[1] +b3 * k[2]

def fplok_to_relk(s,k):
    Rcell = s.hamdataRCell()*s.kscale
    return np.linalg.solve(Rcell,k)



def transform_Xkd(T,Xkd,nk):
       
    intp = get_interpolator(Xkd)
    
    Xkdt = np.zeros((nk,nk,nk))
    
    kpts = np.zeros((nk,nk,nk,3))
    
    for i,ki in enumerate(np.linspace(0,1,nk,endpoint=False)):
        for j,kj in enumerate(np.linspace(0,1,nk,endpoint=False)):
            for l,kl in enumerate(np.linspace(0,1,nk,endpoint=False)):
                k1 = [ki,kj,kl]
                k2 = np.dot(T,k1)
                k2_1 = [x % 1 for x in k2]
                kpts[i,j,l,:] = k2_1
                
    return intp(kpts)



        
        
