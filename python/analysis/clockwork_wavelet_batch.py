#!/usr/bin/env python
import os, sys
import math
from ROOT import *
import ROOT
import numpy as np
import pywt
import statistics


## styles
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetPadLeftMargin(0.13)
ROOT.gStyle.SetPadRightMargin(0.13)


import os, sys
import argparse
parser = argparse.ArgumentParser(description='run batch...')
parser.add_argument('-t', metavar='toy', required=True,  help='toy number [integer>0]')
parser.add_argument('-s', metavar='sample', required=True,  help='sample [train/test]')
argus = parser.parse_args()
itoy = int(argus.t)
sample = "" if(argus.s=="train") else "test"
outdir = "/eos/user/h/hod/clockwork/"
indir = "/afs/cern.ch/user/h/hod/clockwork/"
channel = "ee"
### randomise the toys...
rndgen = TRandom()
rndgen.SetSeed()
uniformnum = int(rndgen.Uniform(1e6))
RooRandom.randomGenerator().SetSeed(itoy+uniformnum)

############################################################
############################################################
############################################################


### get the resolution
fPeterRes = TFile(indir+"ee_relResolFunction.root","READ")
fRes = fPeterRes.Get("relResol_dedicatedTF")
sfRes = "sqrt(pow(([0]+[1]/x+[2]/pow(x,2)+[3]*x+[4]*pow(x,2))*sqrt(pow([5],2)+pow([6]/sqrt(x),2)+pow([7]/x,2)),2)+pow((1.0-([0]+[1]/x+[2]/pow(x,2)+[3]*x+[4]*pow(x,2)))*sqrt(pow([8],2)+pow([9]/sqrt(x),2)+pow([10]/x,2)),2))"
for n in xrange(0,fRes.GetNpar()):
   print fRes.GetParName(n)+": "+str(fRes.GetParameter(n))
   sfRes = sfRes.replace("["+str(n)+"]",str(fRes.GetParameter(n)))
fRes.SetLineColor(ROOT.kRed)

### get the acceptance*efficiency
fPeterAcc = TFile(indir+"ee_accEffFunction.root","READ")
fAcc = fPeterAcc.Get("accEff_TF1")
sfAcc = "[0]+[1]/x+[2]/pow(x,2)+[3]/pow(x,3)+[4]/pow(x,4)+[5]/pow(x,5)+[6]*x+[7]*pow(x,2)"
for n in xrange(0,fAcc.GetNpar()):
   print fAcc.GetParName(n)+": "+str(fAcc.GetParameter(n))
   sfAcc = sfAcc.replace("["+str(n)+"]",str(fAcc.GetParameter(n)))
fAcc.SetLineColor(ROOT.kBlack)

### get the background model
fbkgfinal = TFile(indir+"finalbkg.root","READ")
fBkg = fbkgfinal.Get("bkgfit")
xmin = fBkg.GetXmin()
xmax = fBkg.GetXmax()
N = int(xmax-xmin) ## 1 GeV bins

htemp = TH1D("htemp_ee","",N,xmin,xmax)
htemp.SetLineColor(ROOT.kBlack)
htemp.SetMarkerColor(ROOT.kBlack)
htemp.SetMarkerStyle(20)
htemp.SetMinimum(1e-2)
fit = fBkg.Clone("fee")
hfit = htemp.Clone("hfit_ee")
hfit.Reset()
for i in xrange(1,hfit.GetNbinsX()+1):
   x = hfit.GetBinCenter(i)
   if(x<fit.GetXmin()): continue
   y = fit.Eval(x)
   hfit.SetBinContent(i,y)

#### get the signal model
hsig = TH1D("hsig_ee","",N,xmin,xmax)
hbkgsig = hfit.Clone("hbkgsig_ee")
k = str(500)
kR = str(10)
scale = str(12500)
Lmean = str(1*float(k))
Lsigma = str(0.2*float(Lmean))
sClockwork = "("+scale+"*TMath::Landau(x,"+Lmean+","+Lsigma+") * TMath::Exp(-x/"+k+") * (RESONANCES) )*("+sfAcc+")"
sResonances = ""  
for n in xrange(1,1000):
   M = float(k)*ROOT.TMath.Sqrt(1+n*n/(float(kR)*float(kR)))
   if(M>6000): break
   sM = str(M)
   sW = str(M*fRes.Eval(M))
   sn = str(n)
   frac = str((float(k)/M)*(float(k)/M))
   if(n==1): sResonances += "(1-"+frac+")*TMath::Gaus(x,"+sM+","+sW+",1)"
   else:     sResonances += "+(1-"+frac+")*TMath::Gaus(x,"+sM+","+sW+",1)"
