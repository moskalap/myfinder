import json
import requests
from django.shortcuts import render

from django.shortcuts import render, HttpResponse
# Create your views here.

def index(request):
    from wikifinder.engine.data_loader import DataLoader
    dl = DataLoader(
        [
            "/home/przemek/Dokumenty/agh/semestr-5/mownit2/mownit-lab/lab/lab6/res/enwiki-latest-pages-articles1.xml-p10p30302"])
    dl.load_xml_to_queue()
    dl.build_article()
    return HttpResponse('Hello World!')

def search(request):
    parsedData = []
    userData = {}
    username = None
    if request.method == 'POST':
        username = request.POST.get('user')
        return render(request, 'searchresult.html.html', {'data': parsedData})
    userData['name'] = username
    userData['blog'] = 'blog'
    userData['email'] = 'email'
    userData['public_gists'] = 'public_gists'
    userData['public_repos'] = 'public_repos'
    userData['avatar_url'] = 'avatar_url'
    userData['followers'] = 'followers'
    userData['following'] = 'following'

    parsedData.append(userData)
    return render(request, 'search.html', {'data': parsedData})

def data_load(request):
    if request.method == 'POST':
        load_data = request.POST.get('load_data')





def profile(request):
    from wikifinder.engine.data_loader import DataLoader
    dl = DataLoader(
        ["/home/przemek/Dokumenty/agh/semestr-5/mownit2/mownit-lab/lab/lab6/res/enwiki-latest-pages-articles1.xml-p10p30302"])
    dl.load_xml_to_queue()
    dl.build_article()
    return HttpResponse('Hello World!')

