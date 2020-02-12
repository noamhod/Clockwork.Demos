#!/usr/bin/env python
import os, sys
import math
import ROOT
from ROOT import *
import numpy as np

## styles
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetPadLeftMargin(0.13)


def Atlas(side):
   s = TLatex()
   s.SetNDC(1)
   s.SetTextAlign(13)
   s.SetTextColor(kBlack)
   s.SetTextSize(0.044)
   x = 0.49 if(side=="R") else 0.17
   s.DrawLatex(x,0.86,"#font[72]{ATLAS} Internal")
   s.DrawLatex(x,0.81,"#sqrt{s} = 13 TeV")


fPeterRes_ee = TFile("ee_relResolFunction.root","READ")
fRes_ee = fPeterRes_ee.Get("relResol_dedicatedTF")
fPeterAcc_ee = TFile("ee_accEffFunction.root","READ")
fAcc_ee = fPeterAcc_ee.Get("accEff_TF1")

# fPeterRes_uu = TFile("mm_relResolFunction.root","READ")
# fRes_uu = fPeterRes_uu.Get("relResol_dedicatedTF")
# fPeterAcc_uu = TFile("mm_accEffFunction.root","READ")
# fAcc_uu = fPeterAcc_uu.Get("accEff_TF1")


### resolution ee 
sfRes_ee = "sqrt(pow(([0]+[1]/x+[2]/pow(x,2)+[3]*x+[4]*pow(x,2))*sqrt(pow([5],2)+pow([6]/sqrt(x),2)+pow([7]/x,2)),2)+pow((1.0-([0]+[1]/x+[2]/pow(x,2)+[3]*x+[4]*pow(x,2)))*sqrt(pow([8],2)+pow([9]/sqrt(x),2)+pow([10]/x,2)),2))"
for n in xrange(0,fRes_ee.GetNpar()):
   print fRes_ee.GetParName(n)+": "+str(fRes_ee.GetParameter(n))
   sfRes_ee = sfRes_ee.replace("["+str(n)+"]",str(fRes_ee.GetParameter(n)))
print sfRes_ee
fRes_ee.SetLineColor(ROOT.kRed)
fRes_ee.SetTitle("Resolution and Acceptance#timesEfficiency;Truth m_{ll} [GeV];#sigma/m_{ll}, #it{A}#times#epsilon")

### acceptance*efficiency ee
sfAcc_ee = "[0]+[1]/x+[2]/pow(x,2)+[3]/pow(x,3)+[4]/pow(x,4)+[5]/pow(x,5)+[6]*x+[7]*pow(x,2)"
for n in xrange(0,fAcc_ee.GetNpar()):
   print fAcc_ee.GetParName(n)+": "+str(fAcc_ee.GetParameter(n))
   sfAcc_ee = sfAcc_ee.replace("["+str(n)+"]",str(fAcc_ee.GetParameter(n)))
print sfAcc_ee
fAcc_ee.SetLineColor(ROOT.kBlack)
fAcc_ee.SetTitle("Resolution and Acceptance#timesEfficiency;Truth m_{ll} [GeV];#sigma/m_{ll}, #it{A}#times#epsilon")

