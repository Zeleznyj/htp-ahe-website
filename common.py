import dash_bootstrap_components as dbc

column_names = {
    'Total Magnetization' : 'total_magnetization',
    'Average Magnetization' : 'average_magnetization',
    'Maximum Z' : 'maxZ',
    'Number of mirrors': 'n_ms',
    'Number of symmetries' : 'n_syms',
    'AHE magnitude' : 'norm_g',
    'Conductivity xx' : 'cond_xx',
    'Formula' : 'formula',
    'MP id' : 'id',
    'Non-mag spacegroup': 'spacegroup',
    'Mag spacegroup' : 'magnetic_symmetry',
    'Gamma conv': 'gamma_convergence',
    'k conv' : 'k_convergence',
    'AHE angle' : 'Hall_angle',
    'Magnetization' : 'total_magnetization',
}
inv_column_names = {v: k for k, v in column_names.items()}

def Navbar():

    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Material Explorer", href="material_explorer")),
            dbc.NavItem(dbc.NavLink("Statistics", href="statistics")),
            dbc.NavItem(dbc.NavLink("Nodal line analysis", href="nodal_lines")),
        ],
        brand="AHE HTP",
        brand_href="home",
        color="primary",
        dark=True,
    )

    return navbar
