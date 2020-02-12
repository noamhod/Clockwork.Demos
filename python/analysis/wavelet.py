import pywt
import numpy as np
import matplotlib.pyplot as plt
import math
import ROOT
from ROOT import *

## styles
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetPadLeftMargin(0.13)
ROOT.gStyle.SetPadRightMargin(0.13)


dir = ""

fBkgF = TFile("finalbkg.root","READ")
fBkg = fBkgF.Get("bkgfit")
fBkg.SetLineColor(ROOT.kRed)


### resolution
fPeterRes = TFile("ee_relResolFunction.root","READ")
fRes = fPeterRes.Get("relResol_dedicatedTF")
sfRes = "sqrt(pow(([0]+[1]/x+[2]/pow(x,2)+[3]*x+[4]*pow(x,2))*sqrt(pow([5],2)+pow([6]/sqrt(x),2)+pow([7]/x,2)),2)+pow((1.0-([0]+[1]/x+[2]/pow(x,2)+[3]*x+[4]*pow(x,2)))*sqrt(pow([8],2)+pow([9]/sqrt(x),2)+pow([10]/x,2)),2))"
for n in xrange(0,fRes.GetNpar()):
   print fRes.GetParName(n)+": "+str(fRes.GetParameter(n))
   sfRes = sfRes.replace("["+str(n)+"]",str(fRes.GetParameter(n)))
fRes.SetLineColor(ROOT.kRed)

### acceptance*efficiency
fPeterAcc = TFile("ee_accEffFunction.root","READ")
fAcc = fPeterAcc.Get("accEff_TF1")
sfAcc = "[0]+[1]/x+[2]/pow(x,2)+[3]/pow(x,3)+[4]/pow(x,4)+[5]/pow(x,5)+[6]*x+[7]*pow(x,2)"
for n in xrange(0,fAcc.GetNpar()):
   print fAcc.GetParName(n)+": "+str(fAcc.GetParameter(n))
   sfAcc = sfAcc.replace("["+str(n)+"]",str(fAcc.GetParameter(n)))
fAcc.SetLineColor(ROOT.kBlack)



### boundaries and binnings
Nwidths = 500
method = 'cmor1-1' #'cgau4' # 'cmor1-1' #'gaus7'
Nbins = 2000
xmin = 225
xmax = 2225


### the background
dBkg = []
hBkg = TH1D("hClockwork",";m_{ee} [GeV];AU",Nbins,xmin,xmax)
ymax = fBkg.GetMaximum()
for b in xrange(1,hBkg.GetNbinsX()+1):
   x = hBkg.GetBinCenter(b)
   y = fBkg.Eval(x)
   hBkg.SetBinContent(b,y/ymax)
   dBkg.append(y/ymax)
hBkg.SetLineColor(ROOT.kRed)


#### The signal model
k = str(500)
kR = str(10)
scale = str(1000)
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
ymax = fClockwork.GetMaximum()
hClockwork = TH1D("hClockwork",";m_{ee} [GeV];AU",Nbins,xmin,xmax)
dClockwork = []
for b in xrange(1,hClockwork.GetNbinsX()+1):
   x = hClockwork.GetBinCenter(b)
   y = fClockwork.Eval(x)
   hClockwork.SetBinContent(b,y/ymax)
   dClockwork.append(y/ymax)
hClockwork.SetLineColor(ROOT.kBlue)


### wavelet signal for comparison
t = np.linspace(xmin,xmax,Nbins, endpoint=False)
dWavelet = np.cos(1* t)*np.real(np.exp(-0.0001*(t-1000)**2)*np.exp(1j*0.001*(t-1000)))
hWavelet = TH1D("hWavelet",";m_{ee} [GeV];AU",Nbins,xmin,xmax)
for b in xrange(1,hWavelet.GetNbinsX()+1):
   hWavelet.SetBinContent(b,dWavelet[b-1])
hWavelet.SetLineColor(ROOT.kBlack)


### plot
c = TCanvas("c","",500,500)
c.cd()
hWavelet.Draw()
hClockwork.Draw("same")
hBkg.Draw("same")
c.SaveAs("wavelet.pdf(")
c.SaveAs("wavelet_puresignals.pdf")

widths = np.arange(1,1000)
# widths = np.array([1,2,4,8,
#                    10,13,16,19,
#                    20,21,22,23,24,25,26,27,28,29,
#                    30,31,32,33,34,35,36,37,38,39,
#                    40,41,42,43,44,45,46,47,48,49,
#                    50,51,52,53,54,55,56,57,58,59,
#                    60,70,80,90,
#                    100,200,300,400,500,600,700,800,900,
#                    1000,5000,10000,50000,100000,500000,1000000])


cwtmatr_wavelet, freqs_wavelet = pywt.cwt(dWavelet, widths, method)
# plt.plot(t,dWavelet)
# plt.show()
# plt.imshow(cwtmatr_wavelet, cmap='PRGn', aspect='auto',vmax=abs(cwtmatr_wavelet).max(), vmin=-abs(cwtmatr_wavelet).max()) 
# plt.show()

cwtmatr_clockwork, freqs_clockwork = pywt.cwt(dClockwork, widths, method)
# plt.plot(t,dClockwork)
# plt.show() 
# plt.imshow(cwtmatr_clockwork, cmap='PRGn', aspect='auto',vmax=abs(cwtmatr_clockwork).max(), vmin=-abs(cwtmatr_clockwork).max()) 
# plt.show()

