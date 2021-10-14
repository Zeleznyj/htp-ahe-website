from dash import html
from dash import dcc


def Header(app):
    return html.Div([get_header(app), html.Br([]), get_menu()])


def get_header(app):
    header = html.Div(
        [html.H1('HTP-AHE nodal line analysis for top materials')],
        className="row",
    )
    return header

def get_menu():

    menu = html.Div([
        dcc.Dropdown(
            id='materials-selection',
            options=[
                {'label':'Eu2SeO2','value': 'Eu2SeO2'},
                {'label':'GdTmRh2','value': 'GdTmRh2'},
                {'label':'U2PN2','value': 'U2PN2'},
                {'label':'Ni','value': 'Ni'},
                {'label':'MnCoPt2','value': 'MnCoPt2'},
                {'label':'CeTe2','value': 'CeTe2'},
                ],
            value='CeTe2'
        )
        ])

    return menu


def get_menu_old():
    menu = html.Div(
        [
            dcc.Link(
                "Overview",
                href="/dash-financial-report/overview",
                className="tab first",
            ),
            dcc.Link(
                "Price Performance",
                href="/dash-financial-report/price-performance",
                className="tab",
            ),
            dcc.Link(
                "Portfolio & Management",
                href="/dash-financial-report/portfolio-management",
                className="tab",
            ),
            dcc.Link(
                "Fees & Minimums", href="/dash-financial-report/fees", className="tab"
            ),
            dcc.Link(
                "Distributions",
                href="/dash-financial-report/distributions",
                className="tab",
            ),
            dcc.Link(
                "News & Reviews",
                href="/dash-financial-report/news-and-reviews",
                className="tab",
            ),
        ],
        className="row all-tabs",
    )
    return menu


def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table
