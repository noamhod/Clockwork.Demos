#!/usr/bin/env python
import os, sys
import math
import ROOT
from ROOT import *
import numpy as np
import array
from array import *
import pywt

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


fIn = TFile("clockwork_toys.root","READ")


def GetNtoys(f,pattern):
   total = 0
   hnames = []
   for key in f.GetListOfKeys():
      cl = ROOT.gROOT.GetClass(key.GetClassName())
      if(cl.InheritsFrom("TH1")):
         h = key.ReadObj()
         hname = h.GetName()
         if(pattern not in hname): continue
         if(hname not in hnames):
            hnames.append( hname )
            total += 1
   print "Found "+str(total)+" Histograms with pattern: "+pattern
   return  total


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

Ntoys = GetNtoys(fIn,"mass_ee_sigbkg_toy_")


bkgonly_toys_toy = {}
bkgonly_toys_dif = {}
bkgonly_toys_fft = {}
for channel in ["ee"]:
   bkgonly_toys_toy.update({channel:[]})
   bkgonly_toys_dif.update({channel:[]})
   bkgonly_toys_fft.update({channel:[]})
   for itoy in xrange(Ntoys):
      stoy = GetToyStr(itoy)
      name = channel+"_bkgonly_toy_"+stoy
      bkgonly_toys_toy[channel].append(fIn.Get("mass_"+name).Clone("mass_"+name))
      bkgonly_toys_dif[channel].append(fIn.Get("diff_"+name).Clone("diff_"+name))
      bkgonly_toys_fft[channel].append(fIn.Get("fft_"+name).Clone("fft_"+name))

      

sigbkg_toys_toy = {}
sigbkg_toys_dif = {}
sigbkg_toys_fft = {}
for channel in ["ee"]:
   sigbkg_toys_toy.update({channel:[]})
   sigbkg_toys_dif.update({channel:[]})
   sigbkg_toys_fft.update({channel:[]})
   for itoy in xrange(Ntoys):
      stoy = GetToyStr(itoy)
      name = channel+"_sigbkg_toy_"+stoy
      sigbkg_toys_toy[channel].append(fIn.Get("mass_"+name).Clone("mass_"+name))
      sigbkg_toys_dif[channel].append(fIn.Get("diff_"+name).Clone("diff_"+name))
      sigbkg_toys_fft[channel].append(fIn.Get("fft_"+name).Clone("fft_"+name))


sigonly_fft = {}
for channel in ["ee"]:
   name = channel+"_sigonly_analytical"
   sigonly_fft.update({channel:fIn.Get("fft_"+name).Clone("fft_"+name)})



####################################################
####################################################
####################################################

fIn1 = TFile("clockwork.root","READ")
hsins = {}
hfits = {}
hfitsigs = {}
hsins["ee"] = fIn1.Get("hsig_ee")
hfits["ee"] = fIn1.Get("hfit_ee")
hfitsigs["ee"] = fIn1.Get("hfitsig_ee")

####################################################
####################################################
####################################################



### Summarise the bands
bkgonly_fft_bands = {}
for channel in ["ee"]:
   bkgonly_toys_fft_mean = bkgonly_toys_fft[channel][0].Clone( bkgonly_toys_fft[channel][0].GetName()+"_mean" )
   bkgonly_toys_fft_medi = bkgonly_toys_fft[channel][0].Clone( bkgonly_toys_fft[channel][0].GetName()+"_medi" )
   bkgonly_toys_fft_ymax = bkgonly_toys_fft[channel][0].Clone( bkgonly_toys_fft[channel][0].GetName()+"_ymax" )
   bkgonly_toys_fft_ymin = bkgonly_toys_fft[channel][0].Clone( bkgonly_toys_fft[channel][0].GetName()+"_ymin" )
   bkgonly_toys_fft_ymaxX = bkgonly_toys_fft[channel][0].Clone( bkgonly_toys_fft[channel][0].GetName()+"_ymaxX" )
   bkgonly_toys_fft_mean.Reset()
   bkgonly_toys_fft_medi.Reset()
   bkgonly_toys_fft_ymax.Reset()
   bkgonly_toys_fft_ymin.Reset()
   bkgonly_toys_fft_ymaxX.Reset()
   for b in xrange(1,bkgonly_toys_fft_mean.GetNbinsX()+1):
      mean = GetMean(bkgonly_toys_fft[channel],b)
      rms = GetRMS(bkgonly_toys_fft[channel],b,mean)
      med,ymin,ymax,ymaxX = GetEnv(bkgonly_toys_fft[channel],b)
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
   bkgonly_fft_bands.update({channel:{"mean":bkgonly_toys_fft_mean,"ymaxX":bkgonly_toys_fft_ymaxX,"ymax":bkgonly_toys_fft_ymax,"ymin":bkgonly_toys_fft_ymin,"median":bkgonly_toys_fft_medi}})


