#This is an attempt at a pyRoot script to read and make plots from Madgraph+Delphes
#Written by Grace E. Cummings, 21 June 2018

#normal imports
import sys
import ROOT
import glob
import itertools
from math import pi, sqrt, cos

#Generally Useful things
def xsFromBanner(path):
    f = open(path,'r')
    lines = f.readlines()
    xsline = lines[-9]#switch to -10 for things W related, -9 otherwise
    if "Integrated weight" in xsline:
        xslineinfo = xsline.split()
        xs = float(xslineinfo[-1])
    else:
        xs = -99999999
    return xs

def xsandgZpFromBanner(path):
    f = open(path,'r')
    lines = f.readlines()
    xsline = lines[-9]#switch to -10 for things W related
    gZpline = lines[418]#418 for most stuff
    if "Integrated weight" in xsline:
        xslineinfo = xsline.split()
        xs = float(xslineinfo[-1])
    else:
        xsline = lines[-10]
        if "Integrated weight" in xsline:
            xslineinfo = xsline.split()
            xs = float(xslineinfo[-1])
        else:
            xs = -99999999
    if "gZp" in gZpline:
        gZplineinfo = gZpline.split()
        gZp = float(gZplineinfo[1])
    else:
        gZpline = lines[419]
        if "gZp" in gZpline:
            gZplineinfo = gZpline.split()
            gZp = float(gZplineinfo[1])
        else:
            gZp = -66666666
    return xs,gZp
            
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

def deltaR(vec1,vec2):
    v1phi = vec1.Phi()
    v2phi = vec2.Phi()
    v1eta = vec1.Eta()
    v2eta = vec2.Eta()
    dR = sqrt((v2phi-v1phi)**2+(v2eta-v1eta)**2)
    return dR

def findScale(prodnum,lumi,xsec):
    expnum = xsec*lumi
    scalefac = expnum/prodnum
    return scalefac

def make4Vector(vdict):
    v = ROOT.TLorentzVector()
    v.SetPtEtaPhiM(vdict["pt"],vdict["eta"],vdict["phi"],vdict["m"])
    return v

def make4vectorch(chain,particle):
    dic = {}
    vec = TLorentzVector()
    dic["eta"] = chain.GetLeaf("Particle.Eta").GetValue(particle)
    dic["pt"]  = chain.GetLeaf("Particle.PT").GetValue(particle)
    dic["phi"] = chain.GetLeaf("Particle.Phi").GetValue(particle)
    dic["E"]   = chain.GetLeaf("Particle.E").GetValue(particle)
    vec.SetPtEtaPhiE(dic["pt"],dic["eta"],dic["phi"],dic["E"])
    return vec

#Define functions of fill hists
def genJetFinder(num_jets,hist_f,chain):
    for jet in range(num_jets):
        jet_pt = chain.GetLeaf("GenJet.PT").GetValue(jet)
        hist_fill.Fill(jet_pt)

def jetFinder(num_jets,hist2d_fill,hist_fill,hist_mass,hist_drmu1,hist_drmu2,hist_drpassmu1,hist_drpassmu2,mu1,mu2,chain):
    ljet    = ROOT.TLorentzVector()
    jvec    = ROOT.TLorentzVector()
    jetlist = []
    numjet = 0
    ht = 0
    htwl = mu1.Pt()+mu2.Pt()
    for jet in range(num_jets):
        jetdict = {}
        jetdict["pt"]   = chain.GetLeaf("Jet.PT").GetValue(jet)
        jetdict["btag"] = chain.GetLeaf("Jet.BTag").GetValue(jet)
        jetdict["eta"]  = chain.GetLeaf("Jet.Eta").GetValue(jet)
        jetdict["phi"]  = chain.GetLeaf("Jet.Phi").GetValue(jet)
        jetdict["m"]    = chain.GetLeaf("Jet.Mass").GetValue(jet)
        jvec.SetPtEtaPhiM(jetdict["pt"],jetdict["eta"],jetdict["phi"],jetdict["m"])
        dRjetmu1 = deltaR(jvec,mu1)
        dRjetmu2 = deltaR(jvec,mu2)
        hist_drmu1.Fill(dRjetmu1)
        hist_drmu2.Fill(dRjetmu2)
        if abs(jetdict["eta"]) < 2.4 and dRjetmu1 > 0.4 and dRjetmu2 > 0.4:
            jetlist.append(jetdict)
            hist_drpassmu1.Fill(dRjetmu1)
            hist_drpassmu2.Fill(dRjetmu2)
            hist2d_fill.Fill(jetdict["pt"],jetdict["btag"])
            hist_fill.Fill(jetdict["pt"])
            hist_mass.Fill(jetdict["m"])
            ht += jetdict["pt"]
            htwl += jetdict["pt"]
    if jetlist != []:
        ljetdict = max(jetlist, key = lambda jet:jet["pt"])
        ljet.SetPtEtaPhiM(ljetdict["pt"],ljetdict["eta"],ljetdict["phi"],ljetdict["m"])
        numjet = len(jetlist)
        
    return ljet,numjet,ht,htwl
        