sClockwork = sClockwork.replace("RESONANCES",sResonances)
fClockwork = TF1("fClockwork",sClockwork,xmin,xmax)
hsig.SetLineColor(ROOT.kGreen)
hsig.SetLineWidth(1)
hfitsig = hfit.Clone("hfitsig_ee")
for i in xrange(1,N+1):
   x = hsig.GetBinCenter(i)
   y  = fClockwork.Eval(x)
   hsig.SetBinContent(i,y)
   ndata = hbkgsig.GetBinContent(i)
   if(ndata>0):
      hbkgsig.SetBinContent(i,int(ndata+y))
      hfitsig_ee.AddBinContent(i,y)

difbkgsig = hbkgsig.Clone("ee_difbkgsig")
for b in xrange(1,difbkgsig.GetNbinsX()+1):
   x = difbkgsig.GetBinCenter(b)
   y = difbkgsig.GetBinContent(b)
   dy = difbkgsig.GetBinError(b)
   f = fit.Eval(x)
   df = ROOT.TMath.Sqrt(f)
   d = y-f
   dd = ROOT.TMath.Sqrt(dy*dy+df*df)
   if( difbkgsig.GetXaxis().GetBinUpEdge(b)<fit.GetXmin() ):
      difbkgsig.SetBinContent(b,0)
      difbkgsig.SetBinError(b,0)
   else:
      difbkgsig.SetBinContent(b,d)
      difbkgsig.SetBinError(b,0)
difbkgsig.SetMinimum(-250.)
difbkgsig.SetMaximum(+250.)
difbkgsig.SetMarkerSize(0.5)



############################################################
############################################################
############################################################



### https://stackoverflow.com/questions/19975030/amplitude-of-numpys-fft-results-is-to-be-multiplied-by-sampling-period
def GetFFT(category,type,channel,hDiff,x0,x1): ### only do the FFT above a mass threshold x0 to cut the low mass stat...
   mass = []
   diff = []
   for b in xrange(1,hDiff.GetNbinsX()+1):
      if(hDiff.GetBinCenter(b)<x0): continue
      if(hDiff.GetBinCenter(b)>x1): break
      mass.append(hDiff.GetBinCenter(b))
      diff.append(hDiff.GetBinContent(b))
   # create the x-axis
   N = len(mass)
   t = np.linspace(mass[0],mass[N-1],N)
   f = np.asarray(diff)
   # perform FT and multiply by dt
   dt = t[1]-t[0]
   ft = np.fft.fft(f) * dt      
   freq = np.fft.fftfreq(N, dt)
   freq = freq[:N/2+1]
   # get the magnitude
   mag = []
   freqmin = 0.0 # was 0.005
   freqmax = 0.1 # was 0.065 
   freqs = []
   for n in xrange(len(freq)-1):
      if(freq[n]<=freqmin): continue
      if(freq[n]>=freqmax): break
      freqs.append(freq[n])
      mag.append( np.abs(ft[:N/2+1])[n] )
   Nfreqs = len(freqs)
   dfreq = (freq[Nfreqs-1]-freq[0])/Nfreqs
   # fill the histogram
   hFFT = TH1D("fft_"+category+"_"+type,"FFT "+channel+";Frequency [1/GeV];Amplitude",Nfreqs,freqs[0]-dfreq,freqs[Nfreqs-1]+dfreq)
   for n in xrange(len(mag)-1):
      if(freqs[n]>freqmax): break
      hFFT.SetBinContent(n+1,mag[n])
   col = 0
   if("sigonly" in category): col = ROOT.kGreen
   if("sigbkg"  in category):  col = ROOT.kBlue
   if("bkgonly" in category): col = ROOT.kBlack
   hFFT.SetLineColor(col)
   hFFT.SetLineWidth(2)
   hFFT.SetMinimum(0)
   hFFT.SetMaximum(hFFT.GetMaximum()*1.5)
   return hFFT


