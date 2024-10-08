import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

## Download data
url_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
url_recovered = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

confirmed = pd.read_csv(url_confirmed)
deaths = pd.read_csv(url_deaths)
recovered = pd.read_csv(url_recovered)

## Preprocessing Data
### Melting Data
confirmed_date = confirmed.columns[4:] 
confirmed_geo = confirmed.columns[:4]
total_confirmed = confirmed.melt(id_vars=confirmed_geo, value_vars= confirmed_date,value_name='Confirmed',var_name='Date')

deaths_date = deaths.columns[4:]
deaths_geo = deaths.columns[:4]
total_deaths = deaths.melt(id_vars=confirmed_geo, value_vars=deaths_date, value_name='Deaths',var_name='Date')

recovered_date = recovered.columns[4:]
recovered_geo = recovered.columns[:4]
total_recovered= recovered.melt(id_vars=recovered_geo, value_vars=recovered_date, value_name='Recovered',var_name='Date')

### Merging data
covid_data = total_confirmed.merge(total_deaths, on=confirmed_geo.to_list() + ['Date'], how='left')
covid_data = covid_data.merge(total_recovered, on = recovered_geo.to_list() + ['Date'], how='left')

### Correct Data type 'Date'
covid_data['Date'] = pd.to_datetime(covid_data['Date'])

### Fill Nan Value to 0 at 'Recovered'
covid_data['Recovered'] = covid_data['Recovered'].fillna(0)

### Get attribute 'Active' by below formula
covid_data['Active'] = covid_data['Confirmed'] - covid_data['Deaths'] - covid_data['Recovered']

### Get extra covid_data
covid_data_1 = covid_data.groupby(['Date'])[['Confirmed', 'Deaths', 'Recovered', 'Active']].sum().reset_index()
covid_data_2 = covid_data.groupby(['Date', 'Country/Region'])[['Confirmed', 'Deaths', 'Recovered', 'Active']].sum().reset_index()

### Get list of country with latitude and longitude
covid_data_dict = covid_data[['Country/Region', 'Lat', 'Long']]
list_locations = covid_data_dict.set_index('Country/Region')[['Lat', 'Long']].T.to_dict()

