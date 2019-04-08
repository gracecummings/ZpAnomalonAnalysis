#This script should take the root files produced from the other myPlotDelphes scripts to make overlaid signal and bkg plots

import os
import argparse
import ROOT
import glob
from ROOT import kOrange, kViolet, kCyan, kGreen, kPink, kAzure, kMagenta
from datetime import date

#Function to calculate scaling
def findScale(prodnum,lumi,xsec):
    expnum = xsec*lumi
    scalefac = expnum/prodnum

    return scalefac

def findNDMass(filename):
    s1 = filename.split("_")[5]
    s2 = s1.split("ND")[1]

    return int(s2)

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
    listsignal = glob.glob('analysis_output/2019-02-05/Delphes_analysis_output/ZpAnomalonHZ_Zp'+str(mzp)+'_ND*_NS'+str(mns)+'*')#can put back in date thing later
    listsignal.sort(key = findNDMass)
    listbkg = glob.glob('analysis_output/2019-02-05/Delphes_analysis_output/*_bkg*')#can put back in date thing later


    #colors = [kOrange,kOrange+8,kViolet,kViolet+8,kCyan,kCyan-6,kGreen,kPink+7,kViolet+4,632,618]
    sigcolors  = [kOrange,kOrange-3,kCyan,kCyan-6,kGreen,kGreen-6,kPink+7,kPink+4,kViolet+4,kMagenta-2,kMagenta+3]
    sigfiles   = []
    sigweights = []
    sigxsl     = []
    bkgfiles   = []
    bkginfo = []
    bkgcolors  = [kAzure-4,kViolet,kAzure-6,kViolet+8]
    
    for i,path in enumerate(listsignal):
        sigfiles.append(ROOT.TFile(path))
        numevents   = sigfiles[i].Get('hnevents').GetBinContent(1)
        xsp = sigfiles[i].Get('hxs').GetBinContent(1)
        print path
        print "THE XS IN P is ",xsp
        sigxs       = 1000*sigfiles[i].Get('hxs').GetBinContent(1)#converts to fb
        print "THE XS IS ",sigxs
        if args.xsec:
            sigxs = args.xsec
        print "USED XS ",sigxs
        sigxsl.append(sigxs)
        sigweights.append(findScale(numevents,args.lumi,sigxs))

    for i,path in enumerate(listbkg):
        #print path
        bkgdict = {}
        bkgfiles.append(ROOT.TFile(path))
        numbkg = bkgfiles[i].Get('hnevents').GetBinContent(1)
        #print numbkg
        bkgxs  = 1000*bkgfiles[i].Get('hxs').GetBinContent(1)    
        bkgscale = findScale(numbkg,args.lumi,bkgxs)
        bkgdict["xs"] = bkgxs
        bkgdict["scale"] = bkgscale
        params1 = listbkg[i].split('/')
        params2 = params1[3].split('_')
        bkgname = params2[0]
        bkgdict["name"] = bkgname
        bkginfo.append(bkgdict)


    bkginfo = sorted(bkginfo,key = lambda bkg:bkg["xs"])#This should put least prominent background first
    
    keys  = sigfiles[0].GetListOfKeys()

    for i,key in enumerate(keys):
        hname = key.GetName()
        tc = ROOT.TCanvas("tc",hname,450,450)
        tc.SetLogy()#This is not ideal, will set which ones it makes sense to do this for later

        #if "mt2gl" or "mt2gh" in hname:#Do not make extra guess mt2 overlay plots
        #    continue
        #if "hht" in hname:
        #    print hname

        leg = ROOT.TLegend(0.45,0.55,0.90,0.88)

        maxbkg = 0
        hsbkg = ROOT.THStack('hsbkg','')
        for j in range(len(bkginfo)):
            hbkg = bkgfiles[j].Get(hname)
            hbkg.SetStats(0)
            hbkg.Scale(bkginfo[j]["scale"])
            hbkg.SetFillColor(bkgcolors[j])
            bkgmax = hbkg.GetMaximum()
            if bkgmax > maxbkg:
                maxbkg = bkgmax
            #print "max bkg is using ",maxbkg
            hbkg.SetMaximum(10000000)#maxbkg*2000)
            #print "max after setting max ",hbkg.GetMaximum()
            hbkg.SetMinimum(0.1)
            hsbkg.Add(hbkg)
            #print "stack max with bkg ", hsbkg.GetMaximum()
            hsbkg.Draw("HIST")
            hsbkg.SetMaximum(10000000)#maxbkg*2000)
            hsbkg.SetMinimum(0.1)
            leg.AddEntry(hbkg,bkginfo[j]["name"],"f")
                
        for j in range(len(sigfiles)):
            h = sigfiles[j].Get(hname)
            h.SetLineColor(sigcolors[j])
            h.SetStats(0)
            print listsignal[j]
            print "print scale fac used ",sigweights[j]
            h.Scale(sigweights[j])
            #print "max signal sees ",maxbkg*2000
            h.SetMaximum(10000000)
            h.SetMinimum(0.1)
            h.Draw("HISTSAME")
            params = listsignal[j].split('_')
            zpstr  = params[4]
            ndstr  = params[5]
            nsstr  = params[6]
            leg.AddEntry(h,zpstr+" "+ndstr+" "+nsstr+", "+str(sigxsl[j]/1000)+" pb","l")
        ROOT.gStyle.SetLegendBorderSize(0)
        leg.Draw()

        savdir = str(date.today())
        if not os.path.exists("analysis_output/"+savdir+"/images"):
            os.makedirs("analysis_output/"+savdir+"/images")
        pngname = "analysis_output/"+savdir+"/images/Zp"+str(mzp)+"_NS"+str(mns)+"_"+hname+".png"
        tc.SaveAs(pngname)
        


    print "you made stacked overlays. good for you, you should fix the error statement"
    
    for f in sigfiles:
        f.Close()
        
    for f in bkgfiles:
        f.Close()
        
