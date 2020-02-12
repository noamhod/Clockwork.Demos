#!/usr/bin/env python
import os, sys
import math
import ROOT
from ROOT import *
import numpy as np
import array
from array import *
import pywt
import glob


## styles
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetPadLeftMargin(0.13)
ROOT.gStyle.SetPadRightMargin(0.13)

def Atlas(side):
   s = TLatex()
   s.SetNDC(1)
   s.SetTextAlign(13)
   s.SetTextColor(kBlack)
   s.SetTextSize(0.044)
   x = 0.49 if(side=="R") else 0.17
   s.DrawLatex(x,0.86,"#font[72]{ATLAS} Internal")
   s.DrawLatex(x,0.81,"#sqrt{s} = 13 TeV")

def GetToyStr(itoy):
   stoy = str(itoy)
   if(itoy<10):                   stoy = "0000"+stoy
   if(itoy>=10 and itoy<100):     stoy = "000"+stoy
   if(itoy>=100 and itoy<1000):   stoy = "00"+stoy
   if(itoy>=1000 and itoy<10000): stoy = "0"+stoy
   return stoy

def GetMean(histos,bin):
   mean = 0
   rms = 0
   for h in histos: mean += h.GetBinContent(bin)
   mean = mean/len(histos)
   return mean

def GetRMS(histos,bin,mean):
   rms = 0
   for h in histos:
      y = h.GetBinContent(bin)
      rms += (y-mean)*(y-mean)
   rms = ROOT.TMath.Sqrt(rms/len(histos))
   return rms

def GetEnv(histos,bin,quantile=95):
   y = []
   for h in histos: y.append( h.GetBinContent(bin) )
   arr = array("d",y)
   ymed = np.median(arr)
   ymin = np.min(arr)
   ymax = np.max(arr)
   ymaxX = np.percentile(arr,quantile)
   return ymed,ymin,ymax,ymaxX

def GetGraph(newname,histnominal,histmin,histmax):
   xbins = []
   ybins = []
   ymaxp = []
   yminn = []
   errx = []
   n = 0
   for b in xrange(1,histnominal.GetNbinsX()+1):
      x = histnominal.GetBinCenter(b)
      y = histnominal.GetBinContent(b)
      ymax = histmax.GetBinContent(b)
      ymin = histmin.GetBinContent(b)
      xbins.append(x)
      ybins.append(y)
      ymaxp.append(ymax-y)
      yminn.append(y-ymin)
      errx.append(histnominal.GetBinWidth(b)/2.)
      n += 1
   arrx  = array("d", xbins)
   arry  = array("d", ybins)
   arrup = array("d", ymaxp)
   arrdn = array("d", yminn)
   arrdx = array("d", errx)
   g = TGraphAsymmErrors(n,arrx,arry,arrdx,arrdx,arrdn,arrup)
   g.SetTitle(histnominal.GetTitle())
   g.GetXaxis().SetTitle(histnominal.GetXaxis().GetTitle())
   g.GetYaxis().SetTitle(histnominal.GetYaxis().GetTitle())
   g.SetLineColor(histnominal.GetLineColor())
   g.SetFillColor(histnominal.GetFillColor())
   g.SetMarkerColor(histnominal.GetMarkerColor())
   g.SetMarkerStyle(histnominal.GetMarkerStyle())
   g.SetName(histnominal.GetName()+"_graph_"+newname)
   return g


#################################################
#################################################
#################################################


indir = "/eos/user/h/hod/clockwork/"
toys = glob.glob(indir+"clockwork_*.root")
limit = 1
for toy in list(toys):
   size = os.path.getsize( toy )
   if(size<5000000): toys.remove(toy)

### slice?
# toys = toys[0:10]

Ntoys = len(toys)
print "Found %g good toy files" % Ntoys

def StripToy(ftoy):
   stoy = ftoy.replace(indir+"clockwork_","").replace(".root","")
   return stoy


