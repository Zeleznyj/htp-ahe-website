from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import re
from fractions import Fraction
from collections import OrderedDict

import pandas as pd
import numpy as np
from numpy.linalg import norm

from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import WorkChainNode,CalcJobNode
from aiida.orm import load_node

from pymatgen import Structure
from pymatgen.core.sites import PeriodicSite
from pymatgen.util.coord import pbc_diff
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from htp.input.fplo_input import structure_to_fplo_new
from htp.scripts.database_scripts import get_linres_calculations
from htp.tools.symmetr_tools import get_symmetry_tensor,find_symmetry
from htp.input.mpstructure import change_magmom_basis
from htp.aiida_plugin.parsers import parse_fplo_output
from analyze_res import read_new

def get_n_sites_node(node):
    fplo_out =  node.outputs.result.get_content().splitlines()
    wyckoffs,sites_wps = read_wyckoffs(fplo_out)
    return len(sites_wps)

def get_n_sites(struct):

    struct_info = structure_to_fplo_new('/jakzel/Temp/',struct,FPLO_q_axis=[0,0,1])
    struct_new = Structure.from_dict(struct_info['struct'])
    #struct_prim = struct_new.get_primitive_structure()
    sym = SpacegroupAnalyzer(struct_new)
    struct_prim = sym.get_primitive_standard_structure()

    #print(struct)
    #print(struct_new)
    #print(struct_prim)

    return len(struct_prim.sites)

def get_linres_opt(nk):
    if nk == 125:
        linres_opt = {'calc': 'cond',            
         'formulas': [2, 12],
         'gammas': [0.0001, 0.0005, 0.001, 0.005, 0.01],
         'nk': 125}
    elif nk == 250:
        linres_opt = {'calc': 'cond',            
         'formulas': [2, 12],
         'gammas': [0.0001, 0.0005, 0.001, 0.005, 0.01],
         'nk': 250}
    else:
        linres_opt = None

    return linres_opt

def get_linres_calculations_fast(project=None,fplo_nk=None,linres_opt=None,finished_ok_only=False,q_axis=None):

    filters = {'extras.calculation':{'==':'linres'}}
    filters['extras']={'has_key':'workchain_pk'}
    if project is not None:
        filters['extras.project']={'==':project}
    if fplo_nk is not None:
        filters['extras.fplo_nk']={'==':fplo_nk}
    if linres_opt is not None:
        filters['extras.linres_opt']={'==':linres_opt}
    if finished_ok_only:
        filters['attributes.exit_status']={'==':0}
    if q_axis is not None:
        filters['extras.q_axis.0'] = {'==':q_axis[0]}
        filters['extras.q_axis.1'] = {'==':q_axis[1]}
        filters['extras.q_axis.2'] = {'==':q_axis[2]}

    qb = QueryBuilder()
    qb.append(CalcJobNode,
        filters=filters)
    
    all_calc = qb.all()

    workchain_pks = []
    node_pks = []
    for calc in all_calc:
        workchain_pks.append(calc[0].get_extra('workchain_pk'))
        node_pks.append(calc[0].pk)
    df_dict = {'fplo_pk':workchain_pks,'pk':node_pks}
    df = pd.DataFrame(data=df_dict)

    return df

