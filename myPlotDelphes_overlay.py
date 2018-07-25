#This script should take the root files produced from the other myPlotDelphes scripts to make overlaid signal and bkg plots

import argparse
import ROOT

#Function to calculate scaling
#This should be moved to the analysis script and made dynamic, or store event number in analysis script
def findScale(numevents,lumi,datatype,sigxs):
    zjxs = 17593.3 #femptobarns
    zpxs = 11.814  #femptobarns heavy params
    xs = 0

    #Chose which crosssection to use
    if "sig" in datatype:
        if sigxs:
            xs = sigxs
        else:
            xs = zpxs
    if "bkg" in datatype:
        xs = zjxs

    #Find number of events in file
    prodnum = numevents
    
    #find expected number of events for given luminosity and orgicanl cross sectioon
    expnum   = xs*lumi
    scalefac = expnum/prodnum

    return scalefac


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--signal",type=str,help = "signal root file")
    parser.add_argument("-b","--bkg", type=str,help = "background root file")
    parser.add_argument("-L","--lumi", type=float,default = 35.9, help = "integrated luminosity for scale in fb^-1")
    parser.add_argument("-x","--xsec", type=float,default = 1000,help = "desired siganl cross section in fb")
    parser.add_argument("-o","--output",type=str,default ="overlay_out.root" ,help = "output file name")
    args = parser.parse_args()

    
    fsig = ROOT.TFile(args.signal)
    fbkg = ROOT.TFile(args.bkg)
    fout = ROOT.TFile(args.output,"RECREATE")

    keys  = fsig.GetListOfKeys()

    sigscale = findScale(20000,args.lumi,"sig",args.xsec)#scaling xsec to 1pb
    print sigscale
    bkgscale = findScale(20000,args.lumi,"bkg",0)
    print bkgscale

    for i,key in enumerate(keys):
        hname = key.GetName()
        print hname
        tc = ROOT.TCanvas("tc",hname,450,450)
        tc.SetLogy()#This is not ideal, will set which ones it makes sense to do this for later
        
        hsig = fsig.Get(hname)
        hsig.SetLineColor(801)#kOrange+1
        hsig.SetStats(0)
        hsig.Scale(sigscale)

        hbkg = fbkg.Get(hname)
        hbkg.SetStats(0)
        hbkg.Scale(bkgscale)
        hbkg.SetFillColor(861)#kAzure+1
        hbkg.SetMinimum(0.1)
        hbkg.Draw("HIST")
        hsig.SetMinimum(0.1)
        hsig.Draw("SAMEHIST")
        
        #hsig.Draw("HIST")
        
        leg = ROOT.TLegend(0.62,0.7,0.88,0.8)
        leg.AddEntry(hsig,"signal mc","l")
        leg.AddEntry(hbkg,"bkg mc","f")
        ROOT.gStyle.SetLegendTextSize(5)
        ROOT.gStyle.SetLegendBorderSize(0)
        if "hdphi_ZMET" not in hname:
            leg.Draw()

        tc.Write()

    fout.Close()
    fsig.Close()
    fbkg.Close()
        
