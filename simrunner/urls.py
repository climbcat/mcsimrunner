"""mcweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from simrunner import views

urlpatterns = [
    url(r'^instrument/(?P<group_name>\w+)/(?P<instr_name>\w+)/?$', views.instrument, name="instrument"),
    url(r'^startsim/?$', views.instrument_post, name="instrument_post" ),

    url(r'^sim/(?P<simrun>\w)/?$', views.simrun, name="simrun" ),

    url(r'^login/?$', views.login_post, name='login_post'),
    url(r'^logout/?$', views.logout, name='logout'),
    url(r'^', views.home, name="home" ),
]