bkgonly_toys_toy = []
bkgonly_toys_dif = []
bkgonly_toys_fft = []
n=0
for ftoy in toys:
   fIn = TFile(ftoy,"READ")
   stoy = StripToy(ftoy)
   name = "ee_bkgonly_toy_"+stoy
   h1 = fIn.Get("mass_"+name)
   h2 = fIn.Get("diff_"+name)
   h3 = fIn.Get("fft_"+name)
   bkgonly_toys_toy.append( h1.Clone("mass_"+name+"_clone") )
   bkgonly_toys_dif.append( h2.Clone("diff_"+name+"_clone") )
   bkgonly_toys_fft.append( h3.Clone("fft_"+name+"_clone") )
   bkgonly_toys_toy[n].SetDirectory(0)
   bkgonly_toys_dif[n].SetDirectory(0)
   bkgonly_toys_fft[n].SetDirectory(0)
   fIn.Close()
   n += 1

sigbkg_toys_toy = []
sigbkg_toys_dif = []
sigbkg_toys_fft = []
n=0
for ftoy in toys:
   fIn = TFile(ftoy,"READ")
   stoy = StripToy(ftoy)
   name = "ee_sigbkg_toy_"+stoy
   h1 = fIn.Get("mass_"+name)
   h2 = fIn.Get("diff_"+name)
   h3 = fIn.Get("fft_"+name)
   sigbkg_toys_toy.append(h1.Clone("mass_"+name+"_clone"))
   sigbkg_toys_dif.append(h2.Clone("diff_"+name+"_clone"))
   sigbkg_toys_fft.append(h3.Clone("fft_"+name+"_clone"))
   sigbkg_toys_toy[n].SetDirectory(0)
   sigbkg_toys_dif[n].SetDirectory(0)
   sigbkg_toys_fft[n].SetDirectory(0)
   fIn.Close()
   n += 1

name = "ee_sigonly_analytical"
fIn = TFile(toys[0],"READ")
h1 = fIn.Get("fft_"+name)
h1.SetDirectory(0)
sigonly_fft = h1.Clone("fft_"+name+"_clone")
sigonly_fft.SetDirectory(0)
fIn.Close()



####################################################
####################################################
####################################################

fIn = TFile(toys[0],"READ")
hsins = fIn.Get("hsig_ee")
hsins.SetDirectory(0)
hfits = fIn.Get("hfit_ee")
hfits.SetDirectory(0)
hfitsigs = fIn.Get("hfitsig_ee")
hfitsigs.SetDirectory(0)
fIn.Close()

####################################################
####################################################
####################################################


### Summarise the bands
bkgonly_toys_fft_mean = bkgonly_toys_fft[0].Clone( bkgonly_toys_fft[0].GetName()+"_mean" )
bkgonly_toys_fft_medi = bkgonly_toys_fft[0].Clone( bkgonly_toys_fft[0].GetName()+"_medi" )
bkgonly_toys_fft_ymax = bkgonly_toys_fft[0].Clone( bkgonly_toys_fft[0].GetName()+"_ymax" )
bkgonly_toys_fft_ymin = bkgonly_toys_fft[0].Clone( bkgonly_toys_fft[0].GetName()+"_ymin" )
bkgonly_toys_fft_ymaxX = bkgonly_toys_fft[0].Clone( bkgonly_toys_fft[0].GetName()+"_ymaxX" )
bkgonly_toys_fft_mean.Reset()
bkgonly_toys_fft_medi.Reset()
bkgonly_toys_fft_ymax.Reset()
bkgonly_toys_fft_ymin.Reset()
bkgonly_toys_fft_ymaxX.Reset()
for b in xrange(1,bkgonly_toys_fft_mean.GetNbinsX()+1):
   mean = GetMean(bkgonly_toys_fft,b)
   rms = GetRMS(bkgonly_toys_fft,b,mean)
   med,ymin,ymax,ymaxX = GetEnv(bkgonly_toys_fft,b)
   bkgonly_toys_fft_medi.SetBinContent(b,med)
   bkgonly_toys_fft_ymax.SetBinContent(b,ymax)
   bkgonly_toys_fft_ymin.SetBinContent(b,ymin)
   bkgonly_toys_fft_ymaxX.SetBinContent(b,ymaxX)
   bkgonly_toys_fft_mean.SetBinContent(b,mean)
   bkgonly_toys_fft_mean.SetBinError(b,rms)
