from __future__ import unicode_literals
from django.contrib.auth.models import User 
from django.db import models

class OauthCheck(models.Model):
  user = models.ForeignKey(User)
  state = models.CharField(max_length=200)

class Board(models.Model):
  board = models.CharField(max_length=50)
  user = models.ForeignKey(User)

# Create your models here.
class Issue(models.Model):
  board = models.ForeignKey(Board)
  repository = models.CharField(max_length=100)
  issueid = models.CharField(max_length=10)
  title = models.TextField()
  url = models.TextField()
  created = models.CharField(max_length=50)
  updated = models.CharField(max_length=50)
  assigned = models.CharField(max_length=50) #assignee.login
  release = models.CharField(max_length=50)
  status = models.CharField(max_length=50)
  comments = models.TextField()
  changed = models.BooleanField(default=False)
  labels = models.CharField(max_length=200,default='')

class Repository(models.Model):
  board = models.ForeignKey(Board)
  repository = models.CharField(max_length=100)

class ReadPermissions(models.Model):
  board = models.ForeignKey(Board)
  username = models.CharField(max_length=50)

class WritePermissions(models.Model):
  board = models.ForeignKey(Board)
  user = models.ForeignKey(User) 