# ### resolution uu
# sfRes_uu = "sqrt(pow(([0]+[1]/x+[2]/pow(x,2)+[3]*x+[4]*pow(x,2))*([5]+[6]/x+[7]/pow(x,2)+[8]*x+[9]*pow(x,2)),2)+pow((1.0-([0]+[1]/x+[2]/pow(x,2)+[3]*x+[4]*pow(x,2)))*([10]+[11]/x+[12]/pow(x,2)+[13]*x+[14]*pow(x,2)),2))"
# for n in xrange(0,fRes_uu.GetNpar()):
#    print fRes_uu.GetParName(n)+": "+str(fRes_uu.GetParameter(n))
#    sfRes_uu = sfRes_uu.replace("["+str(n)+"]",str(fRes_uu.GetParameter(n)))
# print sfRes_uu
# fRes_uu.SetLineColor(ROOT.kRed)
# fRes_uu.SetTitle("Resolution and Acceptance#timesEfficiency;Truth m_{ll} [GeV];#sigma/m_{ll}, #it{A}#times#epsilon")
# 
# ### acceptance*efficiency uu
# sfAcc_uu = "[0]+[1]/x+[2]/pow(x,2)+[3]/pow(x,3)+[4]/pow(x,4)+[5]/pow(x,5)+[6]*x+[7]*pow(x,2)"
# for n in xrange(0,fAcc_uu.GetNpar()):
#    print fAcc_uu.GetParName(n)+": "+str(fAcc_uu.GetParameter(n))
#    sfAcc_uu = sfAcc_uu.replace("["+str(n)+"]",str(fAcc_uu.GetParameter(n)))
# print sfAcc_uu
# fAcc_uu.SetLineColor(ROOT.kBlack)
# fAcc_uu.SetTitle("Resolution and Acceptance#timesEfficiency;Truth m_{ll} [GeV];#sigma/m_{ll}, #it{A}#times#epsilon")



### the background model ee 
sBkg_ee = "(1-x/13000.)^61.5323189255*exp( 1.944274138*log(x) + -0.219250447331*log(x)^2 + 663.923934036/log(x)^3 )"
fBkg_ee = TF1("fBkg_ee",sBkg_ee,130,fRes_ee.GetXmax())
fBkg_ee.SetLineColor(ROOT.kRed)
fBkg_ee.SetLineWidth(1)
fBkg_ee.SetMinimum(1.e-3)

# ### the background model uu 
# sBkg_uu = "(1-x/13000.)^74.0621722661*exp( 0.125635957377*log(x) + 222.902387716/log(x)^2 )"
# fBkg_uu = TF1("fBkg_uu",sBkg_uu,130,fRes_uu.GetXmax())
# fBkg_uu.SetLineColor(ROOT.kRed)
# fBkg_uu.SetLineWidth(1)
# fBkg_uu.SetMinimum(1.e-3)




N = 50
fGaus_ee = []
gmax = -1
for n in xrange(1,N):
   M = fRes_ee.GetXmin() + n*(fRes_ee.GetXmax()-fRes_ee.GetXmin())/N
   sM = str(M)
   sGaus = "TMath::Gaus(x,"+sM+","+sM+"*"+sfRes_ee+",1)"
   fGaus_ee.append( TF1("fGaus_ee_"+sM+"GeV",sGaus,fRes_ee.GetXmin(),fRes_ee.GetXmax()) )
   fGaus_ee[n-1].SetLineColor(ROOT.kBlue)
   fGaus_ee[n-1].SetNpx(1000) # 10000
   fGaus_ee[n-1].SetTitle("Absolute resolution (normalised Gaussians);Truth m_{ll} [GeV];Arbitrary scale")
   fmax = fGaus_ee[n-1].GetMaximum()
   if(fmax>=gmax): gmax = fmax
# fGaus_ee[0].SetMaximum(gmax*1.05)
fGaus_ee[0].SetMaximum(0.1)

# N = 50
# fGaus_uu = []
# gmax = -1
# for n in xrange(1,N):
#    M = fRes_uu.GetXmin() + n*(fRes_uu.GetXmax()-fRes_uu.GetXmin())/N
#    sM = str(M)
#    sGaus = "TMath::Gaus(x,"+sM+","+sM+"*"+sfRes_uu+",1)"
#    fGaus_uu.append( TF1("fGaus_uu_"+sM+"GeV",sGaus,fRes_uu.GetXmin(),fRes_uu.GetXmax()) )
#    fGaus_uu[n-1].SetLineColor(ROOT.kRed)
#    # fGaus_uu[n-1].SetLineStyle(2)
#    fGaus_uu[n-1].SetNpx(1000) #10000
#    fGaus_uu[n-1].SetTitle("Resolution;Truth m_{ll} [GeV];#sigma")
#    fmax = fGaus_uu[n-1].GetMaximum()
#    if(fmax>=gmax): gmax = fmax
# # fGaus_uu[0].SetMaximum(gmax*1.05)
# fGaus_uu[0].SetMaximum(0.1)


