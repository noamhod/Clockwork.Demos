#!/usr/bin/env python
import ROOT
from ROOT import *
import math


## styles
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetPadLeftMargin(0.13)

####### background function 
xmin = 225 #130
xmax = 6000 # 10130
N = int(xmax-xmin) ## 1 GeV bins
bkgfit = TF1("bkgfit","[0] * [2]/((x-[1])^2 + [2]^2) * (1-(x/13000)^[3])^[4] * (x/13000)^([5]+[6]*log(x/13000)+[7]*log(x/13000)^2+[8]*log(x/13000)^3)",xmin,xmax)
bkgfit.SetParName(0,"N");  bkgfit.SetParameter(0, 1)
# bkgfit.SetParName(0,"N");  bkgfit.SetParameter(0, 178000)
bkgfit.SetParName(1,"m0"); bkgfit.SetParameter(1, +91.1876)
bkgfit.SetParName(2,"w0"); bkgfit.SetParameter(2, +2.4952)
bkgfit.SetParName(3,"c");  bkgfit.SetParameter(3, +1)
bkgfit.SetParName(4,"b");  bkgfit.SetParameter(4, +1.5)
bkgfit.SetParName(5,"p0"); bkgfit.SetParameter(5, -12.38)
bkgfit.SetParName(6,"p1"); bkgfit.SetParameter(6, -4.29)
bkgfit.SetParName(7,"p2"); bkgfit.SetParameter(7, -0.919)
bkgfit.SetParName(8,"p3"); bkgfit.SetParameter(8, -0.0845)
bkgfitI = bkgfit.Integral(xmin,xmax)
print "Integral:",bkgfitI

####### run 2 final dataset
f = TFile("mInv_spectrum_combined_ll_rel21.root","READ")
data = f.Get("mInv_spectrum_201518_ee_1GeV")
data.SetMinimum(5.e-5)
dataN = 0
xup = -1
xxx = -1
isfound = False
# integral0 = data.Integral(1,data.GetNbinsX())
for b in xrange(data.GetNbinsX()):
   x = data.GetBinCenter(b)
   if(x<xmin): continue
   if(x>xmax): break
   integralx = data.Integral(b,data.GetNbinsX())
   relerr    = (1/math.sqrt(integralx))*100 if(integralx>0) else 100
   dataN += data.GetBinContent(b)
   if(relerr>=10 and not isfound):
      xxx = x
      isfound = True
      
   # if(x<2300): print "x:%g --> N=%g --> D=%g" % (x,integralx,relerr)
print "dataN:",dataN
print "xxx=",xxx

gdata = TGraphAsymmErrors()
for i in xrange(1,data.GetNbinsX()+1):
   value = data.GetBinContent(i)
   if(value!=0):
      y1 = value + 1.0
      d1 = 1.0 - 1.0/(9.0*y1) + 1.0/(3*ROOT.TMath.Sqrt(y1))
      error_poisson_up = y1*d1*d1*d1 - value
      y2 = value
      d2 = 1.0 - 1.0/(9.0*y2) - 1.0/(3.0*ROOT.TMath.Sqrt(y2))
      error_poisson_down = value - y2*d2*d2*d2
      gdata.SetPoint(i-1, data.GetBinCenter(i), value)
      gdata.SetPointError(i-1, 0, 0, error_poisson_down, error_poisson_up)
   else:
     # if 0 data points, set Data point to -999 and off the plot
     gdata.SetPoint(i-1, data.GetBinCenter(i), -999.)
     gdata.SetPointError(i-1, 0, 0, 0, 0)
gdata.SetLineColor(1)
gdata.SetMarkerColor(1)
gdata.SetMarkerStyle(20)
gdata.SetMarkerSize(0.5)
gdata.SetMinimum(5.e-5)


####### renormalisation
normfactor = dataN/bkgfitI
print "normfactor:",normfactor
bkgfit.SetParameter(0,normfactor)

fOut = TFile("finalbkg.root","RECREATE")
fOut.cd()
bkgfit.Write()
fOut.Write()
fOut.Close()

bkgfitI1 = bkgfit.Integral(xmin,xmax)
print "Integral after rescaling:",bkgfitI1

####### function as histogram for the puls
bkghist = data.Clone("bkghist")
bkghist.Reset()
for b in xrange(data.GetNbinsX()):
   x = data.GetBinCenter(b)
   if(x<xmin): continue
   if(x>xmax): break
   y = bkgfit.Eval(x)
   bkghist.SetBinContent(b,y)
bkghist.SetLineColor(ROOT.kRed)




################ signal
### get the resolution
fPeterRes = TFile("ee_relResolFunction.root","READ")
fRes = fPeterRes.Get("relResol_dedicatedTF")
sfRes = "sqrt(pow(([0]+[1]/x+[2]/pow(x,2)+[3]*x+[4]*pow(x,2))*sqrt(pow([5],2)+pow([6]/sqrt(x),2)+pow([7]/x,2)),2)+pow((1.0-([0]+[1]/x+[2]/pow(x,2)+[3]*x+[4]*pow(x,2)))*sqrt(pow([8],2)+pow([9]/sqrt(x),2)+pow([10]/x,2)),2))"
for n in xrange(0,fRes.GetNpar()):
   print fRes.GetParName(n)+": "+str(fRes.GetParameter(n))
   sfRes = sfRes.replace("["+str(n)+"]",str(fRes.GetParameter(n)))
