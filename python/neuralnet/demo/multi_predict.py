#!/usr/bin/env python
import os, sys
import subprocess
import ROOT
from ROOT import *
import glob
import argparse
parser = argparse.ArgumentParser(description='predict...')
parser.add_argument('-t', metavar='toyid',   required=True,  help='toy id [integer>0 or 0 for all]')
parser.add_argument('-s', metavar='sample',  required=True,  help='sample [train/test]')
parser.add_argument('-d', metavar='drawopt', required=True,  help='drawopt [scat/cont4/mpltlib]')
parser.add_argument('-p', metavar='species', required=True,  help='species [bkg/sig]')
argus = parser.parse_args()
runtype = argus.s
drawopt = argus.d
species = argus.p
suffix = ".png" if(drawopt=="mpltlib") else ".jpg"
model  = "noam_vgg_mtplotlib8k" if(drawopt=="mpltlib") else "noam10k_"+drawopt
arg4   = " --width 64 --height 64" if(drawopt=="mpltlib") else " --width 32 --height 32 --flatten 1"

## styles
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetPadLeftMargin(0.13)
ROOT.gStyle.SetPadRightMargin(0.13)

def GetToyStr(itoy):
   stoy = str(itoy)
   if(itoy<10):                   stoy = "0000"+stoy
   if(itoy>=10 and itoy<100):     stoy = "000"+stoy
   if(itoy>=100 and itoy<1000):   stoy = "00"+stoy
   if(itoy>=1000 and itoy<10000): stoy = "0"+stoy
   return stoy

runtype = "images" if(runtype=="train") else "imagestest"
pattern = "/Users/hod/cernbox/"+runtype+"/"+drawopt+"/"+species+"/"+species+"_"+drawopt+"_*"+suffix

toys = []
if(argus.t=="0"):
   print "searcing in",pattern
   toys = glob.glob(pattern)
else:
   toys = ["/Users/hod/cernbox/"+runtype+"/"+drawopt+"/"+species+"/"+species+"_"+drawopt+"_"+argus.t+".jpg"]
Ntoys = len(toys)
print "Found %g good toy files" % Ntoys


title = drawopt+" "+species+" "+drawopt
hbkg = TH1D("hpredict_bkg_"+drawopt+"_"+species+"_"+drawopt,title+";probability;N_{toys}",1000,0.,1.)
hsig = TH1D("hpredict_sig_"+drawopt+"_"+species+"_"+drawopt,title+";probability;N_{toys}",1000,0.,1.)

def send(filename):
   cmd = "python predict.py"
   arg1 = " --image "+filename
   arg2 = " --model output/"+model+".model"
   arg3 = " --label-bin output/"+model+".pickle "
   command = cmd+arg1+arg2+arg3+arg4
   p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   out, err = p.communicate()
   # print out, err
   ### fill
   print filename
   # print out
   probabilities = out.split("\n")[0].replace("[","").replace("]","").replace("preds: ","").split(" ")
   while "" in probabilities: probabilities.remove("")
   # print "probabilities=",probabilities
   pbkg = float(probabilities[0])
   psig = float(probabilities[1])
   print "pbkg=%g, psig=%g" % (pbkg,psig)
   hsig.Fill(psig)
   hbkg.Fill(pbkg)

for toy in toys:
   send(toy)


fname = "predictions_"+drawopt+"_"+species+"_"+drawopt
f = TFile(fname+".root", "RECREATE")
f.cd()
hsig.Write()
hbkg.Write()
f.Write()
f.Close()

cnv = TCanvas("c","",1000,500)
cnv.Divide(2,1)
p1 = cnv.cd(1)
p2 = cnv.cd(2)
p1.cd()
p1.SetLogy()
p1.SetTicks(1,1)
hbkg.Draw("hist")
p2.cd()
p2.SetLogy()
p2.SetTicks(1,1)
hsig.Draw("hist")
cnv.Update()
cnv.SaveAs(fname+".pdf")