bkgonly_toys_fft_mean.SetMarkerColor(ROOT.kBlack)
bkgonly_toys_fft_mean.SetLineColor(ROOT.kBlack)
bkgonly_toys_fft_mean.SetFillColorAlpha(ROOT.kBlack,0.6)
bkgonly_toys_fft_medi.SetMarkerColor(ROOT.kBlack)
bkgonly_toys_fft_medi.SetLineColor(ROOT.kBlack)
bkgonly_toys_fft_medi.SetFillColorAlpha(ROOT.kBlack,0.6)
bkgonly_toys_fft_ymax.SetMarkerColor(ROOT.kBlack)
bkgonly_toys_fft_ymax.SetLineColor(ROOT.kBlack)
bkgonly_toys_fft_ymax.SetFillColorAlpha(ROOT.kBlack,0.6)
bkgonly_toys_fft_ymin.SetMarkerColor(ROOT.kBlack)
bkgonly_toys_fft_ymin.SetLineColor(ROOT.kBlack)
bkgonly_toys_fft_ymin.SetFillColorAlpha(ROOT.kBlack,0.6)
bkgonly_toys_fft_ymaxX.SetMarkerColor(ROOT.kBlack)
bkgonly_toys_fft_ymaxX.SetLineColor(ROOT.kBlack)
bkgonly_toys_fft_ymaxX.SetFillColorAlpha(ROOT.kBlack,0.6)
bkgonly_fft_bands = {"mean":bkgonly_toys_fft_mean,"ymaxX":bkgonly_toys_fft_ymaxX,"ymax":bkgonly_toys_fft_ymax,"ymin":bkgonly_toys_fft_ymin,"median":bkgonly_toys_fft_medi}


### Summarise the bands
sigbkg_toys_fft_mean = sigbkg_toys_fft[0].Clone( sigbkg_toys_fft[0].GetName()+"_mean" )
sigbkg_toys_fft_medi = sigbkg_toys_fft[0].Clone( sigbkg_toys_fft[0].GetName()+"_medi" )
sigbkg_toys_fft_ymax = sigbkg_toys_fft[0].Clone( sigbkg_toys_fft[0].GetName()+"_ymax" )
sigbkg_toys_fft_ymin = sigbkg_toys_fft[0].Clone( sigbkg_toys_fft[0].GetName()+"_ymin" )
sigbkg_toys_fft_ymaxX = sigbkg_toys_fft[0].Clone( sigbkg_toys_fft[0].GetName()+"_ymaxX" )
sigbkg_toys_fft_mean.Reset()
sigbkg_toys_fft_medi.Reset()
sigbkg_toys_fft_ymax.Reset()
sigbkg_toys_fft_ymin.Reset()
sigbkg_toys_fft_ymaxX.Reset()
for b in xrange(1,sigbkg_toys_fft_mean.GetNbinsX()+1):
   mean = GetMean(sigbkg_toys_fft,b)
   rms = GetRMS(sigbkg_toys_fft,b,mean)
   med,ymin,ymax,ymaxX = GetEnv(sigbkg_toys_fft,b)
   sigbkg_toys_fft_medi.SetBinContent(b,med)
   sigbkg_toys_fft_ymax.SetBinContent(b,ymax)
   sigbkg_toys_fft_ymin.SetBinContent(b,ymin)
   sigbkg_toys_fft_ymaxX.SetBinContent(b,ymaxX)
   sigbkg_toys_fft_mean.SetBinContent(b,mean)
   sigbkg_toys_fft_mean.SetBinError(b,rms)
sigbkg_toys_fft_mean.SetLineColor(ROOT.kBlue)
sigbkg_toys_fft_mean.SetFillColorAlpha(ROOT.kBlue,0.6)
sigbkg_toys_fft_mean.SetMarkerColor(ROOT.kBlue)
sigbkg_toys_fft_medi.SetLineColor(ROOT.kBlue)
sigbkg_toys_fft_medi.SetFillColorAlpha(ROOT.kBlue,0.6)
sigbkg_toys_fft_medi.SetMarkerColor(ROOT.kBlue)
sigbkg_toys_fft_ymax.SetLineColor(ROOT.kBlue)
sigbkg_toys_fft_ymax.SetFillColorAlpha(ROOT.kBlue,0.6)
sigbkg_toys_fft_ymax.SetMarkerColor(ROOT.kBlue)
sigbkg_toys_fft_ymin.SetLineColor(ROOT.kBlue)
sigbkg_toys_fft_ymin.SetFillColorAlpha(ROOT.kBlue,0.6)
sigbkg_toys_fft_ymin.SetMarkerColor(ROOT.kBlue)
sigbkg_toys_fft_ymaxX.SetLineColor(ROOT.kBlue)
sigbkg_toys_fft_ymaxX.SetFillColorAlpha(ROOT.kBlue,0.6)
sigbkg_toys_fft_ymaxX.SetMarkerColor(ROOT.kBlue)
sigbkg_fft_bands = {"mean":sigbkg_toys_fft_mean,"ymaxX":sigbkg_toys_fft_ymaxX,"ymax":sigbkg_toys_fft_ymax,"ymin":sigbkg_toys_fft_ymin,"median":sigbkg_toys_fft_medi}



