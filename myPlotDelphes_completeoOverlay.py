#This script should take the root files produced from the other myPlotDelphes scripts to make overlaid signal and bkg plots

import os
import argparse
import ROOT
import glob
from ROOT import kOrange, kViolet, kCyan, kGreen, kPink
from datetime import date

#Function to calculate scaling
def findScale(prodnum,lumi,xsec):
    expnum = xsec*lumi
    scalefac = expnum/prodnum

    return scalefac

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-mzp","--Zpmass",type=int,help = "Zp mass of samples you want")
    parser.add_argument("-mns","--NSmass",type=int,help = "NS mass of samples you want")    
    parser.add_argument("-b","--bkg", type=str,help = "background root file")
    parser.add_argument("-L","--lumi", type=float,default = 35.9, help = "integrated luminosity for scale in fb^-1")
    parser.add_argument("-x","--xsec", type=float,help = "desired siganl cross section in fb")
    parser.add_argument("-o","--output",type=str,default ="overlay_out.root" ,help = "output file name")
    args = parser.parse_args()

    mzp = args.Zpmass
    mns = args.NSmass
    listsignal = glob.glob('analysis_output/*/Delphes_analysis_output/ZpAnomalonHZ_Zp'+str(mzp)+'_ND*_NS'+str(mns)+'*')

    colors = [kOrange,kOrange+8,kViolet,kViolet+8,kCyan,kCyan-6,kGreen,kPink+7,kViolet+4,632,618]
    sigfiles = []
    weights  = []
    for i,path in enumerate(listsignal):
        sigfiles.append(ROOT.TFile(path))
        numevents   = sigfiles[i].Get('hnevents').GetBinContent(1)
        sigxs       = 1000*sigfiles[i].Get('hxs').GetBinContent(1)#converts to fb
        if args.xsec:
            sigxs = args.xsec
        weights.append(findScale(numevents,args.lumi,sigxs))
        
    fbkg = ROOT.TFile(args.bkg)
    numbkg = fbkg.Get('hnevents').GetBinContent(1)
    bkgxs  = 1000*fbkg.Get('hxs').GetBinContent(1)
    bkgscale = findScale(numbkg,args.lumi,bkgxs)

    keys  = sigfiles[0].GetListOfKeys()

    for i,key in enumerate(keys):
        hname = key.GetName()
        tc = ROOT.TCanvas("tc",hname,450,450)
        tc.SetLogy()#This is not ideal, will set which ones it makes sense to do this for later

        #if "mt2gl" or "mt2gh" in hname:#Do not make extra guess mt2 overlay plots
        #    continue
        #if "hht" in hname:
        #    print hname
            
        hbkg = fbkg.Get(hname)
        hbkg.SetStats(0)
        hbkg.Scale(bkgscale)
        hbkg.SetFillColor(861)#kAzure+1
        bkgmax = hbkg.GetMaximum()
        hbkg.SetMaximum(bkgmax*100)
        hbkg.SetMinimum(0.1)
        hbkg.Draw("HIST")

        leg = ROOT.TLegend(0.45,0.55,0.90,0.88)
        leg.AddEntry(hbkg,"Z+jets","f")
        
        for j in range(len(sigfiles)):
            h = sigfiles[j].Get(hname)
            h.SetLineColor(colors[j])
            h.SetStats(0)
            h.Scale(weights[j])
            h.SetMaximum(bkgmax*100)
            h.SetMinimum(0.1)
            h.Draw("HISTSAME")
            params = listsignal[j].split('_')
            zpstr  = params[4]
            ndstr  = params[5]
            nsstr  = params[6]
            leg.AddEntry(h,zpstr+" "+ndstr+" "+nsstr+", "+str(sigxs/1000)+" pb","l")
        ROOT.gStyle.SetLegendBorderSize(0)
        leg.Draw()

        savdir = str(date.today())
        if not os.path.exists("analysis_output/"+savdir+"/images"):
            os.makedirs("analysis_output/"+savdir+"/images")
        pngname = "analysis_output/"+savdir+"/images/"+hname+".png"
        tc.SaveAs(pngname)


    for f in sigfiles:
        f.Close()
        
    fbkg.Close()
        
