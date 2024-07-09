from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from collections import defaultdict
import statistics

# Load and process data
freq_data = pd.read_csv('frequency_adc_data.csv')
freq_data['frequency'] = pd.to_numeric(freq_data['frequency'], errors='coerce')  # Ensure frequency is numeric
freq_data = freq_data.dropna(subset=['frequency'])
min_freq = min(freq_data["frequency"])
max_freq = max(freq_data["frequency"])
freq_values_sorted = sorted(list(freq_data["frequency"]))
dropdown_options = [{'label': val, 'value': val} for val in freq_values_sorted]

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define app layout
app.layout = html.Div(
    children=[
        html.H1("Frequency ADC Graph", style={'textAlign': 'center'}),
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id="min_dropdown",
                    value=min_freq,
                    options=dropdown_options,
                    placeholder="Select minimum limit",
                    multi=False,
                ),
                width={"size": 4, "offset": 1},
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="max_dropdown",
                    value=max_freq,
                    options=dropdown_options,
                    placeholder="Select maximum limit",
                    multi=False,
                ),
                width={"size": 4, "offset": 1}
            ),
        ]),
        dcc.Graph(id='complete_graph', figure={}),

        html.Br(),
        html.H2(
            "Single Frequency Data",
            style={'textAlign': 'center'}
        ),
        dbc.Col(
        dcc.Dropdown(
            id="indv_dropdown",
                    value=min_freq,
                    options=dropdown_options,
                    placeholder="Select a frequency",
                    multi=False,
               
        ),
        
        width={"size": 4, "offset": 1}
        ),

        dcc.Graph (id="indv_graph", figure={})

    ]
)

@app.callback(
    Output(component_id='complete_graph', component_property='figure'),
    [Input(component_id='min_dropdown', component_property='value'),
     Input(component_id='max_dropdown', component_property='value')]
)
def change_graph(min_freq, max_freq):
    new_df = freq_data[(freq_data['frequency'] >= min_freq) & (freq_data['frequency'] <= max_freq)]
    freq_adc = defaultdict(list)
    new_df = new_df.reset_index(drop=True)
    
    for i in range(len(new_df)):
        freq = new_df.loc[i, 'frequency']
        for column in new_df.columns:
            if column != 'frequency':
                value = pd.to_numeric(new_df.loc[i, column], errors='coerce')
                if not pd.isna(value):
                    freq_adc[freq].append(value)
                
    freq_adc_medians = {}
    for k, v in freq_adc.items():
        low = min(v)
        high = max(v)
        median = statistics.median(v)
        freq_adc_medians[k] = [low, median, high]
        
    data = defaultdict(list)
    for k, v in freq_adc_medians.items():
        data['frequency'].append(k)
        data['low'].append(v[0])
        data['median'].append(v[1])
        data['high'].append(v[2])
    
    df = pd.DataFrame(data)
    df_melted = df.melt(id_vars='frequency', var_name='Value', value_name='Data')

    fig = px.line(df_melted, x='frequency', y='Data', color='Value',
                  line_group='Value', labels={'frequency': 'Frequency', 'Data': 'Value'})

    # Update layout for better styling
    fig.update_layout(
        title='Frequency vs ADC Values',
        xaxis_title='Frequency (MHz)',
        yaxis_title='ADC Value',
        legend_title='Measurement',
        template='plotly_white',
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="black"
        ),
        title_font=dict(
            size=20,
            color='darkblue',
            family="Arial, sans-serif"
        ),
        legend=dict(
            title=dict(font=dict(size=14)),
            font=dict(size=12)
        ),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    # Add gridlines and enhance visuals
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

    return fig

@callback(
    Output(component_id="indv_graph",component_property='figure'),
    Input(component_id='indv_dropdown',component_property='value')
)
def change_single_frequency_graph(freq):
    new_df = freq_data[(freq_data['frequency']==freq)]
    new_df = new_df.reset_index(drop=True)
    freq = new_df.loc[0, 'frequency']
    i=1
    samplings=[]
    adc_vals=[]
    for column in new_df.columns:
        if column != 'frequency':
            samplings.append(i)
            adc_vals.append(new_df.loc[0, column])
            i+=1
    df = pd.DataFrame({'Sampling': samplings, 'ADC Value': adc_vals})
    fig = px.line(df, x='Sampling', y='ADC Value', title='ADC Values Over Sampling Points')
    
    fig.update_layout(
        title={'text': 'ADC Values Over Sampling Points', 'x': 0.5, 'xanchor': 'center'},
        xaxis_title='Sampling Points',
        yaxis_title='ADC Value',
        template='plotly_white',
        font=dict(family='Arial, sans-serif', size=14, color='black'),
        plot_bgcolor='white',
        paper_bgcolor='white'
        
    )

    fig.update_traces(
        line=dict(color='skyblue', width=2),
        marker=dict(size=4, color='lightcoral')
        )
    return fig

        

if __name__ == "__main__":
    app.run(debug=True)
