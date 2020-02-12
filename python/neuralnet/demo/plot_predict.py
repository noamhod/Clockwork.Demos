#!/usr/bin/env python
import os, sys
import subprocess
import ROOT
from ROOT import *
import glob
from array import array
import argparse
parser = argparse.ArgumentParser(description='plot...')
parser.add_argument('-d', metavar='drawopt', required=True,  help='drawopt [scat/cont4/mpltlib]')
argus = parser.parse_args()
drawopt = argus.d

## styles
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetPadLeftMargin(0.13)
# ROOT.gStyle.SetPadRightMargin(0.13)

def quantile(h,title):
   nq = h.GetNbinsX()
   xq = array('d',[0.]*nq) # position where to compute the quantiles in [0,1]
   yq = array('d',[0.]*nq) # array to contain the quantiles
   for i in xrange(nq): xq[i] = float(i+1)/nq
   h.GetQuantiles(nq,yq,xq)
   g = TGraph(nq,xq,yq)
   g.SetTitle(title)
   g.SetMinimum(0)
   g.SetMaximum(1.1)
   g.SetLineColor(h.GetLineColor())
   g.SetLineWidth(2)
   return g


fbkg = TFile("predictions_"+drawopt+"_bkg_"+drawopt+".root", "READ")
fsig = TFile("predictions_"+drawopt+"_sig_"+drawopt+".root", "READ")

hbkg_bkg = fbkg.Get("hpredict_bkg_"+drawopt+"_bkg_"+drawopt+"")
hbkg_sig = fbkg.Get("hpredict_sig_"+drawopt+"_bkg_"+drawopt+"")

hsig_bkg = fsig.Get("hpredict_bkg_"+drawopt+"_sig_"+drawopt+"")
hsig_sig = fsig.Get("hpredict_sig_"+drawopt+"_sig_"+drawopt+"")

hbkg_bkg.Rebin(20)
hbkg_sig.Rebin(20)
hsig_bkg.Rebin(20)
hsig_sig.Rebin(20)

hbkg_bkg.SetMinimum(0.5)
hbkg_sig.SetMinimum(0.5)
hsig_bkg.SetMinimum(0.5)
hsig_sig.SetMinimum(0.5)

hbkg_bkg.SetLineColor(ROOT.kBlack)
hbkg_sig.SetLineColor(ROOT.kRed)
hsig_bkg.SetLineColor(ROOT.kBlack)
hsig_sig.SetLineColor(ROOT.kRed)

hbkg_bkg.SetTitle("Background toys")
hbkg_sig.SetTitle("Background toys")
hsig_bkg.SetTitle("Signal toys")
hsig_sig.SetTitle("Signal toys")

gbkg_bkg = quantile(hbkg_bkg,";Quantile;Probability").Clone("gbkg_bkg")
gbkg_sig = quantile(hbkg_sig,";Quantile;Probability").Clone("gbkg_sig")
gsig_bkg = quantile(hsig_bkg,";Quantile;Probability").Clone("gsig_bkg")
gsig_sig = quantile(hsig_sig,";Quantile;Probability").Clone("gsig_sig")

mgbkg = TMultiGraph()
mgbkg.Add(gbkg_bkg,"l")
mgbkg.Add(gbkg_sig,"l")
mgbkg.SetTitle(";Quantile;Probability")

mgsig = TMultiGraph()
mgsig.Add(gsig_bkg,"l")
mgsig.Add(gsig_sig,"l")
mgsig.SetTitle(";Quantile;Probability")


legp = TLegend(0.4,0.70,0.80,0.85)
legp.SetFillStyle(4000) # will be transparent
legp.SetFillColor(0)
legp.SetTextFont(42)
legp.SetBorderSize(0)
legp.AddEntry(hbkg_bkg, "P(bkg)","f");
legp.AddEntry(hbkg_sig, "P(sig)","f");


legq = TLegend(0.4,0.60,0.80,0.75)
legq.SetFillStyle(4000) # will be transparent
legq.SetFillColor(0)
legq.SetTextFont(42)
legq.SetBorderSize(0)
legq.AddEntry(gbkg_bkg, "Q(bkg)","l");
legq.AddEntry(gbkg_sig, "Q(sig)","l");


cnv = TCanvas("c","",1000,1000)
cnv.Divide(2,2)
p1 = cnv.cd(1)
p2 = cnv.cd(2)
p3 = cnv.cd(3)
p4 = cnv.cd(4)

p1.cd()
p1.SetLogy()
p1.SetTicks(1,1)
hbkg_bkg.Draw("hist")
hbkg_sig.Draw("hist same")
legp.Draw("same")
p1.RedrawAxis()
p1.Update()

p2.cd()
p2.SetLogy()
p2.SetTicks(1,1)
hsig_sig.Draw("hist")
hsig_bkg.Draw("hist same")
legp.Draw("same")
p2.RedrawAxis()
p2.Update()

p3.cd()
p3.SetTicks(1,1)
p3.SetGrid()
# gbkg_bkg.Draw("alp")
mgbkg.Draw("a")
legq.Draw("same")
p3.RedrawAxis()
p3.Update()

p4.cd()
p4.SetTicks(1,1)
p4.SetGrid()
# gsig_bkg.Draw("alp")
mgsig.Draw("a")
legq.Draw("same")
p4.RedrawAxis()
p4.Update()

cnv.Update()
cnv.SaveAs("predictions_"+drawopt+".pdf")