def create_linres_dataframe(linres_calcs,columns=['id','spacegroup','ahe-xy','ahe-xz','ahe-yz','ahe-tot']):
    for column in columns:
        if column not in ['id','fplo_pk','spacegroup','exit_status','terminated','n_sites','ahe-xy',
                'ahe-xz','ahe-yz','ahe-tot','q_axis','gap','magnetic_moments','structure','cond_xx','X',
                'fplo_spacegroup','symmetry','magnetic_symmetry']:
            raise Exception('undefined column')
    df_dict = OrderedDict()
    df_dict['pk'] = linres_calcs.pk 
    columns_lists = [[] for i in range(len(columns))]
    for j,calc in linres_calcs.iterrows():
        pk = int(calc.pk)
        if len(set(['ahe-xy','ahe-xz','ahe-yz','ahe-tot','cond_xx','X']).intersection(set(columns))) > 0:
            try:
                X = get_calc_result(pk)
            except:
                X = None
        node = load_node(pk)
        for i,column in enumerate(columns):
            try:
                if column == 'id':
                    value = node.get_extra('id')
                if column == 'fplo_pk':
                    value = node.get_extra('workchain_pk')
                if column == 'spacegroup':
                    value = node.get_extra('nonmag_space_group_number')
                if column == 'q_axis':
                    value = node.get_extra('q_axis')
                if column == 'exit_status':
                    value = node.exit_status
                if column == 'terminated':
                    value = node.is_terminated
                if column == 'n_sites':
                    node_fplo = load_node(node.get_extra('workchain_pk')).called[1]
                    value = get_n_sites_node(node_fplo)
                if column in ['ahe-xy','ahe-xz','ahe-yz','ahe-tot','cond_xx','X']:
                    if X is not None:
                        if column == 'ahe-xy':
                            value = X[1,0,0,0,1].data
                        if column == 'ahe-xz':
                            value = X[1,0,0,0,2].data
                        if column == 'ahe-yz':
                            value = X[1,0,0,1,2].data
                        if column == 'cond_xx':
                            value = X[0,2,0,0,0].data
                        if column == 'ahe-tot':
                            value = norm([X[1,0,0,0,1].data,X[1,0,0,0,2].data,X[1,0,0,1,2].data])
                        if column == 'X':
                            value = X
                    else:
                        value = None
                if column in ['gap','magnetic_moments','structure']:
                    node_fplo = load_node(node.get_extra('workchain_pk')).called[1]
                    if column in ['gap','magnetic_moments']:
                        properties = node_fplo.outputs.properties.get_dict()
                        value = properties[column]
                    else:
                        value = node_fplo.outputs.struct_info.get_dict()
                if column == 'fplo_spacegroup':
                    value = get_fplo_spacegroup(node.get_extra('workchain_pk'))
                if column == 'symmetry':
                    value = get_calc_symmetry(node.get_extra('workchain_pk'))
                if column == 'magnetic_symmetry':
                    value = get_calc_symmetry(node.get_extra('workchain_pk'),get_group=True)
            except Exception as e:
                print(j,e)
                value = None
            columns_lists[i].append(value)
    for i,column in enumerate(columns):
        df_dict[column] = columns_lists[i]
    df = pd.DataFrame(data=df_dict)
    return df



def read_wyckoffs(fplo_out):

    start = False
    n_found = 0
    wyckoffs = []

    for line in fplo_out:
        if 'Number of Wyckoff positions' in line:
            start = True
            n_wyckoffs = int(line.split(':')[1])
            continue
        if start:
            if 'No.   Element ' in line:
                continue
            lines = line.split()
            n = int(lines[0])
            Element = lines[1]
            pos = np.array([float(Fraction(x)) for x in lines[2:]])
            wyckoffs.append([n,Element,pos])
            n_found += 1
            if n_found == n_wyckoffs:
                break

    if n_found < n_wyckoffs:
        raise Exception('Found {} wyckoffs, but expecting {}.'.format(n_found,n_wyckoffs))

    start = False
    n_found = 0
    sites_wps = []
    for line in fplo_out:
        if 'Atom sites' in line:
            start = True
            continue
        if start:
            if 'Number of sites' in line:
                n_sites = int(line.split(':')[1])
                continue
            if 'Number of nonempty real sites' in line:
                continue
            if 'No.  Element WPS CPA-Block' in line:
                continue
            if len(line.split()) < 7:
                continue
            lines = line.split()
            sites_wps.append(int(lines[2])-1)
            n_found += 1
            if n_found == n_sites:
                break

    if n_found < n_sites:
        raise Exception('Found {} sites, but expecting {}.'.format(n_found,n_sites))

    return wyckoffs,sites_wps

def assign_wyckoffs(struct,wyckoffs_fplo):

    print(wyckoffs_fplo)
    sym = SpacegroupAnalyzer(struct)
    sym_data = sym.get_symmetry_dataset()
    wyckoffs = sym_data['wyckoffs']
    print(wyckoffs)

    wyckoffs_fplo2 = []
    for w in wyckoffs_fplo:
        wyckoffs_fplo2.append(PeriodicSite(w[1],w[2],struct.lattice,to_unit_cell=True))

    wyckoffs_map = {}
    for i,site in enumerate(wyckoffs_fplo2):
        for j,site2 in enumerate(struct.sites):
            dist = pbc_diff(site.frac_coords,site2.frac_coords)
            if norm(dist) < 1e-4 and site.specie == site2.specie.element:
                wyckoffs_map[wyckoffs[j]] = i
    print(wyckoffs_map)

    if set(wyckoffs_map) != set(wyckoffs):
        raise Exception('Not all wyckoffs identified, something is wrong')
    
    site_map = []
    for i in range(len(struct.sites)):
        site_map.append(wyckoffs_map[wyckoffs[i]])

    return site_map