cnv = TCanvas("c","",1500,500)
cnv.Divide(3,1)
p1 = cnv.cd(1)
p2 = cnv.cd(2)
p3 = cnv.cd(3)

leg1 = TLegend(0.40,0.60,0.87,0.87)#,NULL,"brNDC")
leg1.SetFillStyle(4000) #will be transparent
leg1.SetFillColor(0)
leg1.SetTextFont(42)
leg1.SetBorderSize(0)
leg1.AddEntry(sigbkg_toys_toy[0],"Toy_{s+b}","ple")
leg1.AddEntry(hsins,    "Signal only","l")
leg1.AddEntry(hfits,    "Background fit","l")
leg1.AddEntry(hfitsigs, "Signal#plusBackground","l")

leg2 = TLegend(0.45,0.70,0.87,0.87)#,NULL,"brNDC")
leg2.SetFillStyle(4000) #will be transparent
leg2.SetFillColor(0)
leg2.SetTextFont(42)
leg2.SetBorderSize(0)
leg2.AddEntry(sigonly_fft,         "Signal only (analytic)","l")
leg2.AddEntry(sigbkg_fft_bands["mean"], "Signal+Background","F")
leg2.AddEntry(bkgonly_fft_bands["mean"],"Background only","F")

p1.cd()
p1.SetTicks(1,1)
p1.SetLogx()
p1.SetLogy()
sigbkg_toys_toy[0].SetTitle("One toy_{s+b} ee;m_{ee} [GeV];Events")
sigbkg_toys_toy[0].Draw()
hsins.Draw("same")
hfitsigs.SetLineColor(ROOT.kBlue)
hfitsigs.SetLineWidth(1)
hfitsigs.Draw("hist same")
hfits.SetLineColor(ROOT.kRed)
hfits.SetLineWidth(1)
hfits.Draw("hist same")
leg1.Draw("same")
p1.RedrawAxis()
p1.Update()

p2.cd()
p2.SetTicks(1,1)
p2.SetLogx()
sigbkg_toys_dif[0].SetTitle("One toy_{s+b}#minusFit_{b} ee;m_{ee} [GeV];Events-Fit")
sigbkg_toys_dif[0].SetLineWidth(1)
sigbkg_toys_dif[0].Draw("hist")
p2.RedrawAxis()
p2.Update()

p3.cd()
p3.SetTicks(1,1)
sigonly_fft.SetMaximum(250)
sigonly_fft.SetTitle( sigbkg_fft_bands["mean"].GetTitle()+" ("+str(Ntoys)+" toys);Frequency [1/GeV];|Amplitude|" )
sigonly_fft.Draw("C")
sigbkg_fft_bands["mean"].SetLineColor(sigbkg_fft_bands["mean"].GetFillColor())
sigbkg_fft_bands["mean"].SetFillColorAlpha(sigbkg_fft_bands["mean"].GetFillColor(), 0.60)
sigbkg_fft_bands["mean"].Draw("Ce5 same")
bkgonly_fft_bands["mean"].SetLineColor(bkgonly_fft_bands["mean"].GetFillColor())
bkgonly_fft_bands["mean"].SetFillColorAlpha(bkgonly_fft_bands["mean"].GetFillColor(), 0.60)
bkgonly_fft_bands["mean"].Draw("Ce5 same")
leg2.Draw("same")
p3.RedrawAxis()
p3.Update()

cnv.Update()
cnv.SaveAs("plot_clockwork_toys_band.pdf")
cnv.SaveAs("plot_clockwork_all.pdf(")




#######################################################
# Getting average wavelets
#######################################################
fIn = TFile(toys[0],"READ")
stoy0 = StripToy(toys[0])

