
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

class WikiDump(models.Model):
    name = models.TextField()
    processed = models.BooleanField()