def assign_moments(node_fplo):

    moments = node_fplo.outputs.properties.get_dict()['magnetic_moments']
    with node_fplo.outputs.result.open() as f:                                      
        fplo_out = f.readlines()
    
    wyckoffs,sites_wps = read_wyckoffs(fplo_out)
    wps_moments = {}
    for i,wps in enumerate(sites_wps):
        if not wps in wps_moments:
            wps_moments[wps] = moments[i]
        else:
            if wps_moments[wps] != moments[i]:
                raise Exception('Sites with same wps have different moments {} {}'.format(wps_moments[wps],moments[i]))

    struct_info = node_fplo.outputs.struct_info.get_dict()
    struct = Structure.from_dict(struct_info['struct'])

    site_map = assign_wyckoffs(struct,wyckoffs)

    magmom = []
    for i in range(len(struct.sites)):
        magmom.append([0,0,wps_moments[site_map[i]]])

    struct.remove_site_property('magmom')
    struct.add_site_property('magmom',magmom)

    return struct

def assign_sites(struct,sites):
    sites2 = []
    for s in sites:
        sites2.append(PeriodicSite(s[0],s[1],struct.lattice,to_unit_cell=True))

    sites_map = {}
    for i,site in enumerate(sites2):
        for j,site2 in enumerate(struct.sites):
            dist = pbc_diff(site.frac_coords,site2.frac_coords)
            if norm(dist) < 1e-4 and site.specie == site2.specie.element:
                sites_map[j] = i
    print(sites_map)
    return sites_map

def get_fplo_primitive_structure(node_fplo,assign_moments=True,direct_fplo_output=False):

    if not direct_fplo_output:
        with node_fplo.outputs.result.open() as f:                                      
            fplo_out = f.readlines()
    else:
        fplo_out = node_fplo

    start = False
    n_found = 0
    species = []
    coords = []
    for i,line in enumerate(fplo_out):
        if 'Atom sites' in line:
            start = True
            continue
        if line.startswith('lattice vectors'):
            A = np.zeros((3,3))
            for j in range(3):
                vec = fplo_out[i+j+1].split()[2:5]
                vec = [float(Fraction(v))* 0.529177210903 for v in vec]
                A[j,:] = vec 
        if start:
            if 'Number of sites' in line:
                n_sites = int(line.split(':')[1])
                continue
            if 'Number of nonempty real sites' in line:
                continue
            if 'No.  Element WPS CPA-Block' in line:
                continue
            if len(line.split()) < 7:
                continue
            lines = line.split()
            species.append(lines[1])
            pos = lines[4:]
            pos = [float(x)* 0.529177210903 for x in pos]
            coords.append(pos)
            n_found += 1
            if n_found == n_sites:
                break

    struct = Structure(A,species,coords,coords_are_cartesian=True)

    if assign_moments:
        parsed_output = parse_fplo_output(fplo_out)
        moments = parsed_output[2]['magnetic_moments']
        magmom = []
        for i in range(len(moments)):
            magmom.append([0,0,moments[i]])
        struct.add_site_property('magmom',magmom)
        struct.add_site_property('magmom_basis',['cart']*len(moments))
    return struct

def get_fplo_conventional_structure(node_fplo,direct_fplo_output=False):
    struct = get_fplo_primitive_structure(node_fplo,direct_fplo_output=direct_fplo_output)

    if not direct_fplo_output:
        with node_fplo.outputs.result.open() as f:                                      
            fplo_out = f.readlines()
    else:
        fplo_out = node_fplo

    for i,line in enumerate(fplo_out):
        if 'primitive to bravais transformation' in line:
            P = np.zeros((3,3))
            for j in range(3):
                vec = fplo_out[i+j+1].split()[2:5]
                vec = [float(Fraction(v)) for v in vec]
                P[j,:] = vec

    struct.make_supercell(np.linalg.inv(P))

    return struct