#### The signal model
k = str(500)
kR = str(10)
scale = str(1000)
Lmean = str(1*float(k))
Lsigma = str(0.2*float(Lmean))
# sClockwork_ee = "("+scale+"*TMath::Landau(x,"+Lmean+","+Lsigma+") * TMath::Exp(-0.001*x) * (RESONANCES) )*("+sfAcc_ee+")"
sClockwork_ee = "("+scale+"*TMath::Landau(x,"+Lmean+","+Lsigma+") * TMath::Exp(-x/"+k+") * (RESONANCES) )*("+sfAcc_ee+")"
# sClockwork_uu = "("+scale+"*TMath::Landau(x,"+Lmean+","+Lsigma+") * (RESONANCES) )*("+sfAcc_uu+")"
sResonances_ee = ""
sResonances_uu = ""
for n in xrange(1,1000):
   M = float(k)*ROOT.TMath.Sqrt(1+n*n/(float(kR)*float(kR)))
   if(M>6000): break
   sM = str(M)
   sWee = str(M*fRes_ee.Eval(M))
   # sWuu = str(M*fRes_uu.Eval(M))
   sn = str(n)
   frac = str((float(k)/M)*(float(k)/M))
   if(n==1):
      sResonances_ee += "(1-"+frac+")*TMath::Gaus(x,"+sM+","+sWee+",1)"
      # sResonances_uu += "(1-"+frac+")*TMath::Gaus(x,"+sM+","+sWuu+",1)"
   else:
      sResonances_ee += "+(1-"+frac+")*TMath::Gaus(x,"+sM+","+sWee+",1)"
      # sResonances_uu += "+(1-"+frac+")*TMath::Gaus(x,"+sM+","+sWuu+",1)"
sClockwork_ee = sClockwork_ee.replace("RESONANCES",sResonances_ee)
# sClockwork_uu = sClockwork_uu.replace("RESONANCES",sResonances_uu)
print sClockwork_ee
# print sClockwork_uu
fClockwork_ee = TF1("fClockwork_ee",sClockwork_ee,130.,fRes_ee.GetXmax())
# fClockwork_uu = TF1("fClockwork_uu",sClockwork_uu,130.,fRes_uu.GetXmax())
fClockwork_ee.SetLineColor(ROOT.kGreen)
# fClockwork_uu.SetLineColor(ROOT.kGreen)
# fClockwork_uu.SetLineStyle(2)
fClockwork_ee.SetLineWidth(1)
# fClockwork_uu.SetLineWidth(1)
# fClockwork_uu.SetLineStyle(2)
hBkgClockwork_ee = TH1D("hBkgClockwork_ee","ee selection;m_{ee} [GeV];Events",int(fRes_ee.GetXmax()-130),130,fRes_ee.GetXmax())
# hBkgClockwork_uu = TH1D("hBkgClockwork_uu","#mu#mu selection;m_{ee} [GeV];Events",int(fRes_uu.GetXmax()-130),130,fRes_uu.GetXmax())
hClockwork_ee = TH1D("hClockwork_ee","ee selection;m_{ee} [GeV];Events",int(fRes_ee.GetXmax()-130),130,fRes_ee.GetXmax())
# hClockwork_uu = TH1D("hClockwork_uu","#mu#mu selection;m_{#mu#mu} [GeV];Events",int(fRes_uu.GetXmax()-130),130,fRes_uu.GetXmax())
hClockwork_ee1 = TH1D("hClockwork_ee1","Emulated clockwork d#sigma/dm_{ll};m_{ll} [GeV];Arbitrary scale",int(2000-250),250,2000)
# hClockwork_uu1 = TH1D("hClockwork_uu1","Emulated clockwork d#sigma/dm_{ll};m_{ll} [GeV];Arbitrary scale",int(2000-250),250,2000)

