from django.conf.urls import url

from wikifinder import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^searchresult/$', views.search, name='searchresult'),
    url(r'^data_load/$', views.data_load, name='searchresult'),
]