def assign_moments2(node_fplo):
    moments = node_fplo.outputs.properties.get_dict()['magnetic_moments']
    with node_fplo.outputs.result.open() as f:                                      
        fplo_out = f.readlines()
    
    struct_info = node_fplo.outputs.struct_info.get_dict()
    struct = Structure.from_dict(struct_info['struct'])
    print(struct)

    struct_FPLO = get_fplo_structure(node_fplo)
    print(struct_FPLO)

    sym = SpacegroupAnalyzer(struct)
    sym_data = sym.get_symmetry_dataset()
    eq_atoms = sym_data['equivalent_atoms']
    print(eq_atoms) 
    site_mappings = {}
    for i,site in enumerate(struct.sites):
        for j,site2 in enumerate(struct_FPLO.sites):
            if site.is_periodic_image(site2,tolerance=1e-3):
                site_mappings[i] = j
    print(site_mappings)
    
def get_calc_symmetry(n,precision=0.01,get_group=False):
    node = load_node(n)
    node_fplo = node.called[1]
    struct = get_fplo_primitive_structure(node_fplo)
    change_magmom_basis(struct,'crystal_scaled')
    if not get_group:
        X = get_symmetry_tensor(struct,'/jakzel/Temp/symmetr_input','j',precision=precision)
        return X
    else:
        sg = find_symmetry(struct,'/jakzel/Temp/symmetr_input',precision=precision)
        return sg

def get_calc_result(n):
    node = load_node(n)
    X = read_new(node.outputs.result.get_content().splitlines())
    return X

def get_fplo_spacegroup(num):
    n = load_node(num).called[1]
    fplo_out = n.outputs.input.get_content().replace('\n','')
    find = re.findall(r'spacegroup +=\{\"([0-9]+)\"',fplo_out)
    sg = int(find[0])
    return sg

def get_linres_convergence(n=None,k_conv_tres=0.01,g_conv_tres=0.01):

    linres_opt = get_linres_opt(125)
    linres_calcs_100 = get_linres_calculations_fast(project='mp-ahe',fplo_nk=20,linres_opt=linres_opt,finished_ok_only=True) 
    linres_opt = get_linres_opt(250)
    linres_calcs_200 = get_linres_calculations_fast(project='mp-ahe',fplo_nk=20,linres_opt=linres_opt,finished_ok_only=True) 
    if n is not None:
        linres_calcs_100 = linres_calcs_100[0:n]
        linres_calcs_200 = linres_calcs_200[0:n]

    mp_ids = list(set(linres_calcs_100.id).union(set(linres_calcs_200.id)))

    X_100 = [None,]*len(mp_ids)
    X_200 = [None,]*len(mp_ids)
    for _,calc in linres_calcs_100.iterrows():
        i = mp_ids.index(calc.id)
        node = load_node(calc.pk)
        try:
            X_100[i] = read_new(node.outputs.result.get_content().splitlines())
        except:
            X_100[i] = None

    for _,calc in linres_calcs_200.iterrows():
        i = mp_ids.index(calc.id)
        node = load_node(calc.pk)
        try:
            X_200[i] = read_new(node.outputs.result.get_content().splitlines())
        except:
            X_200[i] = None

    linres_calcs_merged = pd.DataFrame({'id':mp_ids,"X_100":X_100,"X_200":X_200})
     
    g_diff_100_s = []
    g_diff_200_s = []
    for _,calc in linres_calcs_merged.iterrows():
        if calc.X_100 is not None:
            X_100_g = calc.X_100[1,:,0,0,1].data
            g_diff_100 = np.zeros(4)
            for j in range(4):
                g_diff_100[j] = (X_100_g[j]-X_100_g[j+1])/X_100_g[j]
            g_diff_100_s.append(g_diff_100)
        else:
            g_diff_100_s.append(None)

        if calc.X_200 is not None:
            X_200_g = calc.X_200[1,:,0,0,1].data
            g_diff_200 = np.zeros(4)
            for j in range(4):
                g_diff_200[j] = (X_200_g[j]-X_200_g[j+1])/X_200_g[j]
            g_diff_200_s.append(g_diff_200)
        else:
            g_diff_200_s.append(None)

    linres_calcs_merged['g_diff_100'] = g_diff_100_s
    linres_calcs_merged['g_diff_200'] = g_diff_200_s
    
    nk_conv_s = []
    for _,calc in linres_calcs_merged.iterrows():
        if calc.X_100 is not None and calc.X_200 is not None:
            X_100_g = calc.X_100[1,:,0,0,1].data
            X_200_g = calc.X_200[1,:,0,0,1].data
            nk_conv = np.zeros(5)
            for g in range(5):
                nk_conv[g] = (X_200_g[g]-X_100_g[g])/X_200_g[g]
            nk_conv_s.append(nk_conv)
        else:
            nk_conv_s.append(None)

    linres_calcs_merged['nk_conv'] = nk_conv_s
    linres_calcs_merged['converged'] = [is_converged(linres_calcs_merged.X_100[i],linres_calcs_merged.X_200[i],k_conv_tres,g_conv_tres) for i in
            range(len(linres_calcs_merged))]

    return linres_calcs_merged

