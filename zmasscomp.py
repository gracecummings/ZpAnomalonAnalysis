import os
import argparse
import ROOT
import glob as g
from ROOT import kOrange, kViolet, kCyan, kGreen, kPink, kAzure, kMagenta
from datetime import date

def findScale(prodnum,lumi,xsec):
    expnum = xsec*lumi
    scalefac = expnum/prodnum
    return scalefac

def findNDMass(filename):
    s1 = filename.split("_")[5]
    s2 = s1.split("ND")[1]
    return int(s2)

def findNDMassFromDict(dicinquestion):
    filename = dicinquestion["fpath"]
    mnd = findNDMass(filename)
    return mnd

def findZpMass(filename):
    s1 = filename.split("_")[4]
    s2 = s1.split("Zp")[1]
    return s2

def findZpMassFromDict(dicinquestion):
    filename = dicinquestion["fpath"]
    mzp = findZpMass(filename)
    return mzp

def findSignal(filelist,xschoice,lumi):
    sigfiles   = []
    sigweights = []
    for i,path in enumerate(filelist):
        sigfiles.append(ROOT.TFile(path))
        numevents   = sigfiles[i].Get('hnevents').GetBinContent(1)
        sigxs       = 1000*sigfiles[i].Get('hxs').GetBinContent(1)#converts to fb
        if xschoice:
            sigxs = xschoice
        sigweights.append(findScale(numevents,lumi,sigxs))
    return sigfiles,sigweights

def organizeSignal(filelist,xschoice,lumi):
    siginfo  = []
    sigfiles = []
    for i,path in enumerate(filelist):
        sigdict = {}
        sigfiles.append(ROOT.TFile(path))
        numevents   = sigfiles[i].Get('hnevents').GetBinContent(1)
        sigxs       = 1000*sigfiles[i].Get('hxs').GetBinContent(1)#converts to fb
        if xschoice:
            sigxs = xschoice
        sigdict["xs"] = sigxs
        sigdict["scale"] = findScale(numevents,lumi,sigxs)
        sigdict["tfile"] = ROOT.TFile(path)
        sigdict["fpath"] = path

        siginfo.append(sigdict)

    return siginfo

