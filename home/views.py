# import sendgrid
# from sendgrid.helpers.mail import *
# from sendgrid.helpers.mail import (
#     From, To, PlainTextContent, HtmlContent, Mail)
import uuid
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from .models import UserCredits, survey
import stripe
stripe.api_key = "sk_test_51HSGx4HsHAyz3jSs2o0SWfEbJra9ARDSX2gMokooTSMvMzIGP8qxtGz7N8thGD45e5Wyntcm7zbuZaiJnWi0OtGh00jDmNeLRJ"
# Create your views here.


def index(request):
    if request.user.is_anonymous:
        messages.success(request, 'Please Login first')
        return redirect('login.html')
    user_name = request.user.first_name
    print(user_name)
    getSurvey = survey.objects.filter(_user=request.user.username)
    credits = UserCredits.objects.filter(username=request.user.username)
    if(credits.exists()):
        return render(request, 'index.html', {'userName': user_name, 'credit': credits[0].credit, 'getSurvey': getSurvey})
    upuser = UserCredits(credit=0, username=request.user.username)
    # print(upuser)
    upuser.save()

    return render(request, 'index.html', {'userName': user_name, 'credit': 0, 'getSurvey': getSurvey})


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
    getSurvey = survey.objects.filter(_user=request.user.username)
    messages.success(request, 'Please Logout First')
    return render(request, 'index.html', {'userName': request.user.first_name, 'getSurvey': getSurvey})


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
    getSurvey = survey.objects.filter(_user=request.user.username)
    messages.success(request, 'Please Logout First')
    return render(request, 'index.html', {'userName': request.user.first_name, 'getSurvey': getSurvey})


def Userlogout(request):
    logout(request)
    return redirect('login.html')

# Survey Part


def createsurvey(request):
    credits = UserCredits.objects.filter(username=request.user.username)
    if request.method == 'POST':
        title = request.POST.get('title')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        recipient = request.POST.get('recipient')
        return render(request, "surveyreview.html", {'title': title, 'subject': subject, 'body': body, 'recipient': recipient, 'credit': credits[0].credit})
    return render(request, "createsurvey.html", {'credit': credits[0].credit})


def surveyreview(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        recipient = request.POST.get('recipient')
        # print(recipient.split(","))

        createSurvey = survey(surveyId=uuid.uuid1(), title=title, subject=subject, body=body,
                              recipient=recipient, _user=request.user.username)
        createSurvey.save()
        fetchSurvey = survey.objects.all()
        print(fetchSurvey)
        surLen = fetchSurvey.count()
        print(surLen)
        print("ID >>> ", fetchSurvey[surLen-1].surveyId)
        body = f"""<html> <body> <div style = \'text-align: center\'> <h3> I\'d like your Input </h3> <p> PLease answer the following question: </p> <p> {body} <p> <div>
        <a href=\'http://localhost:8000/survey/yes/{fetchSurvey[surLen-1].surveyId}\' style =\'margin: 0px 10px\'> Yes </a></div> <div> <a href=\'http://localhost:8000/survey/no/{fetchSurvey[surLen-1].surveyId}\' > No </a> </div> </div> </body> </html>"""

        mail = EmailMessage(
            subject=subject,
            body=body,
            from_email=f"{title} <rahulsahuhahaha@gmail.com>",
            to=recipient.split(","),
        )
        mail.content_subtype = "html"
        mail.send()
        # print(uuid.uuid1())
        credits = UserCredits.objects.filter(username=request.user.username)
        if int(credits[0].credit) == 0:
            messages.success(
                request, "Now Don't Have enougfh credit to make survey!!")
            return render(request, "surveyreview.html", {'credit': credits[0].credit})
        upcredit = int(credits[0].credit) - 1
        upuser = UserCredits.objects.filter(
            username=request.user.username).update(credit=str(upcredit))
        getSurvey = survey.objects.filter(_user=request.user.username)
        messages.success(request, "Survey has been send.")
    return render(request, "index.html", {'userName': request.user.first_name, 'credit': credits[0].credit, 'getSurvey': getSurvey})
    return render(request, "surveyreview.html")


def addcredit(request):
    if request.user.is_anonymous:
        messages.success(request, 'Please Login first')
        return redirect('login.html')
    credits = UserCredits.objects.filter(username=request.user.username)
    # upcredit = int(credits[0].credit) + 5
    # print(type(upcredit))
    # upuser = UserCredits.objects.filter(
    #     username=request.user.username).update(credit=str(upcredit))
    # messages.success(request, 'Payment Successfull')
    return render(request, "payment.html")


def charge(request):
    if request.user.is_anonymous:
        messages.success(request, 'Please Login first')
        return redirect('login.html')
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
        credits = UserCredits.objects.filter(username=request.user.username)
        upcredit = int(credits[0].credit) + 5
        upuser = UserCredits.objects.filter(
            username=request.user.username).update(credit=str(upcredit))
        messages.success(request, 'Payment Successfull!! Credit Added')
        return redirect("index.html")


def thanks(request, choice, surlen):
    print(choice, surlen)
    res = survey.objects.filter(surveyId=surlen)
    if choice == 'yes':
        response = survey.objects.filter(
            surveyId=surlen).update(yes=res[0].yes + 1)
    else:
        response = survey.objects.filter(
            surveyId=surlen).update(no=res[0].no + 1)
    return render(request, "thanks.html")