Avg_ToyBkg_histo_real = fIn.Get("ToyBkg_histo_"+stoy0).Clone()
Avg_ToyBkg_histo_real.SetDirectory(0)
Avg_ToyBkg_histo_real.Reset()
Avg_Toy_histo_real = fIn.Get("Toy_histo_"+stoy0).Clone()
Avg_Toy_histo_real.SetDirectory(0)
Avg_Toy_histo_real.Reset()

Avg_ToyBkg_histo_imag = fIn.Get("ToyBkg_histo_"+stoy0).Clone()
Avg_ToyBkg_histo_imag.SetDirectory(0)
Avg_ToyBkg_histo_imag.Reset()
Avg_Toy_histo_imag = fIn.Get("Toy_histo_"+stoy0).Clone()
Avg_Toy_histo_imag.SetDirectory(0)
Avg_Toy_histo_imag.Reset()

Avg_ToyBkg_histo = fIn.Get("ToyBkg_histo_"+stoy0).Clone()
Avg_ToyBkg_histo.SetDirectory(0)
Avg_ToyBkg_histo.Reset()
Avg_Toy_histo = fIn.Get("Toy_histo_"+stoy0).Clone()
Avg_Toy_histo.SetDirectory(0)
Avg_Toy_histo.Reset()

RMS_ToyBkg_histo = fIn.Get("ToyBkg_histo_"+stoy0).Clone()
RMS_ToyBkg_histo.SetDirectory(0)
RMS_ToyBkg_histo.Reset()
RMS_Toy_histo = fIn.Get("Toy_histo_"+stoy0).Clone()
RMS_Toy_histo.SetDirectory(0)
RMS_Toy_histo.Reset()

fIn.Close()

### fill the 2d histograms
for ftoy in toys:
   fIn = TFile(ftoy,"READ")
   stoy = StripToy(ftoy)
   Toy_histo_real = fIn.Get("Toy_histo_real_"+stoy)
   Avg_Toy_histo_real.Add(Toy_histo_real)
   ToyBkg_histo_real = fIn.Get("ToyBkg_histo_real_"+stoy)
   Avg_ToyBkg_histo_real.Add(ToyBkg_histo_real)
   Toy_histo_imag = fIn.Get("Toy_histo_imag_"+stoy)
   Avg_Toy_histo_imag.Add(Toy_histo_imag)
   ToyBkg_histo_imag = fIn.Get("ToyBkg_histo_imag_"+stoy)
   Avg_ToyBkg_histo_imag.Add(ToyBkg_histo_imag)
   fIn.Close()
for bx in xrange(1,Avg_ToyBkg_histo.GetNbinsX()+1):
   for by in xrange(1,Avg_ToyBkg_histo.GetNbinsY()+1):
      zBkg_real = Avg_ToyBkg_histo_real.GetBinContent(bx,by)
      zBkgSig_real = Avg_Toy_histo_real.GetBinContent(bx,by)
      zBkg_imag = Avg_ToyBkg_histo_imag.GetBinContent(bx,by)
      zBkgSig_imag = Avg_Toy_histo_imag.GetBinContent(bx,by)
      zBkg = math.sqrt(zBkg_real*zBkg_real+zBkg_imag*zBkg_imag)
      zBkgSig = math.sqrt(zBkgSig_real*zBkgSig_real+zBkgSig_imag*zBkgSig_imag)
      if(zBkgSig!=0.): Avg_Toy_histo.SetBinContent(bx,by,zBkgSig)
      if(zBkg!=0.):    Avg_ToyBkg_histo.SetBinContent(bx,by,zBkg)
Avg_ToyBkg_histo.Scale(1./float(Ntoys))
Avg_Toy_histo.Scale(1./float(Ntoys))


### average of median quantiles for the background only
Avg_yquantlie = Avg_ToyBkg_histo.QuantilesY(0.67,"avg")
Avg_yquantlie.Reset()
for ftoy in toys:
   fIn = TFile(ftoy,"READ")
   stoy = StripToy(ftoy)
   ToyBkg_histo_real = fIn.Get("ToyBkg_histo_real_"+stoy)
   ToyBkg_histo_imag = fIn.Get("ToyBkg_histo_imag_"+stoy)
   ToyBkg_histo_abs = ToyBkg_histo_real.Clone()
   ToyBkg_histo_abs.Reset()
   for bx in xrange(1,ToyBkg_histo_abs.GetNbinsX()+1):
      for by in xrange(1,ToyBkg_histo_abs.GetNbinsY()+1):
         z_real = ToyBkg_histo_real.GetBinContent(bx,by)
         z_imag = ToyBkg_histo_imag.GetBinContent(bx,by)
         z_abs  = math.sqrt(z_real*z_real + z_imag*z_imag)
         ToyBkg_histo_abs.SetBinContent(bx,by,z_abs)
   yquantlie = ToyBkg_histo_abs.QuantilesY(0.67)
   Avg_yquantlie.Add(yquantlie)
   fIn.Close()
