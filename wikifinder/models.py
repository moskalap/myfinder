from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Article(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    text = models.TextField()
    processed = models.BooleanField(default=False)


class WikiDump(models.Model):
    name = models.TextField()
    processed = models.BooleanField()


class Words(models.Model):
    word = models.TextField(unique=True)


class WordsCount(models.Model):
    word = models.ForeignKey(Words)
    article = models.ForeignKey(Article)
    count = models.IntegerField()


class ArticleToMatrix(models.Model):
    article_id = models.IntegerField()
    col_no = models.IntegerField()


class WordToMatrix(models.Model):
    word_id = models.TextField()
    row_no = models.IntegerField()


class Matrix(models.Model):
    row = models.IntegerField()
    col = models.IntegerField()
    data = models.IntegerField()