def organizeBkg(listbkg,lumi):#Returns a dictionary of background info
    bkginfo  = []
    bkgfiles = []
    for i,path in enumerate(listbkg):
        bkgdict = {}
        bkgfiles.append(ROOT.TFile(path))
        numbkg           = bkgfiles[i].Get('hnevents').GetBinContent(1)
        bkgxs            = 1000*bkgfiles[i].Get('hxs').GetBinContent(1)#converts to fb
        bkgscale         = findScale(numbkg,lumi,bkgxs)
        bkgdict["xs"]    = bkgxs
        bkgdict["scale"] = bkgscale
        params1          = listbkg[i].split('/')
        params2          = params1[3].split('_')
        bkgname          = params2[0]
        bkgdict["name"]  = bkgname
        bkgdict["tfile"]  = ROOT.TFile(path)
        
        bkginfo.append(bkgdict)

    bkginfo = sorted(bkginfo,key = lambda bkg:bkg["xs"])#This should put least prominent background first
    return bkginfo
        
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-mns","--NSmass",type=int,help = "NS mass of samples you want")
    parser.add_argument("-L","--lumi", type=float,default = 35.9, help = "integrated luminosity for scale in fb^-1")
    parser.add_argument("-x","--xsec", type=float,help = "desired siganl cross section in fb")
    args = parser.parse_args()
    
    
    #Lists to organize your shit
    mns        = args.NSmass
    xschoice   = args.xsec
    lum        = args.lumi
    listsig    = g.glob('analysis_output/2018-11-*/Delphes_analysis_output/ZpAnomalonHZ_Zp*_ND*_NS'+str(mns)+'*')#list of all signal files with appropraite NS mass
    cleanedl   = map(findZpMass,listsig)
    sortsig    = list(set(cleanedl))#The different Zp masses featured
    sortsig.sort()
    listbkg    = g.glob('analysis_output/2018-11-0*/Delphes_analysis_output/*_bkg*')#can put back in date thing later
    bkgcolors  = [kAzure-4,kViolet,kAzure-6,kViolet+8]
    sigcolors  = [kOrange,kOrange-3,kCyan,kCyan-6,kGreen,kGreen-6,kPink+7,kPink+4,kViolet+4,kMagenta-2,kMagenta+3]
    #sigfiles,sigweights = findSignal(listsig,xschoice,lum)
    siginfo    = organizeSignal(listsig,xschoice,lum)
    bkginfo    = organizeBkg(listbkg,lum)
    keys       = siginfo[0]["tfile"].GetListOfKeys()
    
    
    
    #build the TCanvas parameters
    numpoints = len(sortsig)
    xmlevel = 0
    ymlevel = 0
    if numpoints <= 3:
        ymlevel = 450
        xmlevel = 450*numpoints
    else:
        hori = (numpoints + numpoints%2)/2
        ymlevel = 900
        xmlevel = 450*hori

    lastCanvasdex = hori*2


    
    #Make Some Plots
    for key in keys:
        print "analyzing a new key y'all"
        hname = key.GetName()

        #Make the main canvas
        tc = ROOT.TCanvas("tc",hname,xmlevel,ymlevel)
        tc.Divide(hori,2)

        #Make the kg legend
        ROOT.gStyle.SetLegendBorderSize(0)
        leg1 = ROOT.TLegend(0,0.69,0.45,0.88)

        #Make the stack for the kg
        maxbkg = 0
        hsbkg = ROOT.THStack('hsbkg','')
        for i in range(len(bkginfo)):
            hbkg = bkginfo[i]["tfile"].Get(hname)
            hbkg.SetStats(0)
            hbkg.Scale(bkginfo[i]["scale"])
            hbkg.SetFillColor(bkgcolors[i])
            bkgmax = hbkg.GetMaximum()
            if bkgmax > maxbkg:
                maxbkg = bkgmax
                #print "max bkg is using ",maxbkg
                hbkg.SetMaximum(10000000)#maxbkg*2000)
                #print "max after setting max ",hbkg.GetMaximum()
                hbkg.SetMinimum(0.1)
                hsbkg.Add(hbkg)
                leg1.AddEntry(hbkg,bkginfo[i]["name"],"f")
                #print "just made that sweet stacked ackground"
                #print "stack max with bkg ", hsbkg.GetMaximum()

        legs = []
        for i,mass in enumerate(sortsig):#for each Zp mass point
            sigmass = []
            #print "running for Zp mass ",mass
            tc.cd(i+1)
            ROOT.gPad.SetLogy()#The pad does not have the setting
            hsbkg.SetMaximum(maxbkg*2000)
            hsbkg.SetMinimum(0.1)
            hsbkg.Draw("HIST")

            #Initialize signal legend
            legs.append(ROOT.TLegend(0.40,0.60,0.90,0.88))
            
            for j in range(len(siginfo)):
                if mass == findZpMass(siginfo[j]["fpath"]):
                    sigmass.append(siginfo[j])
            siginfo.sort(key = findNDMassFromDict)
            for k in range(len(sigmass)):
                #print "looking at ND mass ",findNDMassFromDict(sigmass[k])
                h = sigmass[k]["tfile"].Get(hname)
                h.SetLineColor(sigcolors[k])
                h.SetStats(0)
                h.Scale(sigmass[k]["scale"])
                #print "max signal sees ",maxbkg*2000
                h.SetMaximum(maxbkg*2000)
                h.SetMinimum(0.1)
                h.Draw("HISTSAME")
            
                params = sigmass[k]["fpath"].split('_')
                zpstr  = params[4]
                ndstr  = params[5]
                nsstr  = params[6]
                legs[i].AddEntry(h,zpstr+" "+ndstr+" "+nsstr+", "+str(xschoice/1000)+" pb","l")
                
                
                tc.Update()

        for i,leg in enumerate(legs):
            tc.cd(i+1)
            leg.Draw()
            tc.Update()
            
        tc.cd(lastCanvasdex)
        leg1.Draw()
        
        savdir = str(date.today())
        if not os.path.exists("analysis_output/"+savdir+"/images"):
            os.makedirs("analysis_output/"+savdir+"/images")
        pngname = "analysis_output/"+savdir+"/images/ZpALLTHEMASSES_NS"+str(mns)+"_"+hname+".png"
        tc.SaveAs(pngname)
