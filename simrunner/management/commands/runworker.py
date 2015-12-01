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

def mcplot(simrun, print_mcplot_output=False):
    #print('plotting to output files...')
    
    allfiles = [f for f in os.listdir(simrun.data_folder) if os.path.isfile(os.path.join(simrun.data_folder, f))]
    datfiles_nodir = [f for f in allfiles if os.path.splitext(f)[1] == '.dat']
    pngfiles_nodir = [f for f in allfiles if os.path.splitext(f)[1] == '.png']
    datfiles = map(lambda f: os.path.join(simrun.data_folder, f), datfiles_nodir)
    
    for f in datfiles: 
        cmd = 'mcplot-gnuplot-py -s %s' % f
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True)
        (stdoutdata, stderrdata) = process.communicate()
        
        if print_mcplot_output:
            print(stdoutdata)
            if (stderrdata is not None) and (stderrdata != ''):
                raise Exception('mcplot error: %s' % stderrdata)
        
        p = os.path.splitext(f)[0] + '.png'
        print('plot: %s' % p)
    
    return pngfiles_nodir

def mcdisplay(simrun, print_mcdisplay_output=False):
    #print('generating layout.png...')
    
    cmd = 'mcdisplay -png --multi %s -n1 ' % (simrun.instr_filepath)
    for p in simrun.params:
        cmd = cmd + ' %s=%s' % (p[0], p[1])
    
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True)
    (stdoutdata, stderrdata) = process.communicate()
    if print_mcdisplay_output:
        print(stdoutdata)
        if (stderrdata is not None) and (stderrdata != ''):
            print(stderrdata)
    
    oldfilename = '%s.out.png' % os.path.splitext(simrun.instr_filepath)[0]
    newfilename = os.path.join(simrun.data_folder, 'layout.png')
    if os.path.exists(simrun.data_folder):
        os.rename(oldfilename, newfilename)
    else:
        raise Exception('Data folder must exist before running this function (runworker.mcdisplay).')
        
    print 'layout: %s' % newfilename

def mcrun(simrun, print_mcrun_output=False):
    
    # assemble the run command :: NOTE: if we want the mpi param, e.g. "mpi=4", then it goes before instr filepath
    runstr = 'mcrun ' + simrun.instr_filepath + ' -d ' + simrun.data_folder
    runstr = runstr + ' -n ' + str(simrun.neutrons)
    runstr = runstr + ' -N ' + str(simrun.scanpoints)
    if simrun.seed > 0:
        runstr = runstr + ' -s ' + str(simrun.seed)
    for p in simrun.params:
        runstr = runstr + ' ' + p[0] + '=' + p[1]
    
    print('simrun (%s)...' % runstr)
    
    # pass to mcdisplay
    process = subprocess.Popen(runstr,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True)
    
    # TODO: implement a timeout (max simulation time)
    (stdoutdata, stderrdata) = process.communicate()
    if print_mcrun_output:
        print(stdoutdata)
        if (stderrdata is not None) and (stderrdata != ''):
            print(stderrdata)
    
    if process.returncode != 0:
        raise Exception('Instrument compile error.')
    
    print('data: %s' % simrun.data_folder)

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
            print('processing simrun for %s...' % simrun.instr_displayname)
            simrun.started = timezone.now()
            simrun.save()
            
            # check simrun object age
            check_age(simrun, max_mins=30)
            
            # init processing
            simrun.data_folder = create_data_folderpath(simrun.__str__(), 'out')
            simrun.instr_filepath = create_instr_filepath('sim', simrun.group_name, simrun.instr_displayname)
            simrun.save()
            
            # process
            mcrun(simrun)
            mcdisplay(simrun)
            mcplot(simrun)
            
            # finish
            simrun.complete = timezone.now()
            simrun.save()
            
            print('done (%s secs).' % (simrun.complete - simrun.started).seconds)
            
        except Exception as e:
            if e is ExitException:
                exit()

            simrun.failed = timezone.now()
            simrun.fail_str = e.message
            simrun.save()
            print('simrun fail: %s') % e.message
    
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