cwtmatr_bkg, freqs_bkg = pywt.cwt(dBkg, widths, method)
# plt.plot(t,dBkg)
# plt.show() 
# plt.imshow(cwtmatr_bkg, cmap='PRGn', aspect='auto',vmax=abs(cwtmatr_bkg).max(), vmin=-abs(cwtmatr_bkg).max()) 
# plt.show()




###########
n_freqs_wavelet = len(freqs_wavelet)
print "wavelet: Nf=%g, fmin=%g, fmax=%g" % (n_freqs_wavelet,freqs_wavelet[n_freqs_wavelet-1],freqs_wavelet[0])
h2Wavelet = TH2D("h2Wavelet",";m_{ee} [GeV];Frequency [1/GeV];Amplitude",Nbins,xmin,xmax, 100,0,0.1)
h2Wavelet.SetLineColor(ROOT.kBlack)
h2Wavelet.SetMarkerColor(ROOT.kBlack)
h2Wavelet.SetFillColor(ROOT.kBlack)
for i in xrange(n_freqs_wavelet):
   f = freqs_wavelet[i]
   by = h2Wavelet.GetYaxis().FindBin(f)
   for j in xrange(len(cwtmatr_wavelet[i])):
      bx = j+1
      z = abs(cwtmatr_wavelet[i][j])
      h2Wavelet.SetBinContent(bx,by,z)


## fill here the h2Wavelet 2d histogram
n_freqs_clockwork = len(freqs_clockwork)
print "clockwork: Nf=%g, fmin=%g, fmax=%g" % (n_freqs_clockwork,freqs_clockwork[n_freqs_clockwork-1],freqs_clockwork[0])
h2Clockwork = TH2D("h2Clockwork",";m_{ee} [GeV];Frequency [1/GeV];Amplitude",Nbins,xmin,xmax, 100,0,0.1)
h2Clockwork.SetLineColor(ROOT.kBlue)
h2Clockwork.SetMarkerColor(ROOT.kBlue)
h2Clockwork.SetFillColor(ROOT.kBlue)
for i in xrange(n_freqs_clockwork):
   f = freqs_clockwork[i]
   by = h2Clockwork.GetYaxis().FindBin(f)
   for j in xrange(len(cwtmatr_clockwork[i])):
      bx = j+1
      z = abs(cwtmatr_clockwork[i][j])
      h2Clockwork.SetBinContent(bx,by,z)

## fill here the h2Clockwork 2d histogram
n_freqs_bkg = len(freqs_bkg)
print "background: Nf=%g, fmin=%g, fmax=%g" % (n_freqs_bkg,freqs_bkg[n_freqs_bkg-1],freqs_bkg[0])
h2Bkg = TH2D("h2Bkg",";m_{ee} [GeV];Frequency [1/GeV];Amplitude",Nbins,xmin,xmax, 100,0,0.1)
h2Bkg.SetLineColor(ROOT.kBlack)
h2Bkg.SetMarkerColor(ROOT.kBlack)
h2Bkg.SetFillColor(ROOT.kBlack)
for i in xrange(n_freqs_bkg):
   f = freqs_bkg[i]
   by = h2Bkg.GetYaxis().FindBin(f)
   for j in xrange(len(cwtmatr_bkg[i])):
      bx = j+1
      z = abs(cwtmatr_bkg[i][j])
      h2Bkg.SetBinContent(bx,by,z)


c = TCanvas("c","",1500,500)
c.Divide(3,1)
c.cd(1)
h2Wavelet.SetTitle("Arbitrary wavelet")
h2Wavelet.Draw("contz")
c.cd(2)
h2Clockwork.SetTitle("Clockwork signal")
h2Clockwork.Draw("contz")
c.cd(3)
h2Bkg.SetTitle("Background shape")
h2Bkg.Draw("contz")
c.SaveAs("wavelet_puresignals_2d.pdf")
c.SaveAs("wavelet.pdf")


# c = TCanvas("c","",1500,500)
c = TCanvas("c","",1000,500)
c.Divide(2,1)
# c.Divide(3,1)
# c.cd(1)
# h2Clockwork.SetTitle("Clockwork vs Background")
# h2Bkg.SetTitle("Clockwork vs Background")
# h2Clockwork.Draw("scat")
# h2Bkg.Draw("scat same")
# c.cd(2)
c.cd(1)
pxClockwork = h2Clockwork.ProjectionX()
pxClockwork.SetLineColor(ROOT.kBlue)
pxClockwork.SetTitle("Projection on mass axis;m_{ee} [GeV];Amplitude")
pxClockwork.Draw("hist")
pxBkg = h2Bkg.ProjectionX()
pxBkg.SetLineColor(ROOT.kBlack)
pxBkg.SetTitle("Projection on mass axis;m_{ee} [GeV];Amplitude")
pxBkg.Draw("histsame")
# c.cd(3)
c.cd(2)
pyClockwork = h2Clockwork.ProjectionY()
pyClockwork.SetLineColor(ROOT.kBlue)
pyClockwork.SetTitle("Projection on frequency axis;Frequency [1/GeV];Amplitude")
pyClockwork.Draw("hist")
pyBkg = h2Bkg.ProjectionY()
pyBkg.SetLineColor(ROOT.kBlack)
pyBkg.SetTitle("Projection on frequency axis;Frequency [1/GeV];Amplitude")
pyBkg.Draw("histsame")
c.SaveAs("wavelet_puresignals_rojections.pdf")
c.SaveAs("wavelet.pdf)")

