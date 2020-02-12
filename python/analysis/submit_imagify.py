#!/usr/bin/env python
import os, sys
import subprocess
import glob
import argparse
parser = argparse.ArgumentParser(description='run batch...')
parser.add_argument('-s', metavar='sample', required=True,  help='sample [train/test]')
parser.add_argument('-d', metavar='delete', required=True,  help='delete old toys? [y/n]')
argus = parser.parse_args()
sample = "" if(argus.s=="train") else "test"
deleteold  = True if(argus.d=="y") else False

indir = "/eos/user/h/hod/clockwork/"
tmpdir = "/afs/cern.ch/user/h/hod/clockwork/tmp/"
p = subprocess.Popen("/bin/rm -f "+tmpdir+"*", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()


def StripToy(ftoy):
   stoy = ftoy.replace(indir+"clockwork"+sample+"_","").replace(".root","")
   return stoy


def Job(ftoy):
   user = os.environ.get('USER')
   stoy = StripToy(ftoy)
   command = "python /afs/cern.ch/user/h/hod/clockwork/imagify.py  -t "+stoy+"  -s "+argus.s
   jobfilename = tmpdir+"img_job."+stoy+".sh"
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
   jobfile.write("export PATH=~/.local/bin:$PATH\n")
   jobfile.write("export LANGUAGE=en_US.UTF-8\n")
   jobfile.write("export LANG=en_US.UTF-8\n")
   jobfile.write("export LC_ALL=en_US.UTF-8\n")
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
   p = subprocess.Popen("/bin/rm -f /eos/user/h/hod/images/*/*/*.jpg", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   out, err = p.communicate()
   p = subprocess.Popen("/bin/rm -f /eos/user/h/hod/imagestest/*/*/*.jpg", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   out, err = p.communicate()



pattern = indir+"clockwork"+sample+"_*.root"
toys = glob.glob(pattern)
for toy in list(toys):
   if(os.path.getsize(toy)<5000000): toys.remove(toy)
print "Found %g good toy files" % len(toys)

for ftoy in toys: Job(ftoy)
print "check with: condor_q"