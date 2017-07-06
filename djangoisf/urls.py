from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^parse/?$', views.parse, name='parse'),
    url(r'^version/?$', views.version, name='version')
]
