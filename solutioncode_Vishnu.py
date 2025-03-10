# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Y0dlZyaTVKyINy1TSFJr-aYgsGmohjfQ
"""

#INSTALL THE REQUIRED PACKAGES
!pip install fpdf
!pip install schedule

####API KEYE
OMDB_API_KEY = "14ff6ef5"

### OMPORT MODULES HERE
import requests
import pandas as pd
import re
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from fpdf import FPDF
import schedule
import time

#####URL HERE
BOX_OFFICE_URL = "https://www.boxofficemojo.com/weekend/"
ROTTEN_TOMATOES_URL = "https://www.rottentomatoes.com/browse/movies_in_theaters"

#####BOX OFFICE MOJO FUNC TO SCRAPE
def scrape_box_office():
    response = requests.get(BOX_OFFICE_URL)
    if response.status_code != 200:
        print("Error fetching Box Office Mojo data")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    movies = [a.text.strip() for a in soup.select('td.mojo-field-type-release a')]
    return movies[:100]

####ROTTEN TOMATOES SCRAPER
def scrape_rotten_tomatoes():
    response = requests.get(ROTTEN_TOMATOES_URL)
    if response.status_code != 200:
        print("Error fetching Rotten Tomatoes data")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    movies = [a.text.strip() for a in soup.select('a[data-qa="discovery-media-list-item-title"]')]
    return movies[:100]

###OMDB SCRAPER
def fetch_movie_details(title):
    params = {"t": title, "apikey": OMDB_API_KEY}
    #print(f"Fetching data from OMDb: {params}")
    response = requests.get("http://www.omdbapi.com/", params=params)
    data = response.json()
    if data.get("Response") == "False":
        print(f"Error fetching data for: {title} - {data.get('Error', 'Unknown Error')}")
    return data

###FUNCTION TO TRANSFORM THE DATA
def transform_movie_data(movie_data):
    if "Title" not in movie_data:
        print(f"Skipping transformation for missing movie data: {movie_data}")
        return None
    return {
        "Title": re.sub(r'[^a-zA-Z0-9 ]', '', movie_data.get("Title", "Unknown")).title().strip(),
        "Release Date": movie_data.get("Released", "Unknown"),
        "Genre": [g.strip().lower() for g in movie_data.get("Genre", "").split(",")],
        "IMDb Rating": round(float(movie_data.get("imdbRating", "0")), 1) if movie_data.get("imdbRating") != "N/A" else 0,
        "Actors": ", ".join(movie_data.get("Actors", "").split(",")[:3]),
        "Box Office": int(re.sub(r'[^0-9]', '', movie_data.get("BoxOffice", "0"))) if movie_data.get("BoxOffice") else 0,
        "Awards": sum(map(int, re.findall(r'\d+', movie_data.get("Awards", "0")))) if movie_data.get("Awards") else 0,
        "Metascore": int(movie_data.get("Metascore", 0)) if movie_data.get("Metascore") != "N/A" else 0,
        "Language": movie_data.get("Language", "Unknown").lower(),
        "Production": re.sub(r'[^a-zA-Z0-9 ]', '', movie_data.get("Production", "Independent")).strip()
    }

# Extract movie titles
top_movies = list(set(scrape_box_office() + scrape_rotten_tomatoes()))
print("Extracted movie titles:", top_movies)

scrape_rotten_tomatoes()

fetch_movie_details('Dog Man')

# MOVIE DETAILS OBTAINED AND TRANSFORMED
movies_data = [transform_movie_data(fetch_movie_details(title)) for title in top_movies if title]
movies_data = [m for m in movies_data if m is not None] #####REMOVE EMPTY VALUES

# Create DataFrame
df = pd.DataFrame(movies_data)

df.to_csv("movies_data.csv", index=False)

# Save to PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, "Movie Insights Report", ln=True, align='C')

for _, row in df.iterrows():
    pdf.cell(200, 10, f"Title: {row['Title']}", ln=True)
    pdf.cell(200, 10, f"Release Date: {row['Release Date']}", ln=True)
    pdf.cell(200, 10, f"Genre: {', '.join(row['Genre'])}", ln=True)
    pdf.cell(200, 10, f"IMDb Rating: {row['IMDb Rating']}", ln=True)
    pdf.cell(200, 10, f"Actors: {row['Actors']}", ln=True)
    pdf.cell(200, 10, f"Box Office: ${row['Box Office']:,}", ln=True)
    pdf.cell(200, 10, f"Awards: {row['Awards']}", ln=True)
    pdf.cell(200, 10, f"Metascore: {row['Metascore']}", ln=True)
    pdf.cell(200, 10, f"Language: {row['Language']}", ln=True)
    pdf.cell(200, 10, f"Production: {row['Production']}", ln=True)
    pdf.cell(200, 10, "--------------------------------------------------", ln=True)

pdf.output("movies_report.pdf")

print("ETL process completed. CSV and PDF files saved.")

####STRETCH PART WHERE WE VISUALIZE THE DATA AND AUTOMATE THE ETL

plt.figure(figsize=(10, 5))
df_sorted = df.sort_values(by="IMDb Rating", ascending=False)
plt.barh(df_sorted["Title"], df_sorted["IMDb Rating"], color='blue')
plt.xlabel("IMDb Rating")
plt.ylabel("Movie Title")
plt.title("IMDb Ratings for Top Movies")
plt.gca().invert_yaxis()
plt.savefig("imdb_ratings_chart.png")
plt.show()

import pandas as pd
import plotly.express as px
df_sorted = df.sort_values(by="IMDb Rating", ascending=False)

#########BAR PLOT DESCRIBED
fig = px.bar(df_sorted, x="IMDb Rating", y="Title", orientation='h',
              title="IMDb Ratings for Top Movies",
              labels={"IMDb Rating": "IMDb Rating", "Title": "Movie Title"},
              color="IMDb Rating",
              color_continuous_scale="blues")

#########LAYOUT USING PLOTLY
fig.update_layout(yaxis={'categoryorder':'total ascending'})

    # Display the Plotly chart
fig.show()