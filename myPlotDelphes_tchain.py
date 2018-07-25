#This is an attempt at a pyRoot script to read and make plots from Madgraph+Delphes
#Written by Grace E. Cummings, 21 June 2018
#Started to add the ability to do everything at one time lol

#normal imports
from leptophobe_analysis import *
from math import pi
from datetime import date
import sys
import ROOT
import glob
import argparse

#Parser
parser = argparse.ArgumentParser()

#The things to access delphes classes
#Allows for easier ways to read trees, and runs without errors
ROOT.gInterpreter.AddIncludePath("/home/gecummings/fermilabrun/delphes")#/classes/")
ROOT.gInterpreter.AddIncludePath("/home/gecummings/fermilabrun/delphes/external/")#ExRootAnalysis/")
ROOT.gSystem.Load("~/fermilabrun/delphes/libDelphes.so")
         
if __name__=='__main__':
    parser.add_argument("-s","--signal",help = "signal sample directory base name")
    parser.add_argument("-b","--bkg", help = "background samply directory base name")
    parser.add_argument("-o","--output",help = "output file name")
    args = parser.parse_args()
    
    mc_dir  = args.signal#Example: ZpAnomalon_Delphes as argument uses all dir that start with it
    bkg_dir = args.bkg
    outf    = args.output#name of output file
    
    if mc_dir:
        #inputfiles = [mc_dir+'/Events/run_01/tag_1_delphes_events.root']#Just to make one file
        inputfiles = glob.glob(mc_dir+'*/Events/run_01/tag_1_delphes_events.root')
        #outfdefault = "myPlotDelphes_sig_output_withcuts.root"
        print "analyzing the signal sample in ",mc_dir
    if bkg_dir:
        inputfiles = glob.glob(bkg_dir+'*/Events/run_01/tag_1_delphes_events.root')
        outfdefault = "myPlotDelphes_bkg_output_withcuts.root"
        print "analyzing the background sample in ",bkg_dir
        
    ch = ROOT.TChain("Delphes")#Want to read many trees for more events
    for f in inputfiles:
        ch.Add(f)

    #start counters
    evnt_pass = 0

    #Define TCanvases
    tc  = ROOT.TCanvas('tc','canvas with testing hist',450,450)
    #tc1 = ROOT.TCanvas('tc1','MET canvas',450,450)
    
    #Gen Level Hists
    hgenjet_pt = ROOT.TH1F('hgenjet_pt','pt of generated, not reco jets',100,0,600)
    hgenMET    = ROOT.TH1F('hgenMET_mass','Generated MET',100,0,1000)

    #Jet Hists
    hfatjet_pt = ROOT.TH1F('hfatjet_pt','pt of fat jets',200,200,800)
    hfatbtag_pt= ROOT.TH1F('hfatbtag_pt','pt of btag fat jets',200,0,1500)
    hjet_pt    = ROOT.TH1F('hjet_pt','pt of reco jets',200,0,800)
    hjetbtagvpt= ROOT.TH2F('hjetbtagvpt','pt of jet and if btagged',100,0,800,4,0,2)
    #hfatjet_pt.SetMinimum(.1)
    #hjet_pt.SetMinimum(.1)
    
    #MET and Z Hists
    hMET       = ROOT.TH1F('hMET','Reconstructed MET',100,0,1000)
    hdphi_ZMET = ROOT.TH1F('hdphi_ZMET','Delta phi between Z and MET',100,0,3.25)
    hMET_eta   = ROOT.TH1F('hMET_eta','MET Eta',100,-6,6)
    hdimu_mass = ROOT.TH1F('hdimu_mass','mass of dimuon',100,50,130)
    hz_pt      = ROOT.TH1F('hz_pt','pt of reconstructed Z',100,90,800)
    #hMET.SetMinimum(.1)
    #hz_pt.SetMinimum(.1)
    
    hlist = [hfatjet_pt,hjet_pt,hjetbtagvpt,hMET,hdphi_ZMET,hMET_eta,hdimu_mass,hz_pt,hgenMET]
    
    #Loop over all events in TChain
    for i, event in enumerate(ch):
        if i % 1000 == 0: print "reading event "+str(i)

        #analysis
        mus_evnt  = ch.Muon.GetEntries()#number of muons per event
        gjts_evnt = ch.GenJet.GetEntries()#num of gen jets per event
        jts_evnt  = ch.Jet.GetEntries()
        fat_evnt  = ch.FatJet.GetEntries()#num fat jets per event
        genMETFinder(hgenMET,ch)
        
        if mus_evnt == 2:#Z -> mu ~mu, better be two
            mu1, mu2 = muonFinder(ch)
            zreco = mu1 + mu2
            zpt = zreco.Pt()
            if zpt >100:#Cut on Zpt
                evnt_pass += 1                
                fatJetFinder(fat_evnt,hfatjet_pt,hfatbtag_pt,ch)
                jetFinder(jts_evnt,hjetbtagvpt,hjet_pt,ch)
                hz_pt.Fill(zpt)
                zmass = zreco.M()
                met, metphi, meteta = missingETFinder(ch)
                dphiZMET = abs(zreco.Phi()-metphi)
                if dphiZMET > pi:
                    dphiZMET = 2*pi-dphiZMET               

                #Fill Histograms
                hdphi_ZMET.Fill(dphiZMET)
                hMET.Fill(met)
                hMET_eta.Fill(meteta)
                hdimu_mass.Fill(zmass)

    #making output files
    savdir = str(date.today())
    if outf:
        output = ROOT.TFile("analysis_output/"+savdir+"/Delphes_analysis_output/"+outf,"RECREATE")
    else:
        output = ROOT.TFile("analysis_output/"+savdir+"/Delphes_analysis_output/"+outfdefault,"RECREATE")

    tc.cd()
    hMET.Draw()
    #hjetbtagvpt.Draw()
    #hz_pt.Draw()
    tc.Update()
    #tc1.cd()
    #hMET.Draw()
    #tc1.Update()

    #The saved results
    for hist in hlist:
        hist.Write()
    
    print "number of dilepton containing events, with Zpt > 100 GeV: ",evnt_pass
    print "hists saved in ",output
    print "hit Enter to exit"
    
    sys.stdin.readline()#Keeps canvas open
        
    output.Close()
