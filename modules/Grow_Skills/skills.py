import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load your data
df = pd.read_excel("LP Consolidated 2025-05-05.xlsx", sheet_name='Consolidated')
df = df.iloc[:, [1, 5, 6, 13, 14, 16,7]]
df.columns = ['OMP Drivers', 'Behaviours', 'Skills', 'Budget', 'Source', 'Owner','Skills Meta']

# Preprocess (create list columns, explode)
df['Behaviours_List'] = df['Behaviours'].dropna().astype(str).str.split(',')
df['Skills_List'] = df['Skills'].dropna().astype(str).str.split(',')

df_exploded = df.explode('Behaviours_List').explode('Skills_List')
df_exploded['Behaviours_List'] = df_exploded['Behaviours_List'].str.strip()
df_exploded['Skills_List'] = df_exploded['Skills_List'].str.strip()

# Create Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Learning Plan Dashboard"),

    html.Label("Select OMP Driver:"),
    dcc.Dropdown(
        id='omp-driver-dropdown',
        options=[{'label': driver, 'value': driver} for driver in df_exploded['OMP Drivers'].dropna().unique()],
        value=None,
        placeholder="Select an OMP Driver",
        multi=False
    ),

    dcc.Graph(id='skills-graph'),
    dcc.Graph(id='behaviours-graph')
])

@app.callback(
    [Output('skills-graph', 'figure'),
     Output('behaviours-graph', 'figure')],
    [Input('omp-driver-dropdown', 'value')]
)
def update_graphs(selected_driver):
    if selected_driver:
        filtered_df = df_exploded[df_exploded['OMP Drivers'] == selected_driver]
    else:
        filtered_df = df_exploded.copy()

    # Top skills
    skills_counts = filtered_df['Skills_List'].value_counts().reset_index()
    skills_counts.columns = ['Skill', 'Count']
    skills_fig = px.bar(skills_counts, x='Skill', y='Count', title='Top Skills')

    # Top behaviours
    behaviour_counts = filtered_df['Behaviours_List'].value_counts().reset_index()
    behaviour_counts.columns = ['Behaviour', 'Count']
    behaviour_fig = px.bar(behaviour_counts, x='Behaviour', y='Count', title='Top Behaviours')

    return skills_fig, behaviour_fig

if __name__ == '__main__':
    app.run(debug=True)
