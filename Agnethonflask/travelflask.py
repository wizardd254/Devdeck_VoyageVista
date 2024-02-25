from flask import Flask, jsonify,request, url_for, redirect, render_template
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from tensorflow.python.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import numpy as np
from joblib import load
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
from flask_cors import CORS

from transformers import pipeline
import pandas as pd
import wikipedia
import pandas as pd
from serpapi import GoogleSearch
import requests

def fetch_weather(city):
    api_key = "1a531c047d464eb6b4941425242502"
    # WeatherAPI.com API endpoint for current weather
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"

    # Send GET request to the API
    response = requests.get(url)
    weather_info = {}
    # Check if request was successful
    if response.status_code == 200:
        # Parse JSON response
        data = response.json()

        # Extract relevant weather information
        location = data['location']['name']
        weather_description = data['current']['condition']['text']
        temperature = data['current']['temp_c']
        humidity = data['current']['humidity']
        wind_speed = data['current']['wind_kph']

        # Print weather information
        weather_info = {
            "Location": city,
            "Description": weather_description,
            "Temperature": f"{temperature}°C",
            "Humidity": f"{humidity}%",
            "Wind Speed": f"{wind_speed} km/h"
         }
    else:
        # Print error message if request failed
        print(f"Failed to fetch weather data for {city}.")
     
    return weather_info

def getimages(place,city,state):
  api_key = 'c77f4ebdffaeb0ca01035ce5c49b2b5c5d998e37591616d07f0e0ec4691b7082'
  search=GoogleSearch({
      'engine': 'google_maps',
      'type': 'search',
      'q' : f'{place} , {city} , {state}',
      'api_key': 'c77f4ebdffaeb0ca01035ce5c49b2b5c5d998e37591616d07f0e0ec4691b7082',
  })
  revsa=[]
  imsa=[]
  try:
    results = search.get_dict()
    
    reviews=results['place_results']
    photo=reviews["thumbnail"]
    images=reviews["images"]
    for image in images:
      imsa.append(image['thumbnail'])

    user_reviews=reviews["user_reviews"]
    revs=user_reviews["summary"]
    for rev in revs:
      revsa.append(rev['snippet'])
    
    return imsa , revsa
  except:
    print(f'Not sufficent data found for {place}')

    return imsa , revsa

# Function to extract a concise introduction from the Wikipedia content
def extract_description(text):
    # Attempt to split the text to get a concise introduction
    # Splits the content at every new line and returns the first part
    parts = text.split("\n")  # Splits the content at every new line
    if parts:
        return parts[0]  # Return the first part as the description
    return text  # Fallback to the full text if no split is possible

# Function to fetch descriptions from Wikipedia and save them in a CSV
def fetch_descriptions_and_save(places):
    data = []  # Prepare a list to hold your data
    df=pd.read_csv('C:\Agnethonflask\TopPlacestoVisit.csv')

    # Set English as the language for Wikipedia
    wikipedia.set_lang("en")
    
    for place in places:
        try:
            # Fetch the page for the current place
            page = wikipedia.page(place)
            # Extract the description from the content
            description = extract_description(page.content)
            filtered_df = df[df['Name'] == place]
            rating = str(filtered_df['Google review rating'].iloc[0])
            city = str(filtered_df['City'].iloc[0])
            state = str(filtered_df['State'].iloc[0])
            imageslist,reviewslist = getimages(place,city,state)
            weatherdict = fetch_weather(city)
        except wikipedia.exceptions.PageError:
            # No page found for the place
            description = "No description available"
        except wikipedia.exceptions.DisambiguationError:
            # Multiple pages found for the place
            description = "Multiple pages found, specify further."
        
        # Append the place and its description to your data list
        data.append([place, description,reviewslist,imageslist,weatherdict,rating])
    
    # Convert the list to a DataFrame
    df = pd.DataFrame(data, columns=['Name', 'Description','Reviews','Images','Weather','Rating'])
    

    # Optionally return the DataFrame if you want to use it directly
    return df

# Assuming 'placelist' is your list of places
# For example usage, replace 'placelist' with your actual list of place names



# If you want to print the DataFrame to see the output

# Define the function
def get_tqa_answer(query, table):
    if isinstance(table, list):
        # Assuming 'table' is a list of dictionaries, convert it to a DataFrame
        table = pd.DataFrame(table)

    # Ensure the table is in string format for TAPAS compatibility
    table = table.astype(str)
    # Initialize the TAPAS model pipeline
    tqa_pipeline = pipeline(task="table-question-answering", model="google/tapas-base-finetuned-wtq")
    # Use the model to get the answer to the query based on the table
    answer = tqa_pipeline(table=table, query=query)["answer"]
    # Return the answer
    return answer