def fatJetFinder(num_fat,hnobtaginfo,hist_mass,hist_dr,mu1,mu2,zvec,chain):
    lfat = ROOT.TLorentzVector()
    fvec = ROOT.TLorentzVector()
    fatlist = []
    numfat = 0
    for fat in range(num_fat):
        fatdict = {}
        #There are more things in root file, can get them
        fatdict["pt"]  = chain.GetLeaf("FatJet.PT").GetValue(fat)
        fatdict["eta"] = chain.GetLeaf("FatJet.Eta").GetValue(fat)
        fatdict["phi"] = chain.GetLeaf("FatJet.Phi").GetValue(fat)
        fatdict["m"]   = chain.GetLeaf("FatJet.Mass").GetValue(fat)
        fvec.SetPtEtaPhiM(fatdict["pt"],fatdict["eta"],fatdict["phi"],fatdict["m"])
        dRfatmu1 = deltaR(fvec,mu1)
        dRfatmu2 = deltaR(fvec,mu2)
        if abs(fatdict["eta"]) < 2.4 and dRfatmu1 > 0.8 and dRfatmu2 > 0.8:#both muons out of range of jet 
            fatlist.append(fatdict)
            hnobtaginfo.Fill(fatdict["pt"])
            hist_mass.Fill(fatdict["m"])
            hist_dr.Fill(deltaR(fvec,zvec))
    if fatlist != []:
        lfatdict = max(fatlist, key = lambda fat:fat["pt"])
        lfat.SetPtEtaPhiM(lfatdict["pt"],lfatdict["eta"],lfatdict["phi"],lfatdict["m"])
        numfat = len(fatlist)
        
    return lfat,numfat
    
def genMETFinder(hist_fill,chain):
    genMET  = chain.GetLeaf("GenMissingET.MET").GetValue()
    hist_fill.Fill(genMET)

def missingETFinder(chain):
    #need to contemplate MET
    met     = chain.GetLeaf("MissingET.MET").GetValue()
    met_phi = chain.GetLeaf("MissingET.Phi").GetValue()
    met_eta = chain.GetLeaf("MissingET.Eta").GetValue()
    return met, met_phi, met_eta

def muonFinder(chain,mu_num):
    mu1 = ROOT.TLorentzVector()
    mu2 = ROOT.TLorentzVector()
    mulist = []
    for i in range(mu_num):#event this is called for should always have greater than on equal to 2
         mudict        = {}
         mudict["q"]   = chain.GetLeaf("Muon.Charge").GetValue(i)
         mudict["pt"]  = chain.GetLeaf("Muon.PT").GetValue(i)
         mudict["eta"] = chain.GetLeaf("Muon.Eta").GetValue(i)
         mudict["phi"] = chain.GetLeaf("Muon.Phi").GetValue(i)
         mudict["m"]   = 0.105 #in GeV
         mulist.append(mudict)

    mu1dict = max(mulist, key = lambda mu:mu["pt"])
    mulist.remove(mu1dict)
    mu2dict = max(mulist, key = lambda mu:mu["pt"])

    #Muons have to be opposite charge
    if mu1dict["q"] != mu2dict["q"]:
        mu1.SetPtEtaPhiM(mu1dict["pt"],mu1dict["eta"],mu1dict["phi"],mu1dict["m"])         
        mu2.SetPtEtaPhiM(mu2dict["pt"],mu2dict["eta"],mu2dict["phi"],mu2dict["m"])

    return mu1, mu2


def zFinder(mulist):
    veclist  = map(make4Vector,mulist)
    dimul    = list(itertools.combinations(veclist,2))#makes all combos of 2 muons
    zmminus  = lambda x : 90.1 - (x[0][0]+x[1][0]).M()
    masslist = map(zmminus,dimul)
    mui  = masslist.index(min(masslist))#index of pair closest to Z mass
    dimu = dimul[mui]
    mu1  = max(dimu, key = lambda x : x.Pt())
    mu2  = min(dimu, key = lambda x : x.Pt())
    
    return mu1, mu2 

def zmSubtract(dimuon):
    z = ROOT.TLorentzVector()

def zFinderQ(mulist):#Takes charge into account
    mu1 = ROOT.TLorentzVector()
    mu2 = ROOT.TLorentzVector()
    dimul =  list(itertools.combinations(mulist,2))#makes all combos of 2 muons
    goodpairs = []
    for mumu in dimul:
        if mumu[0]["q"] != mumu[1]["q"]:#if charges are different
            mumuv = map(make4Vector,mumu)#make muons four vectors
            if ((mumuv[0]+mumuv[1]).M() > 70 and (mumuv[0]+mumuv[1]).M() < 110): 
                goodpairs.append(mumuv)#append the list of the pair to a list
    if len(goodpairs) == 0:
        return mu1, mu2
    #put this in
    else:
        zmminus  = lambda x : 90.1 - (x[0]+x[1]).M()
        masslist = map(zmminus,goodpairs)
        mui  = masslist.index(min(masslist))#index of pair closest to Z mass
        dimu = goodpairs[mui]
        mu1  = max(dimu, key = lambda x : x.Pt())
        mu2  = min(dimu, key = lambda x : x.Pt())
        return mu1, mu2
        
        
    
def diMuonMass(hist_fill,chain):
    mu1, mu2= muonFinder(chain)
    dimu      = mu1+mu2
    dimu_mass = dimu.M()
    hist_fill.Fill(dimu_mass)

         
def findMt(pt,met,dphi):
    mt = sqrt(2*pt*met*(1-cos(dphi)))

    return mt

#def findMt2():
