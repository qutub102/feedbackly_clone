from pymongo import MongoClient
import pymongo
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives, EmailMessage
from bson.objectid import ObjectId
import stripe
import os
stripe.api_key = os.environ.get('STRIPE_API')
# Create your views here.
client = MongoClient(os.environ.get('MONGO_URL'))

db = client.dev_feedbackly


def home(request):
    return render(request, 'home.html')


def index(request):
    if request.user.is_anonymous:
        messages.success(request, 'Please Login first')
        return redirect('home.html')
    user_name = request.user.first_name
    credits = db.UserCredits.find_one({"username": request.user.username})
    if credits is None:
        db.UserCredits.insert_one(
            {"username": request.user.username, "credit": 0})
        return render(request, 'index.html', {'userName': user_name, 'credit': 0})
    getsurvey = db.survey.find(
        {'_user': request.user.username}).sort('_id', -1)
    return render(request, 'index.html', {'userName': user_name, 'credit': credits["credit"], 'getSurvey': getsurvey})


def register(request):
    if request.user.is_anonymous:
        if request.method == "POST":
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            if name == '' or email == '' or password == '':
                messages.success(request, 'Please Enter Something')
                return redirect('register.html')
            if password != password2:
                messages.success(request, 'Password did not match!!')
                return redirect('register.html')
            try:
                userEmail = User.objects.get(email=email)
                messages.success(request, "Email Already Exist")
                return render(request, 'register.html')
            except User.DoesNotExist:
                userEmail = None
            if userEmail is None:
                user = User.objects.create_user(email, email, password)
                user.first_name = name
                user.save()
                messages.success(request, 'SignUp Successfull')
                return redirect('login.html')
        return render(request, 'register.html')
    messages.success(request, 'Please Logout First')
    return render(request, 'index.html', {'userName': request.user.first_name})


def Userlogin(request):
    if request.user.is_anonymous:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('index.html')
            else:
                messages.success(request, 'Invalid Information')
                return render(request, 'login.html')
        return render(request, 'login.html')
    messages.success(request, 'Please Logout First')
    return render(request, 'index.html', {'userName': request.user.first_name})


def Userlogout(request):
    logout(request)
    return redirect('home.html')


def addcredit(request):
    if request.user.is_anonymous:
        messages.success(request, 'Please Login first')
        return redirect('home.html')
    return render(request, "payment.html")


def charge(request):
    if request.user.is_anonymous:
        messages.success(request, 'Please Login first')
        return redirect('home.html')
    if request.method == 'POST':
        customer = stripe.Customer.create(
            email=request.user.username,
            name=request.user.first_name,
            source=request.POST['stripeToken']
        )
        customer = stripe.Customer.modify(
            customer.id,
            address={"city": "mumbai", "country": "india", "line1": "unr",
                     "line2": "thane", "postal_code": "421005", "state": "maharashtra"},
        )
        charge = stripe.Charge.create(
            customer=customer,
            amount=5000,
            currency='inr',
            description="Credits"
        )
        db.UserCredits.update_one(
            {"username": request.user.username}, {'$inc': {'credit': 5}})
        messages.success(request, 'Payment Successfull!! Credit Added')
        return redirect("index.html")


def createsurvey(request):
    if request.user.is_anonymous:
        messages.success(request, 'Please Login first')
        return redirect('home.html')
    credits = db.UserCredits.find_one({'username': request.user.username})
    if request.method == 'POST':
        title = request.POST.get('title')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        recipient = request.POST.get('recipient')
        return render(request, "surveyreview.html", {'title': title, 'subject': subject, 'body': body, 'recipient': recipient, 'credit': credits['credit']})
    return render(request, "createsurvey.html", {'credit': credits['credit']})


def surveyreview(request):
    if request.user.is_anonymous:
        messages.success(request, 'Please Login first')
        return redirect('home.html')
    if request.method == 'POST':
        title = request.POST.get('title')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        recipient = request.POST.get('recipient')

        credits = db.UserCredits.find_one({'username': request.user.username})
        if credits['credit'] == 0:
            messages.success(
                request, "Now Don't Have enougfh credit to make survey!!")
            return render(request, "surveyreview.html", {'credit': credits['credit'], 'title': title, 'subject': subject, 'body': body, 'recipient': recipient})
        survey_id = db.survey.insert_one({'title': title, 'subject': subject,
                                          'body': body, 'recipient': recipient, 'yes': 0, 'no': 0, '_user': request.user.username}).inserted_id

        body = f"""<html> <body> <div style = \'text-align: center\'> <h3> I\'d like your Input </h3> <p> PLease answer the following question: </p> <p> {body} <p> <div>
        <a clicktracking=off href=\'http://prod-feedbackly.herokuapp.com/survey/yes/{survey_id}\' style =\'margin: 0px 10px\'> Yes </a></div> <div> <a clicktracking=off href=\'http://prod-feedbackly.herokuapp.com/survey/no/{survey_id}\' > No </a> </div> </div> </body> </html>"""

        mail = EmailMessage(
            subject=subject,
            body=body,
            from_email=f"{title} <rahulsahuhahaha@gmail.com>",
            to=recipient.split(","),
        )
        mail.content_subtype = "html"
        mail.send()

        db.UserCredits.update_one({'username': request.user.username}, {
                                  '$inc': {'credit': -1}})
        credits = db.UserCredits.find_one({'username': request.user.username})
        getsurvey = db.survey.find(
            {'_user': request.user.username}).sort('_id', -1)
        messages.success(request, "Survey has been send.")
        # redirect('index')
        return redirect("index.html", {'userName': request.user.first_name, 'credit': credits['credit'], 'getSurvey': getsurvey})
    return render(request, "surveyreview.html")


def thanks(request, choice, surlen):
    if choice == 'yes':
        db.survey.update_one({'_id': ObjectId(surlen)}, {'$inc': {'yes': 1}})
        return redirect('thank.html')
    else:
        db.survey.update_one({'_id': ObjectId(surlen)}, {'$inc': {'no': 1}})
        return redirect("thank.html")
    # return render(request, "thanks.html")


def thank(request):
    return render(request, "thanks.html")