for b in xrange(1,hClockwork_ee.GetNbinsX()+1):
   x = hClockwork_ee.GetBinCenter(b)
   y = fClockwork_ee.Eval(x)
   ybkg = fBkg_ee.Eval(x)
   hClockwork_ee.SetBinContent(b,y)
   hBkgClockwork_ee.SetBinContent(b,y+ybkg)
for b in xrange(1,hClockwork_ee1.GetNbinsX()+1):
   x = hClockwork_ee1.GetBinCenter(b)
   y = fClockwork_ee.Eval(x)
   hClockwork_ee1.SetBinContent(b,y)
hClockwork_ee.SetLineColor(ROOT.kGreen)
hClockwork_ee.SetLineWidth(1)
hClockwork_ee1.SetLineColor(ROOT.kGreen)
hClockwork_ee1.SetLineWidth(1)
hBkgClockwork_ee.SetLineColor(ROOT.kBlue)
hBkgClockwork_ee.SetLineWidth(1)

# for b in xrange(1,hClockwork_uu.GetNbinsX()+1):
#    x = hClockwork_uu.GetBinCenter(b)
#    y = fClockwork_uu.Eval(x)
#    ybkg = fBkg_uu.Eval(x)
#    hClockwork_uu.SetBinContent(b,y)
#    hBkgClockwork_uu.SetBinContent(b,y+ybkg)
# for b in xrange(1,hClockwork_uu1.GetNbinsX()+1):
#    x = hClockwork_uu1.GetBinCenter(b)
#    y = fClockwork_uu.Eval(x)
#    hClockwork_uu1.SetBinContent(b,y)
# hClockwork_uu.SetLineColor(ROOT.kGreen)
# hClockwork_uu.SetLineWidth(1)
# hClockwork_uu1.SetLineColor(ROOT.kGreen)
# hClockwork_uu1.SetLineWidth(1)
# hBkgClockwork_uu.SetLineColor(ROOT.kBlue)
# hBkgClockwork_uu.SetLineWidth(1)






cnv = TCanvas("c1","",500,500)
cnv.SetTicks(1,1)
cnv.SetLogy()

leg_resacc = TLegend(0.60,0.20,0.87,0.45)#,NULL,"brNDC")
leg_resacc.SetFillStyle(4000) #will be transparent
leg_resacc.SetFillColor(0)
leg_resacc.SetTextFont(42)
leg_resacc.SetBorderSize(0)
leg_resacc.AddEntry(fAcc_ee,"Acc#timesEff(ee)","l")
# leg_resacc.AddEntry(fAcc_uu,"Acc#timesEff(#mu#mu)","l")
leg_resacc.AddEntry(fRes_ee,"#sigma_{ee}/m_{ee}","l")
# leg_resacc.AddEntry(fRes_uu,"#sigma_{#mu#mu}/m_{#mu#mu}","l")

fRes_ee.SetMinimum(0.005)
fRes_ee.SetMaximum(2.)
fRes_ee.Draw()
fAcc_ee.Draw("same")
# fRes_uu.SetLineStyle(2)
# fAcc_uu.SetLineStyle(2)
# fRes_uu.Draw("same")
# fAcc_uu.Draw("same")
leg_resacc.Draw("same")
cnv.RedrawAxis()
cnv.Update()
cnv.SaveAs("clockwork_wres_resacc.pdf")
cnv.SaveAs("res.pdf(")




