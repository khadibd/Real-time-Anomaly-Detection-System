import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from collections import deque
from datetime import datetime, timedelta
import random
import time

# Initialize Dash app
app = dash.Dash(__name__)

# Store recent data
MAX_DATA_POINTS = 100
sensor_data = {
    'temperature': deque(maxlen=MAX_DATA_POINTS),
    'pressure': deque(maxlen=MAX_DATA_POINTS),
    'humidity': deque(maxlen=MAX_DATA_POINTS),
    'vibration': deque(maxlen=MAX_DATA_POINTS),
    'timestamps': deque(maxlen=MAX_DATA_POINTS),
    'anomalies': deque(maxlen=MAX_DATA_POINTS),
    'sensor_id': deque(maxlen=MAX_DATA_POINTS)
}

# Initialize with some data
for i in range(50):
    sensor_data['timestamps'].append(datetime.now() - timedelta(seconds=i*2))
    sensor_data['temperature'].append(20 + random.uniform(-2, 2))
    sensor_data['pressure'].append(1013 + random.uniform(-10, 10))
    sensor_data['humidity'].append(50 + random.uniform(-5, 5))
    sensor_data['vibration'].append(random.uniform(0, 0.5))
    sensor_data['anomalies'].append(random.random() > 0.9)  # 10% anomalies
    sensor_data['sensor_id'].append(f"sensor_{random.randint(1, 10)}")

app.layout = html.Div([
    html.Div([
        html.H1("AnomaLens - Real-time Anomaly Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.P("Live monitoring of IoT sensor data with anomaly detection",
               style={'textAlign': 'center', 'color': '#7f8c8d'})
    ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'marginBottom': '20px'}),
    
    html.Div([
        html.Div([
            dcc.Graph(id='live-temperature', style={'height': '400px'}),
            dcc.Graph(id='live-pressure', style={'height': '400px'})
        ], className='row'),
        
        html.Div([
            dcc.Graph(id='live-humidity', style={'height': '400px'}),
            dcc.Graph(id='live-vibration', style={'height': '400px'})
        ], className='row'),
        
        html.Div([
            dcc.Graph(id='anomaly-distribution', style={'height': '400px'}),
            dcc.Graph(id='sensor-status', style={'height': '400px'})
        ], className='row')
    ], style={'padding': '10px'}),
    
    html.Div([
        html.H3("📊 Statistics", style={'marginTop': '30px'}),
        html.Div(id='stats-container', className='row')
    ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'marginTop': '20px'}),
    
    html.Div([
        html.H3("🚨 Recent Alerts", style={'marginTop': '20px'}),
        html.Div(id='alerts-container', style={
            'maxHeight': '200px',
            'overflowY': 'scroll',
            'border': '1px solid #ddd',
            'padding': '10px',
            'backgroundColor': '#fff'
        })
    ], style={'padding': '20px'}),
    
    dcc.Interval(
        id='interval-component',
        interval=2000,  # Update every 2 seconds
        n_intervals=0
    ),
    
    dcc.Store(id='data-store')
], style={'fontFamily': 'Arial, sans-serif'})