def ToyDataFromTH1D(hist,bkgfithist,newname):
   print "making: ",newname
   x = RooRealVar("x","x",hist.GetXaxis().GetXmin(),hist.GetXaxis().GetXmax())
   x.setBins(hist.GetNbinsX())
   rooHist = RooDataHist("rooHist_"+newname,"rooHist",RooArgList(x),hist)
   histPdf = RooHistPdf("histPdf_"+newname,"histPdf",RooArgSet(x),rooHist)
   n = int(rooHist.sumEntries())
   print "Going to sample n=%g events" % (n)
   toy = histPdf.generate(RooArgSet(x),ROOT.RooFit.NumEvents(n),ROOT.RooFit.AutoBinned(ROOT.kFALSE))
   toy.Print()
   ### now dump the toy into the new hist:
   toyHist = hist.Clone("mass_"+newname)
   toyHist.Reset()
   entries = toy.numEntries()
   print "rooHist.sumEntries()=",rooHist.sumEntries()
   for i in xrange(entries):
      event = toy.get(i)
      var = event.find("x");
      val = var.getVal()
      toyHist.Fill(val)
   toyHist.SetMarkerStyle(20)
   toyHist.SetMarkerSize(1)
   toyHist.SetMarkerColor(ROOT.kBlack)
   difHist = toyHist.Clone("diff_"+newname)
   difHist.Add(bkgfithist,-1.)
   return toyHist, difHist


def GetToyStr(itoy):
   stoy = str(itoy)
   if(itoy<10):                   stoy = "0000"+stoy
   if(itoy>=10 and itoy<100):     stoy = "000"+stoy
   if(itoy>=100 and itoy<1000):   stoy = "00"+stoy
   if(itoy>=1000 and itoy<10000): stoy = "0"+stoy
   return stoy








########################################################################
########################################################################
########################################################################
### do the transformations
xmin = 225
xmax = 1533
xminfft = 700
Nbins = int(xmax-xmin)




### write out the fits and the signals
stoy = GetToyStr(itoy)
fOut = TFile(outdir+"clockwork"+sample+"_"+stoy+".root","RECREATE")
fOut.cd()
htemp.Write()
fit.Write()
hfit.Write()
hfitsig.Write()
hsig.Write()
hbkgsig.Write()
difbkgsig.Write()


### toy for the bkg-only
print "Starting bkg-only toy",stoy
fOut.cd()
hToyBkg, hToyBkgDif = ToyDataFromTH1D(hfit,hfit,channel+"_bkgonly_toy_"+stoy)
hFFT = GetFFT(channel+"_bkgonly","toy_"+stoy,channel,hToyBkgDif,xminfft,xmax)
hToyBkg.Write()
hToyBkgDif.Write()
hFFT.Write()
print "Done bkg-only toy",stoy
print ""

### toy for the signal+bkg
ToyBkgSig_wavlets=[]
ToyBkgSigDif_wavlets = [] 
print "Starting sig+bkg toy",stoy
fOut.cd()
hToyBkgSig, hToyBkgSigDif = ToyDataFromTH1D(hfitsig,hfit,channel+"_sigbkg_toy_"+stoy)
hFFT = GetFFT(channel+"_sigbkg","toy_"+stoy,channel,hToyBkgSigDif,xminfft,xmax)
hToyBkgSig.Write()
hToyBkgSigDif.Write()
hFFT.Write()
print "Done sig+bkg toy",stoy
print ""

### one "analytical" for the signal-only
hFFT = GetFFT(channel+"_sigonly","analytical",channel,hsig,xminfft,xmax)
hFFT.SetMinimum(0)
hFFT.SetMaximum(hFFT.GetMaximum()*1.5)
hFFT.Write()




####################################################################
####################################################################
####################################################################
print "#######################################################"
print "                     Wavlet Section                    "
print "#######################################################"
Nwidths = 1000
method = 'cmor1-1' # 'cmor1-1' # 'cgau4' # 'gaus7'
iscomplex = True
widths = np.arange(1, Nwidths)

bkg_wavelet = []
sig_wavelet = []
for i in xrange(1,hToyBkgSigDif.GetNbinsX()+1): sig_wavelet.append(hToyBkgSigDif.GetBinContent(i))
for i in xrange(1,hToyBkgDif.GetNbinsX()+1):    bkg_wavelet.append(hToyBkgDif.GetBinContent(i))
cwtmatr_Toy, freqs_Toy = pywt.cwt(sig_wavelet, widths, method)
cwtmatr_ToyBkg, freqs_ToyBkgDif = pywt.cwt(bkg_wavelet, widths, method)

