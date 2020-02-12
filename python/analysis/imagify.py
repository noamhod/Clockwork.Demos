#!/usr/bin/env python
import os, sys
import math
import ROOT
from ROOT import *
from array import array
import glob
import numpy as np
# import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


import argparse
parser = argparse.ArgumentParser(description='imagify...')
parser.add_argument('-t', metavar='toy', required=True,  help='toy number [toy_id or 0 to run all]')
parser.add_argument('-s', metavar='sample', required=True,  help='sample [train/test]')
argus = parser.parse_args()
sample = "" if(argus.s=="train") else "test"


## styles
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetPadLeftMargin(0)
ROOT.gStyle.SetPadRightMargin(0)
ROOT.gStyle.SetPadBottomMargin(0)
ROOT.gStyle.SetPadTopMargin(0)

indir = "/eos/user/h/hod/clockwork/"
outdir = "/eos/user/h/hod/"
# ###############################################################################
# indir = "/Users/hod/Downloads/clockwork2019/"
# outdir = "/Users/hod/Downloads/clockwork2019/"
# ###############################################################################

toys = []
if(argus.t=="0"):
   toys = glob.glob(indir+"clockwork"+sample+"_*.root")
else:
   toys = [indir+"clockwork"+sample+"_"+argus.t+".root"]
for toy in list(toys):
   if(os.path.getsize(toy)<5000000): toys.remove(toy)
Ntoys = len(toys)
print "Found %g good toy files" % Ntoys

def StripToy(ftoy):
   stoy = ftoy.replace(indir+"clockwork"+sample+"_","").replace(".root","")
   return stoy

subdir = "images/" if(sample=="") else "imagestest/"

##############################################################
### for matplotlib plots
def htoarr(h):
   arr = []
   for by in xrange(h.GetNbinsY()+1,1,-1):
      tmp = []
      for bx in xrange(1,h.GetNbinsX()+1):
         z = h.GetBinContent(bx,by)
         z = abs(math.log(z)) if(z>0) else 0
         tmp.append(z)
      arr.append(tmp)
   arr = np.array(arr)
   return arr

def plotarr(arr,name,show=False):
   # plt.imshow(barr, cmap='Greys', aspect='auto',vmax=abs(barr).max(), vmin=-abs(barr).max()) 
   # plt.imshow(arr, cmap='gist_stern', aspect='auto',vmax=1, vmin=0, interpolation='nearest') 
   # plt.imshow(arr, cmap='gist_ncar', aspect='auto',vmax=1, vmin=0) 
   # plt.imshow(arr, cmap='gist_stern_r', aspect='auto',vmax=1, vmin=0) 
   # plt.imshow(arr, cmap='Spectral', aspect='auto',vmax=1, vmin=0) 
   plt.imshow(arr, cmap='hot', aspect='auto',vmax=1, vmin=0) 
   if(show): plt.show()
   plt.axis('off')
   # plt.xscale("symlog")
   plt.margins(0)
   plt.subplots_adjust(left=0, right=1, top=1, bottom=0) ## no margins
   print "saving",name
   plt.savefig(name)  
##############################################################


# set maximum
for ftoy in toys:
   fIn = TFile(ftoy,"READ")
   stoy = StripToy(ftoy)
   bkg = fIn.Get("ToyBkg_histo_"+stoy)
   sig = fIn.Get("Toy_histo_"+stoy)

   bkg.RebinX(2)
   sig.RebinX(2)
   barr = htoarr(bkg)
   sarr = htoarr(sig)
   barr = barr/abs(barr).max()
   sarr = sarr/abs(sarr).max()
   plotarr(barr,outdir+subdir+"mpltlib/bkg/bkg_mpltlib_"+stoy+".png")
   plotarr(sarr,outdir+subdir+"mpltlib/sig/sig_mpltlib_"+stoy+".png")
   del barr
   del sarr

   # bkgcln = bkg.Clone("bkgcln")
   # sigcln = sig.Clone("sigcln")
   # bkgcln.RebinX(10)
   # sigcln.RebinX(10)
   # barr = htoarr(bkgcln)
   # sarr = htoarr(sigcln)
   # barr = barr/abs(barr).max()
   # sarr = sarr/abs(sarr).max()
   # plotarr(barr,outdir+subdir+"mpltlib/bkg/bkg_mpltlib_"+stoy+".png")
   # plotarr(sarr,outdir+subdir+"mpltlib/sig/sig_mpltlib_"+stoy+".png")
   # del barr,bkgcln
   # del sarr,sigcln

   # cnv = TCanvas("c","",500,500)
   # bkg.GetXaxis().SetTickLength(0)
   # bkg.GetYaxis().SetTickLength(0)
   # bkg.GetZaxis().SetTickLength(0)
   # bkg.Draw("scat")
   # cnv.Update()
   # cnv.SaveAs(outdir+subdir+"scat/bkg/bkg_scat_"+stoy+".jpg")
   # cnv = TCanvas("c","",500,500)
   # sig.GetXaxis().SetTickLength(0)
   # sig.GetYaxis().SetTickLength(0)
   # sig.GetZaxis().SetTickLength(0)
   # sig.Draw("scat")
   # cnv.Update()
   # cnv.SaveAs(outdir+subdir+"scat/sig/sig_scat_"+stoy+".jpg")
   # 
   # bkg.RebinX(20)
   # sig.RebinX(20)
   # bkg.RebinY(2)
   # sig.RebinY(2)
   # 
   # cnv = TCanvas("c","",500,500)
   # bkg.GetXaxis().SetTickLength(0)
   # bkg.GetYaxis().SetTickLength(0)
   # bkg.GetZaxis().SetTickLength(0)
   # bkg.Scale(1./bkg.GetMaximum())
   # bkg.SetMinimum(0)
   # # bkg.SetMaximum(1)
   # bkg.SetMaximum(0.25)
   # bkg.Draw("cont4")
   # # bkg.DrawNormalized("cont4")
   # cnv.Update()
   # cnv.SaveAs(outdir+subdir+"cont4/bkg/bkg_cont4_"+stoy+".jpg")
   # cnv = TCanvas("c","",500,500)
   # sig.GetXaxis().SetTickLength(0)
   # sig.GetYaxis().SetTickLength(0)
   # sig.GetZaxis().SetTickLength(0)
   # sig.Scale(1./sig.GetMaximum())
   # sig.SetMinimum(0)
   # # sig.SetMaximum(1)
   # sig.SetMaximum(0.25)
   # sig.Draw("cont4")
   # # sig.DrawNormalized("cont4")
   # cnv.Update()
   # cnv.SaveAs(outdir+subdir+"cont4/sig/sig_cont4_"+stoy+".jpg")

   fIn.Close()