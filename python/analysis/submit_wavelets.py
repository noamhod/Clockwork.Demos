#!/usr/bin/env python
import os, sys
import subprocess
import argparse
parser = argparse.ArgumentParser(description='run batch...')
parser.add_argument('-n', metavar='ntoys', required=True,  help='number of toys [integer>0]')
parser.add_argument('-s', metavar='sample', required=True,  help='sample [train/test]')
parser.add_argument('-d', metavar='delete', required=True,  help='delete old toys? [y/n]')
argus = parser.parse_args()
Ntoys = int(argus.n)
sample = argus.s
deleteold  = True if(argus.d=="y") else False

# dir = "/eos/user/h/hod/clockwork/exe"
dir = "/afs/cern.ch/user/h/hod/clockwork/tmp"
p = subprocess.Popen("/bin/rm -f "+dir+"/*", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()


def Job(itoy):
   user = os.environ.get('USER')
   stoy = str(itoy)
   command = "python /afs/cern.ch/user/h/hod/clockwork/clockwork_wavelet_batch.py  -t "+stoy+"  -s "+sample
   jobfilename = dir+"/job."+stoy+".sh"
   outfilename = jobfilename.replace(".sh",".out")
   errfilename = jobfilename.replace(".sh",".err")
   logfilename = jobfilename.replace(".sh",".log")
   subfilename = jobfilename.replace(".sh",".sub")
   p = subprocess.Popen("touch "+logfilename+"; chmod 755 "+logfilename, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   out, err = p.communicate()
   p = subprocess.Popen("/bin/rm -f "+jobfilename.replace(".sh",".*"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   out, err = p.communicate()

   print "writing job to: ",jobfilename
   jobfile = open(jobfilename,"w")
   if(not jobfile): quit()
   jobfile.write("#!/bin/bash\n")
   jobfile.write("echo \"host = $HOSTNAME\"\n")
   jobfile.write(". /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh\n")
   jobfile.write(command+"\n")
   jobfile.write("/bin/rm -f "+logfilename+" \n")
   jobfile.write("/bin/rm -f "+subfilename+" \n")
   jobfile.write("/bin/rm -f "+outfilename+" \n")
   jobfile.close()

   print "writing sub to: ",subfilename
   subfile = open(subfilename,"w")
   subfile.write("executable = "+jobfilename+"\n")
   # subfile.write("arguments  = -t "+stoy+"\n")
   subfile.write("output      = "+outfilename+"\n")
   subfile.write("error       = "+errfilename+"\n")
   subfile.write("log         = "+logfilename+"\n")
   subfile.write("+JobFlavour = \"espresso\"\n")
   subfile.write("queue")
   subfile.close()

   '''
   espresso     = 20 minutes
   microcentury = 1 hour
   longlunch    = 2 hours
   workday      = 8 hours
   tomorrow     = 1 day
   testmatch    = 3 days
   nextweek     = 1 week
   '''
 
   p = subprocess.Popen("chmod 755 "+jobfilename, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   out, err = p.communicate()
   p = subprocess.Popen("condor_submit "+subfilename, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   out, err = p.communicate()
   print out, err

if(deleteold):
   p = subprocess.Popen("/bin/rm -f /eos/user/h/hod/clockwork/clockwork_*.root", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   out, err = p.communicate()
   p = subprocess.Popen("/bin/rm -f /eos/user/h/hod/clockwork/clockworktest_*.root", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   out, err = p.communicate()

for itoy in xrange(Ntoys):
   Job(itoy)

print "check with: condor_q"