cnv = TCanvas("c2","",500,500)
cnv.SetTicks(1,1)
leg_gauss = TLegend(0.50,0.65,0.80,0.80)#,NULL,"brNDC")
leg_gauss.SetFillStyle(4000) #will be transparent
leg_gauss.SetFillColor(0)
leg_gauss.SetTextFont(42)
leg_gauss.SetBorderSize(0)
leg_gauss.AddEntry(fGaus_ee[0],"#it{G}(m_{ee},m_{n},#sigma_{ee}(m_{n}))","l")
# leg_gauss.AddEntry(fGaus_uu[0],"#it{G}(m_{#mu#mu},m_{n},#sigma_{#mu#mu}(m_{n}))","l")
for fi in xrange(len(fGaus_ee)):
   if(fi==0):
      fGaus_ee[fi].Draw()
      # fGaus_uu[fi].Draw("same")
   else:
      fGaus_ee[fi].Draw("same")
      # fGaus_uu[fi].Draw("same")
leg_gauss.Draw("same")
cnv.RedrawAxis()
cnv.Update()
cnv.SaveAs("clockwork_wres_resgauss.pdf")
cnv.SaveAs("res.pdf")



cnv = TCanvas("c1","",1500,500)
cnv.SetTicks(1,1)
leg_clockwork = TLegend(0.40,0.65,0.80,0.80)#,NULL,"brNDC")
leg_clockwork.SetFillStyle(4000) #will be transparent
leg_clockwork.SetFillColor(0)
leg_clockwork.SetTextFont(42)
leg_clockwork.SetBorderSize(0)
leg_clockwork.AddEntry(hClockwork_ee1,"~Clockwork d#sigma/dm_{ee}, #it{k}=500 GeV, #it{M}_{5}=6 TeV","l")
# leg_clockwork.AddEntry(hClockwork_uu1,"~Clockwork d#sigma/dm_{#mu#mu}, #it{k}=500 GeV, #it{M}_{5}=6 TeV","l")
hClockwork_ee1.SetMinimum(0)
hClockwork_ee1.SetMaximum(0.32)
hClockwork_ee1.Draw()
# hClockwork_uu1.SetLineStyle(2)
# hClockwork_uu1.Draw("same")
leg_clockwork.Draw("same")
cnv.RedrawAxis()
cnv.Update()
cnv.SaveAs("clockwork_wres_signal.pdf")
cnv.SaveAs("res.pdf")



cnv = TCanvas("c1","",1000,500)
cnv.Divide(2,1)
p1 = cnv.cd(1)
p2 = cnv.cd(2)
leg_bkgclockwork = TLegend(0.25,0.75,0.87,0.87)#,NULL,"brNDC")
leg_bkgclockwork.SetFillStyle(4000) #will be transparent
leg_bkgclockwork.SetFillColor(0)
leg_bkgclockwork.SetTextFont(42)
leg_bkgclockwork.SetBorderSize(0)
leg_bkgclockwork.AddEntry(fBkg_ee,"Background-only fit (from 80 fb^{-1} data)","l")
leg_bkgclockwork.AddEntry(hClockwork_ee,"Signal-only: #it{k}=500 GeV, #it{M}_{5}=6 TeV","l")
leg_bkgclockwork.AddEntry(hBkgClockwork_ee,"Background+Signal","l")
p1.cd()
p1.SetTicks(1,1)
p1.SetLogx()
p1.SetLogy()
fBkg_ee.SetTitle("ee selection;m_{ee} [GeV];Events")
fBkg_ee.Draw()
hClockwork_ee.Draw("same")
hBkgClockwork_ee.Draw("same")
leg_bkgclockwork.Draw("same")
p1.RedrawAxis()
p1.Update()

p2.cd()
p2.SetTicks(1,1)
p2.SetLogx()
p2.SetLogy()
# fBkg_uu.SetTitle("#mu#mu selection;m_{ee} [GeV];Events")
# fBkg_uu.Draw()
# hClockwork_uu.Draw("same")
# hBkgClockwork_uu.Draw("same")
leg_bkgclockwork.Draw("same")
p2.RedrawAxis()
p2.Update()

cnv.SaveAs("clockwork_wres_sigbkg.pdf")
cnv.Update()
cnv.SaveAs("res.pdf)")

