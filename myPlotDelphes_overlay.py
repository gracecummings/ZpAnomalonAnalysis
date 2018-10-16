#This script should take the root files produced from the other myPlotDelphes scripts to make overlaid signal and bkg plots

import os
import argparse
import ROOT
from ROOT import kViolet, kCyan
from datetime import date

#Function to calculate scaling
def findScale(prodnum,lumi,xsec):
    expnum = xsec*lumi
    scalefac = expnum/prodnum

    return scalefac

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s1","--signal1",type=str,help = "first signal root file")
    parser.add_argument("-s2","--signal2",type=str,help = "second signal root file")
    parser.add_argument("-s3","--signal3",type=str,help = "third signal root file")
    parser.add_argument("-b","--bkg", type=str,help = "background root file")
    parser.add_argument("-L","--lumi", type=float,default = 35.9, help = "integrated luminosity for scale in fb^-1")
    parser.add_argument("-x","--xsec", type=float,help = "desired siganl cross section in fb")
    parser.add_argument("-o","--output",type=str,default ="overlay_out.root" ,help = "output file name")
    args = parser.parse_args()

    
    fsig1 = ROOT.TFile(args.signal1)
    fsig2 = ROOT.TFile(args.signal2)
    fsig3 = ROOT.TFile(args.signal3)
    fbkg = ROOT.TFile(args.bkg)
    fout = args.output

    numsig1 = fsig1.Get('hnevents').GetBinContent(1)
    numsig2 = fsig2.Get('hnevents').GetBinContent(1)
    numsig3 = fsig3.Get('hnevents').GetBinContent(1)
    numbkg = fbkg.Get('hnevents').GetBinContent(1)
    sig1xs  = 1000*fsig1.Get('hxs').GetBinContent(1)#converting to fb
    sig2xs  = 1000*fsig2.Get('hxs').GetBinContent(1)#converting to fb
    sig3xs  = 1000*fsig3.Get('hxs').GetBinContent(1)#converting to fb
    bkgxs  = 1000*fbkg.Get('hxs').GetBinContent(1)

    if args.xsec:
        sig1xs = args.xsec
        sig2xs = args.xsec
        sig3xs = args.xsec

    sig1scale = findScale(numsig1,args.lumi,sig1xs)
    sig2scale = findScale(numsig2,args.lumi,sig2xs)
    sig3scale = findScale(numsig3,args.lumi,sig3xs)
    bkgscale = findScale(numbkg,args.lumi,bkgxs)

    keys  = fsig1.GetListOfKeys()

    for i,key in enumerate(keys):
        hname = key.GetName()
        print hname
        tc = ROOT.TCanvas("tc",hname,450,450)
        tc.SetLogy()#This is not ideal, will set which ones it makes sense to do this for later

        if "mt2" in hname:#Do not make mt2 overlay plots
            continue
        
        hsig1 = fsig1.Get(hname)
        hsig1.SetLineColor(801)#kOrange+1
        hsig1.SetStats(0)
        hsig1.Scale(sig1scale)

        hsig2 = fsig2.Get(hname)
        hsig2.SetLineColor(kCyan
        )#kOrange+1
        hsig2.SetStats(0)
        hsig2.Scale(sig2scale)

        hsig3 = fsig3.Get(hname)
        hsig3.SetLineColor(kViolet)#kOrange+1
        hsig3.SetStats(0)
        hsig3.Scale(sig3scale)

        hbkg = fbkg.Get(hname)
        hbkg.SetStats(0)
        hbkg.Scale(bkgscale)
        hbkg.SetFillColor(861)#kAzure+1
        bkgmax = hbkg.GetMaximum()

        hbkg.SetMaximum(bkgmax*100)
        hsig1.SetMaximum(bkgmax*100)
        hsig2.SetMaximum(bkgmax*100)
        hsig3.SetMaximum(bkgmax*100)
        hbkg.SetMinimum(0.1)
        hsig1.SetMinimum(0.1)
        hsig2.SetMinimum(0.1)
        hsig3.SetMinimum(0.1)
        hbkg.Draw("HIST")
        hsig1.Draw("SAMEHIST")
        hsig2.Draw("SAMEHIST")
        hsig3.Draw("SAMEHIST")
        
        #hsig.Draw("HIST")
        
        leg = ROOT.TLegend(0.45,0.7,0.88,0.85)
        leg.AddEntry(hsig1,"Zp 2000 ND 500 NS 200, 0.1 pb","l")
        leg.AddEntry(hsig2,"Zp 1500 ND 400 NS 150, 0.1 pb","l")
        leg.AddEntry(hsig3,"Zp 1000 ND 300 NS 100, 0.1 pb","l")
        leg.AddEntry(hbkg,"Z+jets","f")
        #ROOT.gStyle.SetLegendTextSize(5)
        ROOT.gStyle.SetLegendBorderSize(0)
        leg.Draw()

        savdir = str(date.today())
        if not os.path.exists("analysis_output/"+savdir+"/images"):
            os.makedirs("analysis_output/"+savdir+"/images")
        pngname = "analysis_output/"+savdir+"/images/"+hname+".png"
        tc.SaveAs(pngname)

        #if not os.path.exists("analysis_output/"+savdir+"/Delphes_analysis_output"):
        #    os.makedirs("analysis_output/"+savdir+"/Delphes_analysis_output")
        #tfout = ROOT.TFile("analysis_ouput/"+savdir+"/Delphes_analysis_output/"+fout,"RECREATE")
        #tc.Write()

    fout.Close()
    fsig.Close()
    fbkg.Close()
        
