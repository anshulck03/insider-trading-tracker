# Insider Trading Tracker

import requests
from bs4 import BeautifulSoup
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Function to scrape insider trading data
def scrape_insider_trading():
    url = "https://www.sec.gov/cgi-bin/own-disp?action=getall"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Example: Parse table data
    rows = soup.find_all("tr")
    data = []

    for row in rows[1:]:  # Skip header row
        cols = row.find_all("td")
        if len(cols) > 0:
            data.append([col.text.strip() for col in cols])

    columns = [col.text.strip() for col in rows[0].find_all("th")]
    return pd.DataFrame(data, columns=columns)

# Scrape data
data = scrape_insider_trading()

# Initialize Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Insider Trading Tracker"),
    dcc.Graph(id="insider-chart"),
    dcc.Dropdown(
        id="company-filter",
        options=[{"label": company, "value": company} for company in data['Company'].unique()],
        placeholder="Filter by company",
        multi=True
    ),
    dcc.Interval(id="interval", interval=60*1000, n_intervals=0)  # Update data every minute
])

# Callback to update chart
@app.callback(
    Output("insider-chart", "figure"),
    [Input("company-filter", "value")]
)
def update_chart(selected_companies):
    filtered_data = data
    if selected_companies:
        filtered_data = data[data['Company'].isin(selected_companies)]

    figure = {
        "data": [
            {
                "x": filtered_data['Date'],
                "y": filtered_data['Shares Traded'],
                "type": "bar",
                "name": company
            } for company in filtered_data['Company'].unique()
        ],
        "layout": {
            "title": "Insider Trading Activity",
            "xaxis": {"title": "Date"},
            "yaxis": {"title": "Shares Traded"}
        }
    }
    return figure

# Run app
if __name__ == "__main__":
    app.run_server(debug=True)