# CSS for responsive design
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>AnomaLens Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            .row {
                display: flex;
                flex-wrap: wrap;
                margin: 0 -10px;
            }
            .row > div {
                flex: 1;
                min-width: 400px;
                padding: 10px;
            }
            .stat-card {
                background: white;
                padding: 15px;
                margin: 10px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }
            .alert-item {
                padding: 10px;
                margin: 5px 0;
                background: #ffeaa7;
                border-left: 4px solid #e74c3c;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

def generate_new_data_point():
    """Generate new simulated data point"""
    timestamp = datetime.now()
    temperature = 20 + random.uniform(-2, 2)
    pressure = 1013 + random.uniform(-10, 10)
    humidity = 50 + random.uniform(-5, 5)
    vibration = random.uniform(0, 0.5)
    
    # Randomly introduce anomalies (5% chance)
    is_anomaly = random.random() > 0.95
    
    if is_anomaly:
        # Make data point anomalous
        temperature += random.choice([-10, 15])
        pressure += random.choice([-50, 80])
        anomaly_type = random.choice(['temperature_spike', 'pressure_drop', 'vibration_high'])
    else:
        anomaly_type = 'normal'
    
    return {
        'timestamp': timestamp,
        'temperature': temperature,
        'pressure': pressure,
        'humidity': humidity,
        'vibration': vibration,
        'anomaly': is_anomaly,
        'anomaly_type': anomaly_type,
        'sensor_id': f"sensor_{random.randint(1, 10)}"
    }

@app.callback(
    [Output('live-temperature', 'figure'),
     Output('live-pressure', 'figure'),
     Output('live-humidity', 'figure'),
     Output('live-vibration', 'figure'),
     Output('anomaly-distribution', 'figure'),
     Output('sensor-status', 'figure'),
     Output('stats-container', 'children'),
     Output('alerts-container', 'children'),
     Output('data-store', 'data')],
    Input('interval-component', 'n_intervals'),
    State('data-store', 'data')
)
def update_all_graphs(n, stored_data):
    # Generate new data point
    new_data = generate_new_data_point()
    
    # Update sensor data
    sensor_data['timestamps'].append(new_data['timestamp'])
    sensor_data['temperature'].append(new_data['temperature'])
    sensor_data['pressure'].append(new_data['pressure'])
    sensor_data['humidity'].append(new_data['humidity'])
    sensor_data['vibration'].append(new_data['vibration'])
    sensor_data['anomalies'].append(new_data['anomaly'])
    sensor_data['sensor_id'].append(new_data['sensor_id'])
    
    # Create temperature plot
    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(
        x=list(sensor_data['timestamps']),
        y=list(sensor_data['temperature']),
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#3498db', width=2),
        marker=dict(size=6)
    ))
    
    # Highlight anomalies
    anomaly_indices = [i for i, anomaly in enumerate(sensor_data['anomalies']) if anomaly]
    if anomaly_indices:
        temp_fig.add_trace(go.Scatter(
            x=[sensor_data['timestamps'][i] for i in anomaly_indices],
            y=[sensor_data['temperature'][i] for i in anomaly_indices],
            mode='markers',
            name='Anomalies',
            marker=dict(color='red', size=12, symbol='x')
        ))
    
    temp_fig.update_layout(
        title='🌡️ Temperature Over Time',
        xaxis_title='Time',
        yaxis_title='Temperature (°C)',
        template='plotly_white',
        height=350
    )
    
    # Create pressure plot
    pressure_fig = go.Figure()
    pressure_fig.add_trace(go.Scatter(
        x=list(sensor_data['timestamps']),
        y=list(sensor_data['pressure']),
        mode='lines',
        name='Pressure',
        line=dict(color='#2ecc71', width=2)
    ))
    pressure_fig.update_layout(
        title='📊 Pressure Over Time',
        xaxis_title='Time',
        yaxis_title='Pressure (hPa)',
        template='plotly_white',
        height=350
    )
    
    # Create humidity plot
    humidity_fig = go.Figure()
    humidity_fig.add_trace(go.Scatter(
        x=list(sensor_data['timestamps']),
        y=list(sensor_data['humidity']),
        mode='lines',
        name='Humidity',
        line=dict(color='#9b59b6', width=2)
    ))
    humidity_fig.update_layout(
        title='💧 Humidity Over Time',
        xaxis_title='Time',
        yaxis_title='Humidity (%)',
        template='plotly_white',
        height=350
    )
    
    # Create vibration plot
    vibration_fig = go.Figure()
    vibration_fig.add_trace(go.Scatter(
        x=list(sensor_data['timestamps']),
        y=list(sensor_data['vibration']),
        mode='lines',
        name='Vibration',
        line=dict(color='#e74c3c', width=2)
    ))
    vibration_fig.update_layout(
        title='📳 Vibration Over Time',
        xaxis_title='Time',
        yaxis_title='Vibration Level',
        template='plotly_white',
        height=350
    )
    
    # Anomaly distribution pie chart
    anomaly_count = sum(sensor_data['anomalies'])
    normal_count = len(sensor_data['anomalies']) - anomaly_count
    anomaly_dist_fig = go.Figure(data=[go.Pie(
        labels=['Normal', 'Anomalies'],
        values=[normal_count, anomaly_count],
        marker_colors=['#2ecc71', '#e74c3c']
    )])
    anomaly_dist_fig.update_layout(
        title='📈 Anomaly Distribution',
        template='plotly_white',
        height=350
    )
    
    # Sensor status heatmap
    sensor_ids = list(set(sensor_data['sensor_id']))
    status_data = []
    for sensor in sensor_ids:
        indices = [i for i, sid in enumerate(sensor_data['sensor_id']) if sid == sensor]
        if indices:
            latest_anomaly = any(sensor_data['anomalies'][i] for i in indices[-5:])
            status_data.append({
                'sensor': sensor,
                'status': '⚠️ Alert' if latest_anomaly else '✅ Normal',
                'value': 0 if latest_anomaly else 1
            })
    
    if status_data:
        df_status = pd.DataFrame(status_data)
        sensor_status_fig = px.bar(df_status, x='sensor', y='value', 
                                 color='status', title='📱 Sensor Status',
                                 color_discrete_map={'✅ Normal': '#2ecc71', '⚠️ Alert': '#e74c3c'})
    else:
        sensor_status_fig = go.Figure()
        sensor_status_fig.update_layout(title='📱 Sensor Status')
    sensor_status_fig.update_layout(template='plotly_white', height=350)
    
    # Statistics cards
    stats = html.Div([
        html.Div([
            html.H4(f"{len(sensor_data['timestamps'])}", style={'color': '#3498db'}),
            html.P("Total Data Points")
        ], className='stat-card'),
        html.Div([
            html.H4(f"{anomaly_count}", style={'color': '#e74c3c'}),
            html.P("Anomalies Detected")
        ], className='stat-card'),
        html.Div([
            html.H4(f"{len(set(sensor_data['sensor_id']))}", style={'color': '#2ecc71'}),
            html.P("Active Sensors")
        ], className='stat-card'),
        html.Div([
            html.H4(f"{sensor_data['temperature'][-1]:.1f}°C", style={'color': '#9b59b6'}),
            html.P("Current Temp")
        ], className='stat-card')
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'})
    
    # Recent alerts
    recent_alerts = []
    for i in range(min(10, len(sensor_data['timestamps']))):
        idx = -i-1
        if sensor_data['anomalies'][idx]:
            alert_time = sensor_data['timestamps'][idx].strftime('%H:%M:%S')
            alert_text = f"[{alert_time}] {sensor_data['sensor_id'][idx]} - Anomaly detected: Temp={sensor_data['temperature'][idx]:.1f}°C"
            recent_alerts.append(html.Div(alert_text, className='alert-item'))
    
    if not recent_alerts:
        recent_alerts = [html.Div("No recent alerts", style={'color': '#7f8c8d'})]
    
    # Store data for next callback
    stored_data = {
        'timestamps': list(sensor_data['timestamps']),
        'temperatures': list(sensor_data['temperature']),
        'anomalies': list(sensor_data['anomalies'])
    }
    
    return (temp_fig, pressure_fig, humidity_fig, vibration_fig, 
            anomaly_dist_fig, sensor_status_fig, stats, recent_alerts, stored_data)

# Add custom CSS
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    # Use app.run() instead of app.run_server()
    app.run(debug=True, port=8050)