### Summarise the bands
sigbkg_fft_bands = {}
for channel in ["ee"]:
   sigbkg_toys_fft_mean = sigbkg_toys_fft[channel][0].Clone( sigbkg_toys_fft[channel][0].GetName()+"_mean" )
   sigbkg_toys_fft_medi = sigbkg_toys_fft[channel][0].Clone( sigbkg_toys_fft[channel][0].GetName()+"_medi" )
   sigbkg_toys_fft_ymax = sigbkg_toys_fft[channel][0].Clone( sigbkg_toys_fft[channel][0].GetName()+"_ymax" )
   sigbkg_toys_fft_ymin = sigbkg_toys_fft[channel][0].Clone( sigbkg_toys_fft[channel][0].GetName()+"_ymin" )
   sigbkg_toys_fft_ymaxX = sigbkg_toys_fft[channel][0].Clone( sigbkg_toys_fft[channel][0].GetName()+"_ymaxX" )
   sigbkg_toys_fft_mean.Reset()
   sigbkg_toys_fft_medi.Reset()
   sigbkg_toys_fft_ymax.Reset()
   sigbkg_toys_fft_ymin.Reset()
   sigbkg_toys_fft_ymaxX.Reset()
   for b in xrange(1,sigbkg_toys_fft_mean.GetNbinsX()+1):
      mean = GetMean(sigbkg_toys_fft[channel],b)
      rms = GetRMS(sigbkg_toys_fft[channel],b,mean)
      med,ymin,ymax,ymaxX = GetEnv(sigbkg_toys_fft[channel],b)
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
   sigbkg_fft_bands.update({channel:{"mean":sigbkg_toys_fft_mean,"ymaxX":sigbkg_toys_fft_ymaxX,"ymax":sigbkg_toys_fft_ymax,"ymin":sigbkg_toys_fft_ymin,"median":sigbkg_toys_fft_medi}})




####################################################
####################################################
####################################################




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
leg1.AddEntry(sigbkg_toys_toy["ee"][0],"Toy_{s+b}","ple")
leg1.AddEntry(hsins["ee"],    "Signal only","l")
leg1.AddEntry(hfits["ee"],    "Background fit","l")
leg1.AddEntry(hfitsigs["ee"], "Signal#plusBackground","l")

leg2 = TLegend(0.45,0.70,0.87,0.87)#,NULL,"brNDC")
leg2.SetFillStyle(4000) #will be transparent
leg2.SetFillColor(0)
leg2.SetTextFont(42)
leg2.SetBorderSize(0)
leg2.AddEntry(sigonly_fft["ee"],         "Signal only (analytic)","l")
leg2.AddEntry(sigbkg_fft_bands["ee"]["mean"], "Signal+Background","F")
leg2.AddEntry(bkgonly_fft_bands["ee"]["mean"],"Background only","F")

p1.cd()
p1.SetTicks(1,1)
p1.SetLogx()
p1.SetLogy()
sigbkg_toys_toy["ee"][0].SetTitle("One toy_{s+b} ee;m_{ee} [GeV];Events")
sigbkg_toys_toy["ee"][0].Draw()
hsins["ee"].Draw("same")
hfitsigs["ee"].SetLineColor(ROOT.kBlue)
hfitsigs["ee"].SetLineWidth(1)
hfitsigs["ee"].Draw("hist same")
hfits["ee"].SetLineColor(ROOT.kRed)
hfits["ee"].SetLineWidth(1)
hfits["ee"].Draw("hist same")
leg1.Draw("same")
p1.RedrawAxis()
p1.Update()