fRes.SetLineColor(ROOT.kRed)
### get the acceptance*efficiency
fPeterAcc = TFile("ee_accEffFunction.root","READ")
fAcc = fPeterAcc.Get("accEff_TF1")
sfAcc = "[0]+[1]/x+[2]/pow(x,2)+[3]/pow(x,3)+[4]/pow(x,4)+[5]/pow(x,5)+[6]*x+[7]*pow(x,2)"
for n in xrange(0,fAcc.GetNpar()):
   print fAcc.GetParName(n)+": "+str(fAcc.GetParameter(n))
   sfAcc = sfAcc.replace("["+str(n)+"]",str(fAcc.GetParameter(n)))
fAcc.SetLineColor(ROOT.kBlack)
#### get the signal model
hsig = TH1D("hsig_ee","",N,xmin,xmax)
hsigsmall = TH1D("hsigsmall",";m_{ee} [GeV]; Events",1200,400,1600)
hbkgsig = hsig.Clone("hbkgsig_ee")
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
#make the signal-only and signal+bkg histogram from the analytical shapes
hsig.SetLineColor(ROOT.kGreen)
hsig.SetLineWidth(1)
hsigsmall.SetLineColor(ROOT.kGreen)
hbkgsig.SetLineColor(ROOT.kCyan)
hbkgsig.SetLineWidth(1)
for i in xrange(1,N+1):
   x = hsig.GetBinCenter(i)
   y = fClockwork.Eval(x)
   hsig.SetBinContent(i,y)
   if(x>=hsigsmall.GetXaxis().GetXmin() and x<=hsigsmall.GetXaxis().GetXmax()):
      binsmall = hsigsmall.FindBin(x)
      hsigsmall.SetBinContent(binsmall,y)
   nbkg = bkgfit.Eval(x)
   hbkgsig.SetBinContent(i,nbkg+y)
hbkgsig.SetMaximum(5.e+4)
hbkgsig.SetMinimum(1.e-2)






####### plot
leg = TLegend(0.65,0.52,0.9,0.64)#,NULL,"brNDC")
leg.SetFillStyle(4000) #will be transparent
leg.SetFillColor(0)
leg.SetTextFont(42)
leg.SetBorderSize(0)
leg.AddEntry(data,    "Data 139 fb-1","ple")
leg.AddEntry(hsig,    "Signal only","l")
leg.AddEntry(bkgfit,  "Background fit","l")
leg.AddEntry(hbkgsig, "Background#plusSignal","l")

cnv = TCanvas("c","",700,500)
cnv.cd()
cnv.SetTicks(1,1)
cnv.SetLogy()
cnv.SetLogx()
data.SetTitle("139 fb^{-1} Data, ee selection with Backgroud fit vs Clockwork signal")
data.SetMarkerSize(0.5)
dataclone = data.Clone()
dataclone.Reset()
dataclone.Draw()
dataclone.SetMaximum(5.e+5)
dataclone.SetMinimum(5.e-5)
# data.Draw()
# hbkgsig.Draw()
gdata.Draw("Psame")
hbkgsig.Draw("same")
bkgfit.Draw("same")
hsig.Draw("same")
leg.Draw("same")
stopline = TLine(xxx,cnv.GetUymin(),xxx,1.2*cnv.GetUymax())
stopline.SetLineColor(ROOT.kYellow)
stopline.SetLineWidth(3)
stopline.SetLineStyle(2)
stopline.Draw("same")

ROOT.gStyle.SetPadBottomMargin(0.16)

subpad = TPad("subpad","",0.39,0.65,0.9,0.88)
subpad.SetTicks(1,1)
hsigsmall.GetXaxis().SetLabelFont(42)
hsigsmall.GetXaxis().SetLabelSize(0.07)
hsigsmall.GetXaxis().SetTitleSize(0.07)
hsigsmall.GetXaxis().SetTitleFont(42)
hsigsmall.GetYaxis().SetLabelFont(42)
hsigsmall.GetYaxis().SetLabelSize(0.07)
hsigsmall.GetYaxis().SetTitleSize(0.07)
hsigsmall.GetYaxis().SetTitleFont(42)
hsigsmall.GetYaxis().SetTitleOffset(0.4)
print "hsig.Integral(500,6000)=",hsig.Integral(500,6000)
print "bkgfit.Integral(500,6000)=",bkgfit.Integral(500,6000)

subpad.Draw()
subpad.cd()
hsigsmall.Draw()
subpad.cd()

leg1 = TLegend(0.5,0.35,0.8,0.8)#,NULL,"brNDC")
leg1.SetFillStyle(4000) #will be transparent
leg1.SetFillColor(0)
leg1.SetTextFont(42)
leg1.SetBorderSize(0)
leg1.AddEntry(0, "#int(sig)="+str(int(hsig.Integral(500,6000))),"")
leg1.AddEntry(0, "","")
leg1.AddEntry(0, "#int(bkg)="+str(int(bkgfit.Integral(500,6000))),"")
leg1.AddEntry(0, "","")
leg1.AddEntry(0, "in 500<m_{ee}<6000 GeV","")
leg1.Draw("same")
cnv.RedrawAxis()
cnv.Update()
cnv.SaveAs("plotbkgfit.pdf")





# c1 = TCanvas("c1")
# h1 = TH1F("h1","test1",100,-4,4)
# h1.FillRandom("gaus")
# h1.Draw()

# subpad = TPad("subpad","",0.6,0.3,0.95,0.65)
# subpad.Draw()
# subpad.cd()
# h2 = TH1F("h2","test2",100,-2,4)
# h2.FillRandom("gaus")
# h2.Draw()
