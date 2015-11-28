'''

'''
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

def home(req):
    # TODO: render login form
    return render(req, template_name='dummy.html', context = {'word': 'word!'})

def login_post(req):
    '''
    # TODO: 
    # 1) process credentials
    # 2) redirect to home on failure
    # 3) redirect to instrument on success
    return render(req, template_name='dummy.html', context = {'word': 'login_post'})

def logout(req):
    # TODO:
    # 1) logout the current user
    # 2) redirect to home
    return render(req, template_name='dummy.html', context = {'word': 'logout'})

def instrument(req, group_name, instr_name):
    # TODO:
    # 1) get group and instrument from db
    # 2) get all group_names
    # 3) get instrument_names in this group
    # 4) render instrument page
    return render(req, template_name='dummy.html', context = {'word': 'instrument'})

def instrument_post(req):
    # TODO: 
    # 1) get fields from form
    # 2) create simrun object
    # 3) redirect to instrument
    return render(req, template_name='dummy.html', context = {'word': 'instrument_post'})

def simrun(req, simrun):
    # TODO:
    # 1) get simrun object from db
    # 2) render simrun page (consisting mostly of hrefs to static content)
    return render(req, template_name='dummy.html', context = {'word': 'simrun'})