# Example usage
table = pd.read_csv("C:\Agnethonflask\TopPlacestoVisit.csv")  # Assuming your CSV is correctly formatted and located
table = table[:10]  # Use only the first 10 rows for example
query = "I like parks"



def recommend_city(zone=None, state=None, type=None, significance=None, time_to_visit=None):
    knn_loaded = load('travel_model.joblib')
    df=pd.read_csv('C:\Agnethonflask\TopPlacestoVisit.csv')
    
    X = df[['Zone','State','Type','Significance', 'Best Time to visit']]  
    y = df['City']  

    encoder = OneHotEncoder(handle_unknown='ignore')
    X_encoded = encoder.fit_transform(X.values).toarray()

    
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    if state is None and zone is None:
        states = df['State'].unique()
        state = np.random.choice(states)

    if state is None or state not in df['State'].unique():
        states = df[df['Zone'] == zone]['State'].unique()
        state = np.random.choice(states)
    
    if zone is None:
        zone = df[df['State'] == state]['Zone'].unique()[0]  
   
    if type is None or type not in df['Type'].unique():
        types = df['Type'].unique()
        type = np.random.choice(types)
        
    if significance is None or significance not in df['Significance']:
        significances = df['Significance'].unique() 
        significance = np.random.choice(significances)
        
    
    if time_to_visit is None or time_to_visit not in df['Best Time to visit']:
        times = df['Best Time to visit'].unique()
        time_to_visit = np.random.choice(times)

    new_input = pd.DataFrame([[zone, state, type, significance, time_to_visit]], columns=['Zone', 'State', 'Type', 'Significance', 'Best Time to visit'])
    new_input_encoded = encoder.transform(new_input).toarray()

    prediction = knn_loaded.predict(new_input_encoded)
    predicted_city = label_encoder.inverse_transform(prediction)[0]  
    places = df.loc[(df['City'] == predicted_city) & (df['Type'] == type), 'Name'].unique()
    return predicted_city , places





zone_input="Western"
state_input="Maharashtra"
type_input="Beach"
significance_input="Scenic"
time_input="All"


app = Flask(__name__)
CORS(app)
@app.route('/', methods=['POST', 'GET'])
def predict():
    if request.method == 'POST':
        
        data = request.json
        form_data=data.get('formData')

        zone_input = form_data.get('zone', None)
        state_input = form_data.get('state',None)
        type_input = form_data.get('type', None)
        time_input = form_data.get('time', None)
        city_input = form_data.get('city', None)

        significance_input = form_data.get('significance', None)
        print(zone_input)
        print(state_input)
        print(time_input)
        print(significance_input)
        print(type_input)


        user_preference = form_data.get('userPreference')

        city,placelist=recommend_city(zone_input,state_input,type_input,significance_input,time_input)
        global description_df 
        description_df=fetch_descriptions_and_save(placelist)
        description_dict_list = description_df[['Name', 'Description','Images','Rating']].to_dict(orient='records')
        global weather1
        weather1=fetch_weather(city)
        print(weather1)

        print(description_dict_list)
        print(city)
        print(placelist)
        response_data = {
            'city': city,
            'placelist': placelist.tolist(),  # Convert DataFrame to a list for JSON serialization
            'description_list':description_dict_list,
            'weather':weather1,
        }

        return jsonify(response_data)
              
    else:
        return "hello"

@app.route('/query', methods=['POST'])
def query():
    if request.method == 'POST':
        data = request.json  # Assuming data is sent as JSON in the request body
        placelist = data.get('placelist')
        query = data.get('message')
        print(placelist)
        print(query)

        # Process the data and perform the desired operations
        
        answerofcb = get_tqa_answer(query, description_df)
        print(answerofcb)

        # Return the result as JSON
        return jsonify({'answerofcb': answerofcb})
    else:
        return "Method not allowed", 405    

@app.route('/weather', methods=['POST'])
def get_weather():
    if request.method == 'POST':
        data = request.json  # Assuming data is sent as JSON in the request body
        city = data.get('city')

        # Fetch weather information for the given city
        weather_info = weather1

        # Return the weather information as JSON response
        return jsonify(weather_info)
    else:
        # If the request method is not POST, return an error response
        return jsonify({'error': 'Method not allowed'}), 405    


if __name__ == '__main__':
    app.run(debug=True)










