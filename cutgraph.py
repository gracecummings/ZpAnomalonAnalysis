import os
import argparse
import ROOT
import glob
from ROOT import *
from datetime import date

def findNDMass(filename):
    s1 = filename.split("_")[5]
    s2 = s1.split("ND")[1]

    return int(s2)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-mzp","--Zpmass",type=int,help = "Zp mass of samples you want")
    parser.add_argument("-mns","--NSmass",type=int,help = "NS mass of samples you want")

    args = parser.parse_args()

    mzp = args.Zpmass
    mns = args.NSmass
    listsignal = glob.glob('analysis_output/2018-11-0*/Delphes_analysis_output/ZpAnomalonHZ_Zp'+str(mzp)+'_ND*_NS'+str(mns)+'*')#can put back in date thing later
    listsignal.sort(key = findNDMass)
    sigfiles = []

    mg = TMultiGraph()
    
    
    tg0 = TGraph()
    tg0.SetTitle("muon in abs(eta) < 2.4")
    tg1 = TGraph()
    tg1.SetTitle("greater than one muon requirment")
    tg2 = TGraph()
    tg2.SetTitle("opposite charge muon requirment")
    tg3 = TGraph()
    tg3.SetTitle("leading and subleading muon pT cuts")
    tg4 = TGraph()
    tg4.SetTitle("ZpT > 100 GeV cut")
    tg5 = TGraph()
    tg5.SetTitle("greater than 0 fat jet requirement")
    tg6 = TGraph()
    tg6.SetTitle("Fat Jet in abs(eta) < 2.4")

    glist = [tg0,tg1,tg2,tg3,tg4,tg5,tg6]
    cutlist = ["muon abs(eta) < 2.4","muon # > 1","opposite charged muon","muon pT cut","ZpT > 100 GeV cut","Fat Jet # > 0","Fat Jet in abs(eta) < 2.4"]
    colors = [kOrange,kOrange+8,kViolet,kViolet+8,kCyan,kCyan-6,kGreen,kPink+7,kViolet+4,632,618]
    
    for i,path in enumerate(listsignal):
        sigfiles.append(ROOT.TFile(path))
        numevents   = sigfiles[i].Get('hnevents').GetBinContent(1)
        munumpass = sigfiles[i].Get('hmunumcut').GetBinContent(1)
        muetapass = sigfiles[i].Get('hmuetacut').GetBinContent(1)
        muqpass = sigfiles[i].Get('hmuqcut').GetBinContent(1)
        muptpass = sigfiles[i].Get('hmuptcut').GetBinContent(1)
        zptpass =  sigfiles[i].Get('hzptcutut').GetBinContent(1)
        fatnumpass = sigfiles[i].Get('hfatnumcut').GetBinContent(1)
        fatetapass = sigfiles[i].Get('hfatetacut').GetBinContent(1)
       
        params = listsignal[i].split('_')
        param1 = params[5]
        param1s = param1.split('D')
        masspoint = float(param1s[1])

        tg0.SetPoint(tg0.GetN(),masspoint,muetapass/numevents)
        tg1.SetPoint(tg1.GetN(),masspoint,munumpass/numevents)
        tg2.SetPoint(tg2.GetN(),masspoint,muqpass/numevents)
        tg3.SetPoint(tg3.GetN(),masspoint,muptpass/numevents)
        tg4.SetPoint(tg4.GetN(),masspoint,zptpass/numevents)
        tg5.SetPoint(tg5.GetN(),masspoint,fatnumpass/numevents)        
        tg6.SetPoint(tg6.GetN(),masspoint,fatetapass/numevents)


    #tg0.SetLineColor(colors[0])
    #mg.Add(tg0)
    #tg1.SetLineColor(colors[1])
    #mg.Add(tg1)

    leg = TLegend(0,0.55,0.45,0.88)
    
    for i,g in enumerate(glist):
        g.SetLineColor(colors[i+2])
        g.SetLineWidth(5)
        leg.AddEntry(g,cutlist[i],"l")
        mg.Add(g)

        
    tc = TCanvas("tc","Cutflow vs. Mass",1000,500)
    tc.Divide(2,1)
    tc.cd(1)
    mg.Draw("al")
    tc.cd(2)
    leg.Draw()
    tc.Update()
    
    tc.SaveAs("cutflowtest.png")