def is_converged(X_100,X_200,k_conv_tres=0.01,g_conv_tres=0.01):
    if X_100 is not None and X_200 is not None:
        X_100_g = X_100[1,:,0,0,1].data
        X_200_g = X_200[1,:,0,0,1].data
        k_conv = []
        for g in range(5):
            if abs((X_200_g[g]-X_100_g[g])/X_200_g[g]) < k_conv_tres:
                k_conv.append(True)
            else:
                k_conv.append(False)

        g_conv = []
        for j in range(4):
            g_conv.append(abs((X_200_g[j]-X_200_g[j+1])/X_200_g[j]) < g_conv_tres)

        
        conv = []
        for j in range(4):
            if k_conv[j] and k_conv[j+1]:
                if g_conv[j]:
                    conv.append(True)
                else:
                    conv.append(False)
            else:
                conv.append(False)

        return conv
    else:
        return None

def get_calc_convergence(X_1,X_2,compx=0,compy=1):

    if X_1 is not None and X_2 is not None:
        try:
            X_1_g = X_1[1,:,0,compx,compy].data
            X_2_g = X_2[1,:,0,compx,compy].data
            k_conv = []
            for g in range(5):
                k_conv.append(abs((X_2_g[g]-X_1_g[g])/X_2_g[g])*100)

            g_conv = []
            for j in range(4):
                g_conv.append(abs((X_2_g[j]-X_2_g[j+1])/X_2_g[j])*100)

            return k_conv,g_conv
        except Exception as e:
            print(e)
            return None
    else:
        return None



def get_all_results(n=None):

    linres_opt = get_linres_opt(250)
    linres_calcs = get_linres_calculations_fast(project='mp-ahe',fplo_nk=20,linres_opt=linres_opt,finished_ok_only=True)

    ids = []
    fplo_pks = []
    pks = []
    materials = []
    space_groups = []
    ahes = []
    cond_xs = []
    cond_zs = []

    if n is not None:
        linres_calcs = linres_calcs[0:n]

    for i,calc in linres_calcs.iterrows():
        node = load_node(calc.id)
        try:
            Xcalc = get_calc_result(calc.pk)
        except:
            Xcalc = None
        if Xcalc is not None:
            ids.append(node.get_extra('id'))
            fplo_pks.append(calc.id)
            pks.append(calc.pk)
            materials.append(node.get_extra('material'))
            space_groups.append(node.get_extra('nonmag_space_group_number'))
            ahes.append(Xcalc[1,0,0,0,1].data)
            cond_xs.append(Xcalc[0,0,0,0,0].data)
            cond_zs.append(Xcalc[0,0,0,2,2].data)

    df_dict = OrderedDict([
               ('id', ids),
               ('fplo_pk',fplo_pks),
               ('pk',pks),
               ('material', materials),
               ('space_group', space_groups),
               ('ahe', ahes),
               ('cond_xx', cond_xs),
               ('cond_zz', cond_zs)])

    df = pd.DataFrame(data=df_dict)
    return df

def get_gap(Xb):
    shape = Xb.shape
    gaps = np.zeros((shape[0],shape[1],shape[2]))
    for i in range(shape[0]):
        for j in range(shape[1]):
            for l in range(shape[2]):
                for m,E in enumerate(Xb[i,j,l,:]):
                    E1 = Xb[i,j,l,m+1]
                    if E <0 and  E1 > 0:
                        gaps[i,j,l] = E1 - E
                        #print(m,E,E1)
                        break
    return gaps
