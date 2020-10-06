from django.db import models
# from django.contrib.auth.models import User
# Create your models here.


class UserCredits(models.Model):
    username = models.CharField(max_length=100)
    credit = models.CharField(max_length=10, default='0')

    def __str__(self):
        return self.credit


class survey(models.Model):
    surveyId = models.CharField(primary_key=True, max_length=50)
    title = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    body = models.CharField(max_length=500)
    recipient = models.CharField(max_length=500)
    yes = models.IntegerField(default=0)
    no = models.IntegerField(default=0)
    _user = models.CharField(max_length=100)

    def __str__(self):
        return str(self.surveyId)
