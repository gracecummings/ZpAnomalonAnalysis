#This is an attempt at a pyRoot script to read and make plots from Madgraph+Delphes
#Written by Grace E. Cummings, 21 June 2018

#normal imports
import sys
import ROOT
import glob
from math import pi

#Define functions of fill hists
def genJetFinder(num_jets,hist_f,chain):
    for jet in range(num_jets):
        jet_pt = chain.GetLeaf("GenJet.PT").GetValue(jet)
        hist_fill.Fill(jet_pt)

def jetFinder(num_jets,hist2d_fill,hist_fill,chain):
    for jet in range(num_jets):
        jet_pt   = chain.GetLeaf("Jet.PT").GetValue(jet)
        jet_btag = chain.GetLeaf("Jet.BTag").GetValue(jet)
        hist2d_fill.Fill(jet_pt,jet_btag)
        hist_fill.Fill(jet_pt)
        
def fatJetFinder(num_fat,hnobtaginfo,hbtaginfo,chain):
    for fat in range(num_fat):
        fat_pt = chain.GetLeaf("FatJet.PT").GetValue(fat)
        hnobtaginfo.Fill(fat_pt)

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

    mu1dict = max(mulist)
    mu1.SetPtEtaPhiM(mu1dict["pt"],mu1dict["eta"],mu1dict["phi"],mu1dict["m"])
    mulist = mulist.remove(mu1dict)
    mu2dict = max(mulist)
    mu2.SetPtEtaPhiM(mu2dict["pt"],mu2dict["eta"],mu2dict["phi"],mu2dict["m"])
         
#         if i == 0:
#             mu1.SetPtEtaPhiM(mu_list[i]["pt"],mu_list[i]["eta"],mu_list[i]["phi"],mu_list[i]["m"])
#         elif:
#             if mu_list[i]["pt"] > mu_list[i-1]["pt"]:
#                 mu1.SetPtEtaPhiM(mu_list[i]["pt"],mu_list[i]["eta"],mu_list[i]["phi"],mu_list[i]["m"])
#                 mu2.SetPtEtaPhiM(mu_list[i-1]["pt"],mu_list[i-1]["eta"],mu_list[i-1]["phi"],mu_list[-1]["m"])
##         if mu_pt > lead_pt:#This is currently broken, will not do anything if both muons have pt greater than leading cut
#              mu1.SetPtEtaPhiM(mu_pt,mu_eta,mu_phi,mu_mass)
#         elif mu_pt >sublead_pt:
#              mu2.SetPtEtaPhiM(mu_pt,mu_eta,mu_phi,mu_mass)
#         else:
#             print "You have funky muons with non-standard charge"
#
    return mu1, mu2
             
def diMuonMass(hist_fill,chain):
    mu1, mu2= muonFinder(chain)
    dimu      = mu1+mu2
    dimu_mass = dimu.M()
    hist_fill.Fill(dimu_mass)

         
