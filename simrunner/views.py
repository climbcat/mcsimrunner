'''
simrunner functional views
'''
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from models import InstrGroup, Instrument, SimRun

def home(req):
    return render(req, template_name='login.html')

def login_post(req):
    form = req.POST
    username = form.get('username', '')
    password = form.get('password', '')
    
    user = authenticate(username=username, password=password)
    if user is None or not user.is_active:
        return redirect(home)
    login(req, user)

    # TODO: enable defaults on user object    
    default_group = 'group1'
    default_instr = 'PSI_DMC'
    
    return redirect('instrument', group_name=default_group, instr_name=default_instr)

def logout_user(req):
    if req.user is not None:
        logout(req)
    
    return redirect(home)

def instrument(req, group_name, instr_name=None):
    group = InstrGroup.objects.get(name=group_name)
    
    # TODO: move the case of instr_name=None to another view, due to the need to render instrument params
    if instr_name == None:
        instr_name = Instrument.objects.filter(group=group)[0].displayname
        
    instr = Instrument.objects.get(name=group_name + '_' + instr_name)
    
    group_names = map(lambda g: g.name, InstrGroup.objects.all())
    instr_names = map(lambda i: i.displayname, Instrument.objects.filter(group=group))
    
    params = instr.params
    neutrons = 1000000
    seed = 0
    numpoints = 1
    
    return render(req, 'instrument.html', {'group_names': group_names, 'instr_names': instr_names, 'group_name': group.name, 'instr_name': instr.displayname, 
                                           'numpoints': numpoints, 'neutrons': neutrons, 'seed': seed, 'params': params})
    
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
