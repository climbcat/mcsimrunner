'''

'''
from django.db.models import Model, CharField, TextField, ForeignKey, DateTimeField, PositiveIntegerField
from django.utils import timezone
import json

class InstrGroup(Model):
    ''' corresponds to a folder containing instruments '''
    name = CharField(max_length=200, unique=True)

class Instrument(Model):
    ''' corresponds to a mcstas instrument contained in a certain folder '''
    group = ForeignKey(InstrGroup)
    
    name = CharField(max_length=200, unique=True)
    displayname = CharField(max_length=200)
    docs = TextField()
    
    params_str = CharField(max_length=1000)
    
    @property
    def params(self):
        return json.loads(self.params_str)
    
    @params.setter
    def params(self, p):
        self.params_str = json.dumps(p)

class SimRun(Model):
    ''' corresponds to a simulation run of a particular instrument '''
    instrument = ForeignKey(Instrument)
    
    created = DateTimeField('date created', default=timezone.now)
    started = DateTimeField('date started', blank=True, null=True)
    completed = DateTimeField('date completed', blank=True, null=True)
    failed = DateTimeField('date failed', blank=True, null=True)
    
    neutrons = PositiveIntegerField(default=1000000)
    seed = PositiveIntegerField(default=0)
    scanpoints = PositiveIntegerField(default=1)
    
    params_str = CharField(max_length=1000)
    
    @property
    def params(self):
        return json.loads(self.params_str)
    
    @params.setter
    def params(self, p):
        self.params_str = json.dumps(p)
    
