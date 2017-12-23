
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from datetime import date
# Create your models here.
class Article(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    text = models.TextField()
    processed =models.BooleanField(default=False)

class WikiDump(models.Model):
    name = models.TextField()
    processed = models.BooleanField()

class Words(models.Model):
    word = models.TextField(unique=True)