Avg_yquantlie.Scale(1./float(Ntoys))

### rms of median quantiles for the background only
RMS_yquantlie = Avg_ToyBkg_histo.QuantilesY(0.67,"rms")
RMS_yquantlie.Reset()
for ftoy in toys:
   fIn = TFile(ftoy,"READ")
   stoy = StripToy(ftoy)
   ToyBkg_histo_real = fIn.Get("ToyBkg_histo_real_"+stoy)
   ToyBkg_histo_imag = fIn.Get("ToyBkg_histo_imag_"+stoy)
   ToyBkg_histo_abs = ToyBkg_histo_real.Clone()
   ToyBkg_histo_abs.Reset()
   for bx in xrange(1,ToyBkg_histo_abs.GetNbinsX()+1):
      for by in xrange(1,ToyBkg_histo_abs.GetNbinsY()+1):
         z_real = ToyBkg_histo_real.GetBinContent(bx,by)
         z_imag = ToyBkg_histo_imag.GetBinContent(bx,by)
         z_abs  = math.sqrt(z_real*z_real + z_imag*z_imag)
         ToyBkg_histo_abs.SetBinContent(bx,by,z_abs)
   yquantlie = ToyBkg_histo_abs.QuantilesY(0.67)
   for bx in xrange(1,yquantlie.GetNbinsX()+1):
      av = Avg_yquantlie.GetBinContent(bx)
      y = yquantlie.GetBinContent(bx)
      rms = (av-y)*(av-y) + RMS_yquantlie.GetBinContent(bx)
      RMS_yquantlie.SetBinContent(bx,by,rms)
   fIn.Close()

RMS_yquantlie.Scale(1./float(Ntoys))
for bx in xrange(1,RMS_yquantlie.GetNbinsX()+1):
   rms = math.sqrt(RMS_yquantlie.GetBinContent(bx))
   RMS_yquantlie.SetBinContent(bx,rms)


### convert average quantiles to graph
xarr_freq_avg = []
yarr_freq_avg = []
for bx in xrange(1,Avg_yquantlie.GetNbinsX()+1):
   x = Avg_yquantlie.GetBinContent(bx)
   y = Avg_yquantlie.GetBinCenter(bx)
   if(x==0): continue
   xarr_freq_avg.append(x)
   yarr_freq_avg.append(y)
gQ_freq_avg = TGraph(len(xarr_freq_avg), array('d', xarr_freq_avg), array('d', yarr_freq_avg))
gQ_freq_avg.SetLineColor(ROOT.kBlack)
gQ_freq_avg.SetMarkerColor(ROOT.kBlack)
gQ_freq_avg.SetMarkerStyle(20)
gQ_freq_avg.SetMarkerSize(0.5)
### convert rms quantiles to graph
xarr_freq_rms = []
yarr_freq_rms = []
for bx in xrange(1,RMS_yquantlie.GetNbinsX()+1):
   x = RMS_yquantlie.GetBinContent(bx) + Avg_yquantlie.GetBinContent(bx) # !!!
   y = Avg_yquantlie.GetBinCenter(bx)
   if(x==0): continue
   xarr_freq_rms.append(x)
   yarr_freq_rms.append(y)
gQ_freq_rms = TGraph(len(xarr_freq_rms), array('d', xarr_freq_rms), array('d', yarr_freq_rms))
gQ_freq_rms.SetLineColor(ROOT.kGray)
gQ_freq_rms.SetMarkerColor(ROOT.kGray)
gQ_freq_rms.SetMarkerStyle(20)
gQ_freq_rms.SetMarkerSize(0.5)
### add them up on multigraph
mgQ = TMultiGraph()
mgQ.Add(gQ_freq_avg,"lp")
mgQ.Add(gQ_freq_rms,"lp")