p2.cd()
p2.SetTicks(1,1)
p2.SetLogx()
sigbkg_toys_dif["ee"][0].SetTitle("One toy_{s+b}#minusFit_{b} ee;m_{ee} [GeV];Events-Fit")
sigbkg_toys_dif["ee"][0].SetLineWidth(1)
sigbkg_toys_dif["ee"][0].Draw("hist")
p2.RedrawAxis()
p2.Update()

p3.cd()
p3.SetTicks(1,1)
sigonly_fft["ee"].SetMaximum(200)
sigonly_fft["ee"].SetTitle( sigbkg_fft_bands["ee"]["mean"].GetTitle()+" ("+str(Ntoys)+" toys);Frequency [1/GeV];|Amplitude|" )
sigonly_fft["ee"].Draw("C")
sigbkg_fft_bands["ee"]["mean"].SetLineColor(sigbkg_fft_bands["ee"]["mean"].GetFillColor())
sigbkg_fft_bands["ee"]["mean"].SetFillColorAlpha(sigbkg_fft_bands["ee"]["mean"].GetFillColor(), 0.60)
sigbkg_fft_bands["ee"]["mean"].Draw("Ce5 same")
bkgonly_fft_bands["ee"]["mean"].SetLineColor(bkgonly_fft_bands["ee"]["mean"].GetFillColor())
bkgonly_fft_bands["ee"]["mean"].SetFillColorAlpha(bkgonly_fft_bands["ee"]["mean"].GetFillColor(), 0.60)
bkgonly_fft_bands["ee"]["mean"].Draw("Ce5 same")
leg2.Draw("same")
p3.RedrawAxis()
p3.Update()

cnv.Update()
cnv.SaveAs("plot_clockwork_toys_band.pdf")




#######################################################
# Getting average
#######################################################
fToyscwt = TFile("clockwork_toys_cwt.root","READ")

Avg_ToyBkg_histo_real = fToyscwt.Get("ToyBkg_histo_1").Clone()
Avg_ToyBkg_histo_real.Reset()
Avg_Toy_histo_real = fToyscwt.Get("Toy_histo_1").Clone()
Avg_Toy_histo_real.Reset()

Avg_ToyBkg_histo_imag = fToyscwt.Get("ToyBkg_histo_1").Clone()
Avg_ToyBkg_histo_imag.Reset()
Avg_Toy_histo_imag = fToyscwt.Get("Toy_histo_1").Clone()
Avg_Toy_histo_imag.Reset()

Avg_ToyBkg_histo = fToyscwt.Get("ToyBkg_histo_1").Clone()
Avg_ToyBkg_histo.Reset()
Avg_Toy_histo = fToyscwt.Get("Toy_histo_1").Clone()
Avg_Toy_histo.Reset()

for itoy in range(Ntoys):
   Toy_histo_real = fToyscwt.Get("Toy_histo_real_"+str(itoy+1))
   Avg_Toy_histo_real.Add(Toy_histo_real)
   ToyBkg_histo_real = fToyscwt.Get("ToyBkg_histo_real_"+str(itoy+1))
   Avg_ToyBkg_histo_real.Add(ToyBkg_histo_real)
   Toy_histo_imag = fToyscwt.Get("Toy_histo_imag_"+str(itoy+1))
   Avg_Toy_histo_imag.Add(Toy_histo_imag)
   ToyBkg_histo_imag = fToyscwt.Get("ToyBkg_histo_imag_"+str(itoy+1))
   Avg_ToyBkg_histo_imag.Add(ToyBkg_histo_imag)

for bx in xrange(1,Avg_ToyBkg_histo.GetNbinsX()+1):
   for by in xrange(1,Avg_ToyBkg_histo.GetNbinsY()+1):
      zBkg_real = Avg_ToyBkg_histo_real.GetBinContent(bx,by)
      zBkgSig_real = Avg_Toy_histo_real.GetBinContent(bx,by)
      zBkg_imag = Avg_ToyBkg_histo_imag.GetBinContent(bx,by)
      zBkgSig_imag = Avg_Toy_histo_imag.GetBinContent(bx,by)
      zBkg = math.sqrt(zBkg_real*zBkg_real+zBkg_imag*zBkg_imag)
      zBkgSig = math.sqrt(zBkgSig_real*zBkgSig_real+zBkgSig_imag*zBkgSig_imag)
      if(zBkg!=0.):    Avg_ToyBkg_histo.SetBinContent(bx,by,zBkg/float(Ntoys))
      if(zBkgSig!=0.): Avg_Toy_histo.SetBinContent(bx,by,zBkgSig/float(Ntoys))