fOut.cd()
n_freqs_ToyBkgDif = len(freqs_ToyBkgDif)
ToyBkg_histo = TH2D("ToyBkg_histo_"+stoy,";m_{ee} [GeV];Frequency [1/GeV];Amplitude",Nbins,xmin,xmax, 100,0,0.1)
ToyBkg_histo_real = TH2D("ToyBkg_histo_real_"+stoy,";m_{ee} [GeV];Frequency [1/GeV];Amplitude",Nbins,xmin,xmax, 100,0,0.1)
ToyBkg_histo_imag = TH2D("ToyBkg_histo_imag_"+stoy,";m_{ee} [GeV];Frequency [1/GeV];Amplitude",Nbins,xmin,xmax, 100,0,0.1)
ToyBkg_histo.SetLineColor(ROOT.kBlue)
ToyBkg_histo.SetMarkerColor(ROOT.kBlue)
ToyBkg_histo.SetFillColor(ROOT.kBlue)
ToyBkg_histo_real.SetLineColor(ROOT.kBlue)
ToyBkg_histo_real.SetMarkerColor(ROOT.kBlue)
ToyBkg_histo_real.SetFillColor(ROOT.kBlue)
ToyBkg_histo_imag.SetLineColor(ROOT.kBlue)
ToyBkg_histo_imag.SetMarkerColor(ROOT.kBlue)
ToyBkg_histo_imag.SetFillColor(ROOT.kBlue)
for i in xrange(n_freqs_ToyBkgDif):
   f = freqs_ToyBkgDif[i]
   by = ToyBkg_histo.GetYaxis().FindBin(f)
   for j in xrange(len(cwtmatr_ToyBkg[i])):
      bx = j+1
      z_real = cwtmatr_ToyBkg[i][j].real
      z_imag = cwtmatr_ToyBkg[i][j].imag
      z = abs(cwtmatr_ToyBkg[i][j])
      if(z>0.): ToyBkg_histo.SetBinContent(bx,by,z)
      if(z>0.): ToyBkg_histo_real.SetBinContent(bx,by,z_real)
      if(z>0.): ToyBkg_histo_imag.SetBinContent(bx,by,z_imag)
ToyBkg_histo_real.Write()
ToyBkg_histo_imag.Write()
ToyBkg_histo.Write()

fOut.cd()
n_freqs_Toy = len(freqs_Toy)
Toy_histo = TH2D("Toy_histo_"+stoy,";m_{ee} [GeV];Frequency [1/GeV];Amplitude",Nbins,xmin,xmax, 100,0,0.1)
Toy_histo_real = TH2D("Toy_histo_real_"+stoy,";m_{ee} [GeV];Frequency [1/GeV];Amplitude",Nbins,xmin,xmax, 100,0,0.1)
Toy_histo_imag = TH2D("Toy_histo_imag_"+stoy,";m_{ee} [GeV];Frequency [1/GeV];Amplitude",Nbins,xmin,xmax, 100,0,0.1)
Toy_histo.SetLineColor(ROOT.kBlue)
Toy_histo.SetMarkerColor(ROOT.kBlue)
Toy_histo.SetFillColor(ROOT.kBlue)
Toy_histo_real.SetLineColor(ROOT.kBlue)
Toy_histo_real.SetMarkerColor(ROOT.kBlue)
Toy_histo_real.SetFillColor(ROOT.kBlue)
Toy_histo_imag.SetLineColor(ROOT.kBlue)
Toy_histo_imag.SetMarkerColor(ROOT.kBlue)
Toy_histo_imag.SetFillColor(ROOT.kBlue)
for i in xrange(n_freqs_Toy):
   f = freqs_Toy[i]
   by = Toy_histo.GetYaxis().FindBin(f)
   for j in xrange(len(cwtmatr_Toy[i])):
      bx = j+1
      z = abs(cwtmatr_Toy[i][j])
      z_real = cwtmatr_Toy[i][j].real
      z_imag = cwtmatr_Toy[i][j].imag
      if(z>0.): Toy_histo.SetBinContent(bx,by,z)
      if(z>0.): Toy_histo_real.SetBinContent(bx,by,z_real if(iscomplex) else z)
      if(z>0.): Toy_histo_imag.SetBinContent(bx,by,z_imag if(iscomplex) else z)
Toy_histo.Write()
Toy_histo_real.Write()
Toy_histo_imag.Write()

fOut.Write()
fOut.Close()