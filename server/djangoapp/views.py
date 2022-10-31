from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    if request.method == "GET":
        return render(request, 'djangoapp/about.html')
    else:
        return redirect('djangoapp:index')


# Create a `contact` view to return a static contact page
def contact(request):
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html')
    else:
        return redirect('djangoapp:index')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/index.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://eu-gb.functions.cloud.ibm.com/api/v1/namespaces/mofokeng.chk%40gmail.com_dev/actions/dealership-package/get-dealership?blocking=true"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        context['dealer_names'] = [dealer.short_name for dealer in dealerships]
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://eu-gb.functions.cloud.ibm.com/api/v1/namespaces/mofokeng.chk%40gmail.com_dev/actions/dealership-package/get-review?blocking=true"
        # Get dealers from the URL
        dealerships = get_dealer_reviews_from_cf(url, dealer_id)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        context['dealer_details'] = dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            url = "https://eu-gb.functions.cloud.ibm.com/api/v1/namespaces/mofokeng.chk%40gmail.com_dev/actions/dealership-package/post-review?blocking=true"

            review = dict()
            review["time"] = datetime.utcnow().isoformat()
            review["dealership"] = 20
            review["review"] = "This is a great car dealer" 
            review["car_make"] = "BMW"
            review["car_model"] = "120i"
            review["car_year"] = 2022
            review["id"] = dealer_id
            review["name"] = "Sekoai Mongo"
            review["purchase"] = False
            review["purchase_date"] = "02/16/2021"

            json_payload = dict()
            json_payload["review"] = review

            result = post_request(url, json_payload, dealerId=dealer_id)
            print(result)
            return result
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)