#######################################################
## one signal toy example
fIn = TFile(toys[5],"READ")
stoy = StripToy(toys[5])
One_Toy_histo = fIn.Get("Toy_histo_"+stoy).Clone("onetoysig")
One_Toy_histo.SetDirectory(0)
fIn.Close()

## one background toy example
fIn = TFile(toys[5],"READ")
stoy = StripToy(toys[5])
One_BkgToy_histo = fIn.Get("ToyBkg_histo_"+stoy).Clone("onetoybkg")
One_BkgToy_histo.SetDirectory(0)
fIn.Close()
#######################################################


cnv = TCanvas("c","",1000,1000)
cnv.Divide(2,2)
p1 = cnv.cd(1)
p2 = cnv.cd(2)
p3 = cnv.cd(3)
p4 = cnv.cd(4)
p1.cd()
zmaxSig = Avg_Toy_histo.GetMaximum()
zmaxBkg = Avg_ToyBkg_histo.GetMaximum()
zmax = zmaxSig if(zmaxSig>zmaxBkg) else zmaxBkg
zmax = zmax*1.1
Avg_ToyBkg_histo.SetMaximum(zmax)
Avg_ToyBkg_histo.SetTitle("Background-only toys Average")
Avg_ToyBkg_histo.GetZaxis().SetTitle("|Amplitude|")
Avg_ToyBkg_histo.DrawNormalized("contz")
mgQ.Draw()
p2.cd()
Avg_Toy_histo.SetMaximum(zmax)
Avg_Toy_histo.SetTitle("Background+Signal toys Average")
Avg_Toy_histo.GetZaxis().SetTitle("|Amplitude|")
Avg_Toy_histo.DrawNormalized("contz")
mgQ.Draw()
cnv.Update()
p3.cd()
One_BkgToy_histo.SetMaximum(zmax)
One_BkgToy_histo.SetTitle("Background-only single toy")
One_BkgToy_histo.GetZaxis().SetTitle("|Amplitude|")
One_BkgToy_histo.DrawNormalized("contz")
mgQ.Draw()
p4.cd()
One_Toy_histo.SetMaximum(zmax)
One_Toy_histo.SetTitle("Background+Signal single toy")
One_Toy_histo.GetZaxis().SetTitle("|Amplitude|")
One_Toy_histo.DrawNormalized("contz")
mgQ.Draw()
cnv.Update()
cnv.SaveAs("plot_clockwork_contz_wavelets.pdf")
cnv.SaveAs("plot_clockwork_all.pdf")


cnv = TCanvas("c","",1000,1000)
cnv.Divide(2,2)
p1 = cnv.cd(1)
p2 = cnv.cd(2)
p3 = cnv.cd(3)
p4 = cnv.cd(4)
p1.cd()
Avg_ToyBkg_histo.SetTitle("Background-only toys Average")
Avg_ToyBkg_histo.GetZaxis().SetTitle("|Amplitude|")
Avg_ToyBkg_histo.DrawNormalized("cont4z")
mgQ.Draw()
p2.cd()
Avg_Toy_histo.SetTitle("Background+Signal toys Average")
Avg_Toy_histo.GetZaxis().SetTitle("|Amplitude|")
Avg_Toy_histo.DrawNormalized("cont4z")
mgQ.Draw()
cnv.Update()
p3.cd()
One_BkgToy_histo.SetTitle("Background-only single toy")
One_BkgToy_histo.GetZaxis().SetTitle("|Amplitude|")
One_BkgToy_histo.DrawNormalized("cont4z")
mgQ.Draw()
p4.cd()
One_Toy_histo.SetTitle("Background+Signal single toy")
One_Toy_histo.GetZaxis().SetTitle("|Amplitude|")
One_Toy_histo.DrawNormalized("cont4z")
mgQ.Draw()
cnv.Update()
cnv.SaveAs("plot_clockwork_cont4zNorm_wavelets.pdf")
cnv.SaveAs("plot_clockwork_all.pdf")