#Creating dashboard
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
app.layout = html.Div([

    #####HEADER OF PAGE######
    html.Div([
        html.Div([
            html.Div([
                html.H3("Covid - 19", style={"margin-bottom": "0px", 'color': 'white'}),
                html.H5("Track Covid - 19 Cases", style={"margin-top": "0px", 'color': 'white'}),
            ])
        ], className="one-half column", id="title"),

        html.Div([
            html.H6('Last Updated: ' + str(covid_data_1['Date'].iloc[-1].strftime("%B %d, %Y")) + '  00:01 (UTC)',
                    style={'color': 'orange'}),

        ], className="one-third column", id='title1'),

    ], id="header", className="row flex-display", style={"margin-bottom": "25px"}),

    #####ROW INFORMATION 1#####
    html.Div([

        ###global cases card###
        html.Div([
            html.H6(
                children='Global cases',
                style = {'textAlign':'center',
                         'color': 'white'}
                    ),
            html.P(f"{covid_data_1.iloc[-1]['Confirmed']}",
                    style = {'textAlign':'center',
                            'color':'orange',
                            'fontSize':40}
                    ),
            html.P(
                'New: ' + f"{covid_data_1.iloc[-1]['Confirmed'] - covid_data_1.iloc[-2]['Confirmed']}"\
                      + ' (' + str(round(((covid_data_1['Confirmed'].iloc[-1] - covid_data_1['Confirmed'].iloc[-2])\
                                           / covid_data_1['Confirmed'].iloc[-1]) * 100, 2)) + '%)',
                style={
                       'textAlign': 'center',
                       'color': 'orange',
                       'fontSize': 15,
                       'margin-top': '-18px'}
                    )
            ], className = 'card_container three columns',),

        ###Global deaths###
        html.Div([
            html.H6(children='Global Deaths',
                    style={
                        'textAlign':'center',
                        'color':'white'}),
            html.P(f"{covid_data_1['Deaths'].iloc[-1]}",
                   style={'textAlign': 'center',
                        'color': '#dd1e35',
                        'fontSize': 40}),
            html.P('new:  ' + f"{covid_data_1['Deaths'].iloc[-1] - covid_data_1['Deaths'].iloc[-2]} "\
                   + ' (' + str(round(((covid_data_1['Deaths'].iloc[-1] - covid_data_1['Deaths'].iloc[-2]) / \
                                       covid_data_1['Deaths'].iloc[-1]) * 100, 2)) + '%)',
                   style={
                       'textAlign': 'center',
                       'color': '#dd1e35',
                       'fontSize': 15,
                       'margin-top': '-18px'}
                   )], className="card_container three columns",),

        ###Global Recovered###
        html.Div([
            html.H6(children='Global Recovered',
                    style={'textAlign':'center',
                           'color':'white'}),
            html.P(f"{covid_data_1['Recovered'].iloc[-1]:,.0f}",
                   style={
                       'textAlign': 'center',
                       'color': 'green',
                       'fontSize': 40}
                   ),
            html.P('new:  ' + f"{covid_data_1['Recovered'].iloc[-1] - covid_data_1['Recovered'].iloc[-2]:,.0f} "
                   + ' (' + str(round(((covid_data_1['Recovered'].iloc[-1] - covid_data_1['Recovered'].iloc[-2]) /
                                       covid_data_1['Recovered'].iloc[-1]) * 100, 2)) + '%)',
                   style={
                       'textAlign': 'center',
                       'color': 'green',
                       'fontSize': 15,
                       'margin-top': '-18px'}
                   )], className="card_container three columns"),

        ###Global Active###
        html.Div([
            html.H6(children='Global Active',
                    style={
                        'textAlign': 'center',
                        'color': 'white'}
                    ),

            html.P(f"{covid_data_1['Active'].iloc[-1]:,.0f}",
                   style={
                       'textAlign': 'center',
                       'color': '#e55467',
                       'fontSize': 40}
                   ),

            html.P('new:  ' + f"{covid_data_1['Active'].iloc[-1] - covid_data_1['Active'].iloc[-2]:,.0f} "
                   + ' (' + str(round(((covid_data_1['Active'].iloc[-1] - covid_data_1['Active'].iloc[-2]) /
                                       covid_data_1['Active'].iloc[-1]) * 100, 2)) + '%)',
                   style={
                       'textAlign': 'center',
                       'color': '#e55467',
                       'fontSize': 15,
                       'margin-top': '-18px'}
                   )], className="card_container three columns"),
    ], className="row flex-display"),

    #####ROW INFORMATION 2#####
    html.Div([
        #### Dropdown to choose 1 country####
        html.Div([
            html.P('Select country: ', className='fix_label', style={'color':'white'}),

            dcc.Dropdown(id='w_countries', 
                multi=False, #only one country can be chosen per time
                clearable=False,# allow us clear previous work
                value='Vietnam', #default value
                placeholder='Select Countries',
                options = [{'label': c, 'value': c} for c in (covid_data['Country/Region'].unique())],
                className= 'dcc_compon'),

            html.P('New Cases of ' + '  ' + ' ' + str(covid_data_2['Date'].iloc[-1].strftime("%B %d, %Y")) + '  ', 
                className='fix_label',  
                style={'color': 'white', 'text-align': 'center'}),
            
            dcc.Graph(id='confirmed', 
                    config={'displayModeBar': False},
                    className = 'dcc_compon',
                    style={'margin-top':'20px'}),
            

            dcc.Graph(id='deaths',
                    config={'displayModeBar':False},
                    className='dcc_compon',
                    style={'margin-top':'20px'}),

            dcc.Graph(id='recovered',
                    config={'displayModeBar':False},
                    className='dcc_compon',
                    style={'margin-top':'20px'}),

            dcc.Graph(id='active',
                    config={'displayModeBar':False},
                    className='dcc_compon',
                    style={'margin-top':'20px'})
        ], className="create_container three columns", id="cross-filter-options"),

        ###Pie chart###
        html.Div([
            dcc.Graph(id='pie_chart',
                    config={'displayModeBar': 'hover',}),
        ], className="create_container four columns"),

        ###Line charts###
        html.Div([
            dcc.Graph(id='line_chart')
        ], className='create_container five columns')
    ], className='row flex-display'),

    ###ROW INFORMATION 3###
    html.Div([
        html.Div([
            dcc.Graph(id='map')
        ], className='create_container1 twelve columns')
    ], className="row flex-display")

], id='mainContainer', style={"display": "flex", "flex-direction": "column"})


#confirmed
@app.callback(
    Output('confirmed', 'figure'),
    Input('w_countries','value')
)  
def update_country(w_countries):

    #Fomular: total recent confirms - total previous confirms
    value_confirmed = covid_data_2[covid_data_2['Country/Region'] == w_countries]['Confirmed'].iloc[-1]\
         - covid_data_2[covid_data_2['Country/Region'] == w_countries]['Confirmed'].iloc[-2]
    #Fomular: total previous confirms - total 2 last days confirms
    delta_confirmed = covid_data_2[covid_data_2['Country/Region'] == w_countries]['Confirmed'].iloc[-2]\
         - covid_data_2[covid_data_2['Country/Region'] == w_countries]['Confirmed'].iloc[-3]
    return {
            'data': [go.Indicator(
                    mode='number+delta',
                    value=value_confirmed,
                    delta={'reference': delta_confirmed,
                              'position': 'right',
                              'valueformat': ',g',
                              'relative': False,

                              'font': {'size': 15}},
                    number={'valueformat': ',',
                            'font': {'size': 20},

                               },
                    domain={'y': [0, 1], 'x': [0, 1]})],
            'layout': go.Layout(
                title={'text': 'New Confirmed',
                       'y': 1,
                       'x': 0.5,
                       'xanchor': 'center',
                       'yanchor': 'top'},
                font=dict(color='orange'),
                paper_bgcolor='#1f2c56',
                plot_bgcolor='#1f2c56',
                height=50
                ),

            }
# Deploy web
if __name__ == '__main__':
    app.run_server()