"""Importing the required libraries"""

import bs4
import requests
import time
import random as ran
import sys
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from urllib.parse import quote


def scrape_mblock(movie_block):
    
    movieb_data ={}
  
    try:
        movieb_data['name'] = movie_block.find('a').get_text() # Name of the movie
    except:
        movieb_data['name'] = None

    try:    
        movieb_data['year'] = str(movie_block.find('span',{'class': 'lister-item-year'}).contents[0][1:-1]) # Release year
    except:
        movieb_data['year'] = None

    try:
        movieb_data['rating'] = float(movie_block.find('div',{'class':'inline-block ratings-imdb-rating'}).get('data-value')) #rating
    except:
        movieb_data['rating'] = None

    try:
        movieb_data['m_score'] = float(movie_block.find('span',{'class':'metascore favorable'}).contents[0].strip()) #meta score
    except:
        movieb_data['m_score'] = None

    try:
        movieb_data['votes'] = int(movie_block.find('span',{'name':'nv'}).get('data-value')) # votes
    except:
        movieb_data['votes'] = None

    return movieb_data
    

def scrape_m_page(movie_blocks):
    
    page_movie_data = []
    num_blocks = len(movie_blocks)
    
    for block in range(num_blocks):
        page_movie_data.append(scrape_mblock(movie_blocks[block]))
    
    return page_movie_data


def scrape_this(link,t_count):
    
    #from IPython.core.debugger import set_trace

    base_url = link
    target = t_count
    
    current_mcount_start = 0
    current_mcount_end = 0
    remaining_mcount = target - current_mcount_end 
    
    new_page_number = 1
    
    movie_data = []
    
    while remaining_mcount > 0:

        url = base_url + str(new_page_number)
        
        #set_trace()
        
        source = requests.get(url).text
        soup = bs4.BeautifulSoup(source,'html.parser')
        
        movie_blocks = soup.findAll('div',{'class':'lister-item-content'})
        
        movie_data.extend(scrape_m_page(movie_blocks))   
        
        current_mcount_start = int(soup.find("div", {"class":"nav"}).find("div", {"class": "desc"}).contents[1].get_text().split("-")[0])

        current_mcount_end = int(soup.find("div", {"class":"nav"}).find("div", {"class": "desc"}).contents[1].get_text().split("-")[1].split(" ")[0])

        remaining_mcount = target - current_mcount_end
        
        print('\r' + "currently scraping movies from: " + str(current_mcount_start) + " - "+str(current_mcount_end), "| remaining count: " + str(remaining_mcount), flush=True, end ="")
        
        new_page_number = current_mcount_end + 1
        
        time.sleep(ran.randint(0, 10))
    
    return movie_data


base_url = "https://www.imdb.com/search/title/?title_type=feature&num_votes=25000,&sort=user_rating,desc&start="
target_count = 100

movie_data = scrape_this(base_url, target_count)

df = pd.DataFrame(movie_data)

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1("Top Rated Movies Dashboard"),
        dcc.Graph(id="movie-rating-graph"),
    ]
)


@app.callback(
    dash.dependencies.Output("movie-rating-graph", "figure"),
    dash.dependencies.Input("movie-rating-graph", "id"),
)
def update_graph(selected_movie):
    figure = {
        "data": [
            {
                "x": df["name"],
                "y": df["rating"],
                "type": "bar",
            },
        ],
        "layout": {
            "title": "Top Rated Movies",
            "xaxis": {"title": "Movie"},
            "yaxis": {"title": "Rating"},
        },
    }
    return figure

if __name__ == "__main__":
    app.run_server(debug=True)
