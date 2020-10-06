from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from home import views

urlpatterns = [
    url('home', views.home, name="home"),
    url('index', views.index, name='index'),
    url('register', views.register, name='register'),
    url('login', views.Userlogin, name='login'),
    url('logout', views.Userlogout, name='logout'),
    url('addcredit', views.addcredit, name='addcredit'),
    url('charge', views.charge, name='createsurvey'),
    url('createsurvey', views.createsurvey, name='createsurvey'),
    url('surveyreview', views.surveyreview, name='surveyreview'),
    path('survey/<str:choice>/<str:surlen>', views.thanks, name='thanks'),
    url('thanks', views.thank, name='thank')
]