#######################################################
## one signal toy example
One_Toy_histo_real = fToyscwt.Get("Toy_histo_real_5").Clone()
One_Toy_histo_imag = fToyscwt.Get("Toy_histo_imag_5").Clone()
One_Toy_histo = fToyscwt.Get("Toy_histo_5").Clone()
One_Toy_histo.Reset()
for bx in xrange(1,One_Toy_histo.GetNbinsX()+1):
   for by in xrange(1,One_Toy_histo.GetNbinsY()+1):
      zBkgSig_real = One_Toy_histo_real.GetBinContent(bx,by)
      zBkgSig_imag = One_Toy_histo_imag.GetBinContent(bx,by)
      zBkgSig = math.sqrt(zBkgSig_real*zBkgSig_real+zBkgSig_imag*zBkgSig_imag)
      if(zBkgSig!=0.): One_Toy_histo.SetBinContent(bx,by,zBkgSig)


cnv = TCanvas("c","",1500,500)
cnv.Divide(3,1)
p1 = cnv.cd(1)
p2 = cnv.cd(2)
p3 = cnv.cd(3)
p1.cd()
zmax = Avg_Toy_histo.GetMaximum()*1.1
Avg_ToyBkg_histo.SetMaximum(zmax)
Avg_ToyBkg_histo.SetTitle("Background-only toys Average")
Avg_ToyBkg_histo.GetZaxis().SetTitle("|Amplitude|")
Avg_ToyBkg_histo.Draw("contz")
p2.cd()
One_Toy_histo.SetMaximum(zmax)
One_Toy_histo.SetTitle("Background+Signal single toy")
One_Toy_histo.GetZaxis().SetTitle("|Amplitude|")
One_Toy_histo.Draw("contz")
p3.cd()
Avg_Toy_histo.SetMaximum(zmax)
Avg_Toy_histo.SetTitle("Background+Signal toys Average")
Avg_Toy_histo.GetZaxis().SetTitle("|Amplitude|")
Avg_Toy_histo.Draw("contz")
cnv.Update()
cnv.SaveAs("plot_clockwork_wavelets.pdf")

cnv = TCanvas("c","",1000,500)
cnv.Divide(2,1)
p1 = cnv.cd(1)
p2 = cnv.cd(2)
p1.cd()
pyClockwork = Avg_Toy_histo.ProjectionX()
pyBackground = Avg_ToyBkg_histo.ProjectionX()
pyClockwork1 = One_Toy_histo.ProjectionX()
pyClockwork1.SetLineColor(ROOT.kRed)
pyClockwork.SetLineColor(ROOT.kBlue)
pyBackground.SetLineColor(ROOT.kBlack)
pyBackground.SetFillColor(ROOT.kBlack)
pyClockwork.SetTitle("Toys avg: projection on mass axis;Mass [GeV];|Amplitude|")
pyClockwork.Draw("hist")
pyBackground.Draw("hist same")
pyClockwork1.Draw("hist same")
p2.cd()
pyClockwork = Avg_Toy_histo.ProjectionY()
pyBackground = Avg_ToyBkg_histo.ProjectionY()
pyClockwork1 = One_Toy_histo.ProjectionY()
pyClockwork1.SetLineColor(ROOT.kRed)
pyClockwork.SetLineColor(ROOT.kBlue)
pyBackground.SetLineColor(ROOT.kBlack)
pyBackground.SetFillColor(ROOT.kBlack)
pyClockwork.SetTitle("Toys avg: projection on frequency axis;;|Amplitude|")
pyClockwork.GetXaxis().SetTitle("Frequency [1/GeV]")
pyBackground.GetXaxis().SetTitle("Frequency [1/GeV]")
pyClockwork.GetXaxis().SetTitleOffset(1.0)
pyClockwork1.GetXaxis().SetTitleOffset(1.0)
pyBackground.GetXaxis().SetTitleOffset(1.0)
pyClockwork.Draw("hist")
pyBackground.Draw("hist same")
pyClockwork1.Draw("hist same")
cnv.Update()
cnv.SaveAs("plot_clockwork_wavelets_projections.pdf")