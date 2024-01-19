import pandas as pd 
import plotly.express as px

def biggest_assets(selected_countries):
    df = pd.read_csv("Global_500_2017_modified.csv")
    if len(selected_countries) > 0:
        df = df[df.Country.isin(selected_countries)]
    df = df.sort_values(by = "Assets($millions)", ascending = False)
    df = df.head(10)
    
    fig = px.bar(df, x = "Company Name", y = "Assets($millions)", title = "Top 10 Companies with the biggest Assets $MM", color_discrete_sequence=["green"])
    return fig


def rank_comparison():
    df = pd.read_csv("Global_500_2017_modified.csv")
    df = df[df['Rank'] <=10]
    
    # Create the horizontal bar graph using Plotly Express
    fig = px.bar(df, x=["Rank", "Previous Rank"], y="Company Name", orientation="h", barmode="group", title = "Current and Previous Rank for top companies")

    return fig

def rank_comparison():
    df = pd.read_csv("Global_500_2017_modified.csv")
    df = df[df['Rank'] <=10]
    
    # Create the horizontal bar graph using Plotly Express
    fig = px.bar(df, x=["Rank", "Previous Rank"], y="Company Name", orientation="h", barmode="group", title = "Current and Previous Rank for top companies")

    return fig

def plot_geo_locs(size_param):
    df = pd.read_csv("Global_500_2017_modified.csv")
    df = df[df['Rank'] <=10]
    fig = px.scatter_geo(df, lat="Latitude", lon="Longitude", color="Company Name", size=size_param,  hover_name="Company Name", projection="equirectangular")
    return fig
    