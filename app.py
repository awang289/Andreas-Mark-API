from flask import Flask, render_template, request, redirect, url_for, session


import argparse
import json
import pprint
import sys
import urllib
import urllib2

import oauth2

app=Flask(__name__)

API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'New York City, NY'
SEARCH_LIMIT = 3
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

CONSUMER_KEY = '52cJsXlD2il67hFKR5R8hA'
CONSUMER_SECRET = 'XDab2xT_n2nh5vJ9CW7BJU-oB1U'
TOKEN = 'OSmbTOGudThV67nTdDh-JJ6IJZRAj90f'
TOKEN_SECRET = 'ccupXmp-tCTG23ya0MZbEx_saCk'


def yelp_request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, path)

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()
    
    print 'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

# I used Yelp's sample function as a placeholder but we should replace this with our own
def search(term, location):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """
    
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return yelp_request(API_HOST, SEARCH_PATH, url_params=url_params)

def get_business(business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path)


def query_api(term, location):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    response = search(term, location)

    businesses = response.get('businesses')
   # location = businesses.index('location')
    
    
    if not businesses:
        return "No businesses found with name {0}".format(term,location)
    
    business_id = businesses[0]['id']
    business_name = businesses[0]['name']
    business_rating = businesses[0]['rating']
    business_address = businesses[0]['location']
    business_phone = businesses[0]['phone']
    business_address = business_address.get('display_address')
    

    str=""
    for item in business_address:
       str = str+item+".  "
    business_address=str
    
    
    ret = {'id':business_id, 'name':business_name, 'address':business_address, 'rating':business_rating, 'phone':business_phone}

    return ret

@app.route("/", methods=["GET","POST"])
def home():
    if request.method=="GET":
        return render_template("home.html")
    else:
        parameters = request.form["keywords"]
        location = request.form["location"]
        name = request.form.get('name')
        address = request.form.get('address')
        rating = request.form.get('rating')
        phone = request.form.get('phone')
        if len(location) == 0:
            results = query_api(parameters, DEFAULT_LOCATION)
        else:
            results = query_api(parameters, location)
        return render_template("results.html", results = results, name = name, address=address, rating = rating, phone=phone)

if __name__=="__main__":
    app.debug=True
    app.run()