cnv = TCanvas("c","",1000,1000)
cnv.Divide(2,2)
p1 = cnv.cd(1)
p2 = cnv.cd(2)
p3 = cnv.cd(3)
p4 = cnv.cd(4)
p1.cd()
Avg_ToyBkg_histo.Draw("scat")
mgQ.Draw()
p2.cd()
Avg_Toy_histo.Draw("scat")
mgQ.Draw()
cnv.Update()
p3.cd()
One_BkgToy_histo.Draw("scat")
mgQ.Draw()
p4.cd()
One_Toy_histo.Draw("scat")
mgQ.Draw()
cnv.Update()
cnv.SaveAs("plot_clockwork_scat_wavelets.pdf")
cnv.SaveAs("plot_clockwork_all.pdf")


cnv = TCanvas("c","",1000,500)
cnv.Divide(2,1)
p1 = cnv.cd(1)
p2 = cnv.cd(2)
p1.cd()
pxClockworkX = Avg_Toy_histo.ProjectionX()
pxBackgroundX = Avg_ToyBkg_histo.ProjectionX()
pxClockworkX.SetLineColor(ROOT.kBlue)
pxClockworkX.SetFillColor(ROOT.kBlue)
pxBackgroundX.SetLineColor(ROOT.kBlack)
pxBackgroundX.SetFillColor(ROOT.kBlack)
pxClockworkX.SetTitle("Toys avg: projection on mass axis;Mass [GeV];|Amplitude|")
pxClockworkX.Draw("hist")
pxBackgroundX.Draw("hist same")
p2.cd()
pyClockworkY = Avg_Toy_histo.ProjectionY()
pyBackgroundY = Avg_ToyBkg_histo.ProjectionY()
pyClockworkY.SetLineColor(ROOT.kBlue)
pyClockworkY.SetFillColor(ROOT.kBlue)
pyBackgroundY.SetLineColor(ROOT.kBlack)
pyBackgroundY.SetFillColor(ROOT.kBlack)
pyClockworkY.SetTitle("Toys avg: projection on frequency axis;;|Amplitude|")
pyClockworkY.GetXaxis().SetTitle("Frequency [1/GeV]")
pyBackgroundY.GetXaxis().SetTitle("Frequency [1/GeV]")
pyClockworkY.GetXaxis().SetTitleOffset(1.0)
pyBackgroundY.GetXaxis().SetTitleOffset(1.0)
pyClockworkY.Draw("hist")
pyBackgroundY.Draw("hist same")
cnv.Update()
cnv.SaveAs("plot_clockwork_wavelets_projections.pdf")
cnv.SaveAs("plot_clockwork_all.pdf")


cnv = TCanvas("c","",1000,500)
cnv.Divide(2,1)
p1 = cnv.cd(1)
p2 = cnv.cd(2)
p1.cd()
pxClockworkOneToyX = One_Toy_histo.ProjectionX()
pxClockworkOneToyX.SetLineColor(ROOT.kBlue)
pxClockworkOneToyX.SetFillColor(ROOT.kBlue)
pxBackgroundOneToyX = One_BkgToy_histo.ProjectionX()
pxBackgroundOneToyX.SetLineColor(ROOT.kBlack)
pxBackgroundOneToyX.SetFillColor(ROOT.kBlack)
pxClockworkOneToyX.SetTitle("Single toy: projection on mass axis;Mass [GeV];|Amplitude|")
pxBackgroundOneToyX.SetTitle("Single toy: projection on mass axis;Mass [GeV];|Amplitude|")
pxBackgroundOneToyX.Draw("hist")
pxClockworkOneToyX.Draw("hist same")
p2.cd()
pxClockworkOneToyY = One_Toy_histo.ProjectionY()
pxClockworkOneToyY.SetLineColor(ROOT.kBlue)
pxClockworkOneToyY.SetFillColor(ROOT.kBlue)
pxBackgroundOneToyY = One_BkgToy_histo.ProjectionY()
pxBackgroundOneToyY.SetLineColor(ROOT.kBlack)
pxBackgroundOneToyY.SetFillColor(ROOT.kBlack)
pxClockworkOneToyY.SetTitle("Single toy: projection on frequency axis;Frequency [1/GeV];|Amplitude|")
pxBackgroundOneToyY.SetTitle("Single toy: projection on frequency axis;Frequency [1/GeV];|Amplitude|")
pxBackgroundOneToyY.Draw("hist")
pxClockworkOneToyY.Draw("hist same")
cnv.Update()
cnv.SaveAs("plot_clockwork_wavelets_onetoy_projections.pdf")
cnv.SaveAs("plot_clockwork_all.pdf)")