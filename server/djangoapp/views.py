from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .restapis import *
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def about(request):
    context = {}
    if request.method == "GET":
        return render(request,'djangoapp/about.html',context)


# Create an `about` view to render a static about page
# def about(request):
# ...


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['password']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username,first_name=first_name,last_name=last_name,password=password)
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://7a7b6d28.us-south.apigw.appdomain.cloud/api/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        context['dealerships']=dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...

def get_dealer_details(request, dealer_id):
    context = {}
    dealer_reviews = []
    dealer_details = []
    dealer_id_temp = []

    if request.method == "GET":
        url1 = "https://7a7b6d28.us-south.apigw.appdomain.cloud/api/api/review"
        reviews = get_dealer_reviews_from_cf(url1, dealer_id)

        for review in reviews:
            dealer_reviews.append(review)
        
        url2 = "https://7a7b6d28.us-south.apigw.appdomain.cloud/api/api/dealership"
        dealers = get_dealers_from_cf(url2)
        
        for dealer in dealers:
            dealer_id_temp = dealer.id
            if dealer_id_temp == dealer_id:
                dealer_details.append(dealer)
        
        context = {
            "dealer_id": dealer_id,
            "dealer_details" : dealer_details,
            "reviews" : dealer_reviews
        }

        dealer_details = render(request, 'djangoapp/dealer_details.html', context)
        return dealer_details

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealer_id):
    if request.user.is_authenticated:
        new_review=dict()
        new_review["dealership"]=dealer_id
        new_review["time"] = datetime.utcnow().isoformat()
        new_review["car_make"]="Ford"
        new_review["car_model"]="Mustang"
        new_review["car_year"]="2007"
        new_review["purchase"]=True
        new_review["purchase_date"]="07-01-2007"
        new_review["review"]="Great Car dealer"
        new_review["name"]="User"

        json_payload={}
        json_payload["review"]=new_review

        url="https://7a7b6d28.us-south.apigw.appdomain.cloud/api/api/review"
        parameters={"dealership":dealer_id}
        print("parameters: ",parameters)
        post_response=post_request(url,payload=json_payload)
        print(post_response)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
    else:
        print("Please login to submit a review.")
