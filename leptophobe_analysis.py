#This is an attempt at a pyRoot script to read and make plots from Madgraph+Delphes
#Written by Grace E. Cummings, 21 June 2018

#normal imports
import sys
import ROOT
import glob
from math import pi, sqrt

#Define functions of fill hists
def genJetFinder(num_jets,hist_f,chain):
    for jet in range(num_jets):
        jet_pt = chain.GetLeaf("GenJet.PT").GetValue(jet)
        hist_fill.Fill(jet_pt)


def deltaR(vec1,vec2):
    v1phi = vec1.Phi()
    v2phi = vec2.Phi()
    v1eta = vec1.Eta()
    v2eta = vec2.Eta()
    dR = sqrt((v2phi-v1phi)**2+(v2eta-v1eta)**2)

    return dR

def jetFinder(num_jets,hist2d_fill,hist_fill,hist_mass,chain):
    ljet    = ROOT.TLorentzVector()
    jetlist = []
    numjet = 0
    for jet in range(num_jets):
        jetdict = {}
        jetdict["pt"]   = chain.GetLeaf("Jet.PT").GetValue(jet)
        jetdict["btag"] = chain.GetLeaf("Jet.BTag").GetValue(jet)
        jetdict["eta"]  = chain.GetLeaf("Jet.Eta").GetValue(jet)
        jetdict["phi"]  = chain.GetLeaf("Jet.Phi").GetValue(jet)
        jetdict["m"]    = chain.GetLeaf("Jet.Mass").GetValue(jet)
        if abs(jetdict["eta"]) < 2.4:
            jetlist.append(jetdict)
            hist2d_fill.Fill(jetdict["pt"],jetdict["btag"])
            hist_fill.Fill(jetdict["pt"])
            hist_mass.Fill(jetdict["m"])
    if jetlist != []:
        ljetdict = max(jetlist, key = lambda jet:jet["pt"])
        ljet.SetPtEtaPhiM(ljetdict["pt"],ljetdict["eta"],ljetdict["phi"],ljetdict["m"])
        numjet = len(jetlist)
        
    return ljet,numjet
        
def fatJetFinder(num_fat,hnobtaginfo,hist_mass,hist_dr,zvec,chain):
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
        if abs(fatdict["eta"]) < 2.4 and deltaR(fvec,zvec) > 0.8:#Z out of range of jet 
            fatlist.append(fatdict)
            hnobtaginfo.Fill(fatdict["pt"])
            hist_mass.Fill(fatdict["m"])
            hist_dr.Fill(deltaR(fvec,zvec))
    if fatlist != []:
        lfatdict = max(fatlist, key = lambda fat:fat["pt"])
        lfat.SetPtEtaPhiM(lfatdict["pt"],lfatdict["eta"],lfatdict["phi"],lfatdict["m"])
        numfat = len(fatlist)
        
    return lfat,numfat

#def fatFinder2(numfat,histpt,histmass,zvec,chain):
#    lfat = ROOT.TLorentzVector()
#    fatlist = []
#    passfat  = 0
#    for fat in range(numfat):
        


    
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
             
def diMuonMass(hist_fill,chain):
    mu1, mu2= muonFinder(chain)
    dimu      = mu1+mu2
    dimu_mass = dimu.M()
    hist_fill.Fill(dimu_mass)

         
