'''
Mcstas interfacer thread
'''
from django.core.management.base import BaseCommand
from django.utils import timezone
from simrunner.models import SimRun
import subprocess
import os
import time

class ExitException(Exception):
    pass

def mcplot(simrun):
    print 'mcplot %s' % simrun.instr_filepath
    return

def mcrun(simrun):
    # assemble the run command :: NOTE: if we want the mpi param, e.g. "mpi=4", then it goes before instr filepath
    runstr = 'mcrun ' + simrun.instr_filepath + ' -d ' + simrun.data_folder
    runstr = runstr + ' -n ' + str(simrun.neutrons)
    runstr = runstr + ' -N ' + str(simrun.scanpoints)
    if simrun.seed > 0:
        runstr = runstr + ' -s ' + str(simrun.seed)
    for p in simrun.params:
        runstr = runstr + ' ' + p[0] + '=' + p[1]
    
    # pass to mcrun
    process = subprocess.Popen(runstr,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True)
    
    # TODO: implement a timeout (max simulation time)
    (stdoutdata, stderrdata) = process.communicate()
    print(stdoutdata)
    if (stderrdata is not None) and (stderrdata != ''):
        print(stderrdata)
    
    if process.returncode != 0:
        raise Exception('Instrument compile error.')

def mcdisplay(simrun):
    print 'mcdisplay %s' % simrun.instr_filepath
    return

def create_instr_filepath(instr_basedir, group_name, instr_displayname):
    return '%s/%s/%s.instr' % (instr_basedir, group_name, instr_displayname)

def create_data_folderpath(subfolder, basefolder):
    if not os.path.exists(basefolder):
        raise ExitException('Base output folder %s does not exist, exiting.' % basefolder)
    
    return os.path.join(basefolder, subfolder) 

def check_age(simrun, max_mins):
    ''' raises an exception if age is greater than max_mins. Does not alter object simrun '''
    age = simrun.started - simrun.created
    age_mins = age.seconds / 60
    if age_mins > max_mins:
        raise Exception('Age of object has timed out for %s running %s at time %s).' % 
            (simrun.owner_username,simrun.instr_displayname ,simrun.created.strftime("%H:%M:%S_%Y-%m-%d")))

def work():
    ''' gets non-started SimRun objects, updates status and calls sim and plot functions '''
    simrun_set = SimRun.objects.filter(started=None)
    
    for simrun in simrun_set:
        # exceptions raised during the processing block are written to the simrun object, but do not break the processing loop
        try:
            # mark object as processing initiated
            print('processing simrun %s...' % simrun)
            simrun.started = timezone.now()
            simrun.save()
            
            # check simrun object age
            check_age(simrun, max_mins=30)
            
            # init processing
            simrun.data_folder = create_data_folderpath(simrun.__str__(), 'out')
            simrun.instr_filepath = create_instr_filepath('sim', simrun.group_name, simrun.instr_displayname)
            simrun.save()
            
            # process
            mcdisplay(simrun)
            mcrun(simrun)
            mcplot(simrun)
            
            # finish
            simrun.complete = timezone.now()
            simrun.save()
            
            print('processing done for %s' % simrun)
            
        except Exception as e:
            if e is ExitException:
                exit()

            simrun.failed = timezone.now()
            simrun.fail_str = e.message
            simrun.save()
            print('simrun failed: %s') % e.message
    
    if len(simrun_set) > 0:
        print("idle...")

class Command(BaseCommand):
    help = 'runs mcstas to generate simulation output for SimRun instances, and updates their status'

    def add_arguments(self, parser):
        parser.add_argument('--debug', action='store_true', help="runs work() only once")
        
    def handle(self, *args, **options):
        # debug run
        if options['debug']:
            work()
            exit()
        
        print("looking for simruns...")
        
        # execution loop
        while True:
            work()
            time.sleep(1)
