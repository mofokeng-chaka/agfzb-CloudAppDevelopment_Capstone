import requests
import json
import os
from .models import CarDealer, DealerReview
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions

# Load environment variables from .env file
load_dotenv() 

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        CF_USERNAME = os.environ.get('CF_USERNAME')
        CF_PASSWORD = os.environ.get('CF_PASSWORD')
        params = dict()
        for key in kwargs:
            params[key] = kwargs[key]

        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=params, auth=HTTPBasicAuth(CF_USERNAME, CF_PASSWORD))                                    
    except:
        # If any error occurs
        print("Network exception occurred")
    if "api_key" in kwargs:
        response =requests.get(url, headers={'Content-Type': 'application/json'}, json=params, auth=HTTPBasicAuth('apikey', kwargs["api_key"]))
    status_code = response.status_code
    print("With status {} ".format(status_code))
    return response.json()


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs, json_payload)
    print("POST from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        CF_USERNAME = os.environ.get('CF_USERNAME')
        CF_PASSWORD = os.environ.get('CF_PASSWORD')
        response = requests.post(url, headers={'Content-Type': 'application/json'}, params=kwargs, json=json_payload, auth=HTTPBasicAuth(CF_USERNAME, CF_PASSWORD))                                    
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    return response.json()


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # For each dealer object
        for dealer in json_result["response"]["result"]["result"]:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    # Call get_request with a URL parameter
    try:
        json_result = get_request(url, dealerId=dealer_id)

        # Get its content in `response` object
        dealer_doc = json_result["response"]["result"]["result"][0]
        # Create a DealerReview object with values in `doc` object
        sentiment = analyze_review_sentiments(dealer_doc["review"])
        dealer_obj = DealerReview(dealership=dealer_doc["dealership"], name=dealer_doc["name"], purchase=dealer_doc["purchase"],
                                    id=dealer_doc["id"], review=dealer_doc["review"], purchase_date=dealer_doc["purchase_date"],
                                    car_make=dealer_doc["car_make"], car_model=dealer_doc["car_model"], 
                                    car_year=dealer_doc["car_year"], sentiment=sentiment)
        return dealer_obj
    except requests.exceptions.HTTPError as e:
        print(e)


# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_by_id_from_cf(url, dealer_id):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealer_id)
    if json_result:
        # For each dealer object
        for dealer in json_result["response"]["result"]["result"]:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/e8a6e6dc-3579-4fe3-8570-d6a450cc37a8"
    api_key = os.environ.get('API_KEY')
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )

    natural_language_understanding.set_service_url(url)

    response = natural_language_understanding.analyze(
        text=text,
        features=Features(
            entities=EntitiesOptions(emotion=True, sentiment=True, limit=2),
            keywords=KeywordsOptions(emotion=True, sentiment=True,limit=2)
        )
    ).get_result() 
    result = response["keywords"][0]
    return result["sentiment"]["label"]





