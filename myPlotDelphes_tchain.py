#This is an attempt at a pyRoot script to read and make plots from Madgraph+Delphes
#Written by Grace E. Cummings, Summer 2018
#Started to add the ability to do everything at one time lol

#normal imports
from leptophobe_analysis import *
from ROOT import *
from math import pi,sqrt,cos,sin
from datetime import date
import os
import sys
import glob
import argparse

#Parser
parser = argparse.ArgumentParser()

#The things to access delphes classes
#Allows for easier ways to read trees, and runs without errors
ROOT.gInterpreter.AddIncludePath("/home/gecummings/fermilabrun/delphes")
ROOT.gInterpreter.AddIncludePath("/home/gecummings/fermilabrun/delphes/external/")
gROOT.ProcessLine(".L lester_mt2_bisect.h")
ROOT.gSystem.Load("~/fermilabrun/delphes/libDelphes.so")

MT2Class=asymm_mt2_lester_bisect()
MT2Class.disableCopyrightMessage()
         
if __name__=='__main__':
    parser.add_argument("-s","--signal",help = "sample directory base name")
    parser.add_argument("-o","--output",help = "output file name")
    parser.add_argument("-g","--guess",type=float,default = 200,help = "1st guess for NS mass GeV")
    args = parser.parse_args()
    
    mc_dir  = args.signal#Example: ZpAnomalon_Delphes as argument uses all dir that start with it
    outf    = args.output#name of output file
    gmass   = args.guess

    #Make list for mt2 guess
    gmasslowest  = gmass - 0.5*gmass
    gmasslow     = gmass - 0.25*gmass
    gmasshigh    = gmass + 0.25*gmass
    gmasshighest = gmass + 0.5*gmass 
    
    
    if mc_dir:
        floc = mc_dir+'/Events/run_01/'
        banpath = floc+'run_01_tag_1_banner.txt'
        inputfiles = glob.glob(mc_dir+'*/Events/run_01/tag_1_delphes_events.root')
        outfdefault = mc_dir+"_withcuts"

    print "reading LHE Level cross section"
    xs = xsFromBanner(banpath)
    print "the LHE level cross section is ",xs

    print "analyzing the sample in ",mc_dir
    ch = ROOT.TChain("Delphes")#Want to read many trees for more events
    for f in inputfiles:
        ch.Add(f)

    numevents =ch.GetEntries()
    
    #start counters
    evnt_pass_zcut = 0
    evnt_pass_fatcut = 0
    evnt_pass_jetcut = 0

    #Define TCanvases
    tc  = ROOT.TCanvas('tc','canvas with testing hist',450,450)
    #tc1 = ROOT.TCanvas('tc1','MET canvas',450,450)

    #Hists to Store crap
    hnevents = ROOT.TH1F('hnevents','number of events',1,0,1)
    hxs      = ROOT.TH1F('hxs','generated cross section',1,0,1)
    
    #Gen Level Hists
    #hgenjet_pt = ROOT.TH1F('hgenjet_pt','pt of generated, not reco jets',100,0,600)
    #hgenMET    = ROOT.TH1F('hgenMET_mass','Generated MET',100,0,1000)

    #Jet Hists
    hfatjet_pt = ROOT.TH1F('hfatjet_pt','pt of all Delphes level fat (AK8) jets per event',40,200,1200)#25 Gev Bins
    hjet_pt    = ROOT.TH1F('hjet_pt','pt of all Delphes level AK4 jets per event',40,0,1000)#25 GeV Bins, there is some cut here
    hjet_mass  = ROOT.TH1F('hjet_mass','mass of all Delphes level AK4 jets per event',15,0,150)#10 GeV Bins 
    hfat_mass  = ROOT.TH1F('hfat_mass','mass of all Delphes level AK8 jets per event',60,0,600)#10 GeV Bins
    hljet_mass = ROOT.TH1F('hljet_mass','mass of leading Delphes level AK4 jet',15,0,150)#10 GeV Bins 
    hlfat_mass = ROOT.TH1F('hlfat_mass','mass of leading Delphes level AK8 jet',60,0,600)#10 GeV Bins
    hljet_eta  = ROOT.TH1F('hljet_eta','Eta of leading AK4 jet',100,-5,5)
    hlfat_eta  = ROOT.TH1F('hlfat_eta','Eta of leading AK8 fat jet',100,-4,4)
    hjet_multi = ROOT.TH1F('hjet_multi','Jet multiplicty for AK4 jets',13,0,13)
    hfat_multi = ROOT.TH1F('hfat_multi','Fat Jet multiplicty',7,0,7)
    hjet_passmulti = ROOT.TH1F('hjet_passmulti','Passing Jet multiplicty for AK4 jets',13,0,13)
    hfat_passmulti = ROOT.TH1F('hfat_passmulti','Passing Fat Jet multiplicty',7,0,7)
    hjetbtagvpt  = ROOT.TH2F('hjetbtagvpt','pt of jet and if btagged',100,0,800,4,0,2)
    hht        = ROOT.TH1F('hht','ht of AK4 jets',104,0,2600)
    #hfatbtag_pt  = ROOT.TH1F('hfatbtag_pt','pt of all Delphes btag fat jets',200,0,1500)
       
    #MET and Z Hists
    hMET       = ROOT.TH1F('hMET','Reconstructed MET',40,0,1000)#25 GeV bins
    hMET_eta   = ROOT.TH1F('hMET_eta','MET Eta',100,-3,3)
    hdimu_mass = ROOT.TH1F('hdimu_mass','mass of dimuon',100,50,130)
    hz_pt      = ROOT.TH1F('hz_pt','pt of reconstructed Z',37,75,1000)#25 GeV bins
    hz_eta     = ROOT.TH1F('hz_eta','Z Eta',100,-6,6)
    hzptvdRmm  = ROOT.TH2F('hzptvdRmm','Delta R of muon pair vs. Z pt',38,100,1000,100,0,7)
    hzMET_mt   = ROOT.TH1F('hzMET_mt','Transverse mass of Z and MET',48,0,1200)#25 GeV bins
    hmt2g      = ROOT.TH1F('hmt2g','mt2 with missing mass guess '+str(gmass)+'  GeV',48,0,1200)#25 GeV bins
    hmt2gll    = ROOT.TH1F('hmt2gll','mt2 with missing mass guess '+str(gmasslowest)+'  GeV',48,0,1200)#25 GeV bins
    hmt2gl     = ROOT.TH1F('hmt2gl','mt2 with missing mass guess '+str(gmasslow)+'  GeV',48,0,1200)#25 GeV bins
    hmt2gh     = ROOT.TH1F('hmt2gh','mt2 with missing mass guess '+str(gmasshigh)+'  GeV',48,0,1200)#25 GeV bins
    hmt2ghh    = ROOT.TH1F('hmt2ghh','mt2 with missing mass guess '+str(gmasshighest)+'  GeV',48,0,1200)#25 GeV bins
    
    #Delta angle hists
    hdphi_Zljet   = ROOT.TH1F('hdphi_Zljet','Delta phi between Z and leading AK4 jet',100,0,3.141259)
    hdphi_ZMET    = ROOT.TH1F('hdphi_ZMET','Delta phi between Z and MET',100,0,3.141259)
    hdeta_Zljet   = ROOT.TH1F('hdeta_Zljet','Delta eta between Z and leading AK4 jet',100,0,3.141259)
    hdR_Zlfat     = ROOT.TH1F('hdR_Zlfat','Delta R between Z and leading fat jet',100,0,5)
    hdR_Zfats     = ROOT.TH1F('hdR_Zfats','Delta R between Z and all fat jets',100,0,5)
    hjetm1_alldr  = ROOT.TH1F('hjetm1_alldr','Delta R between muon 1 and all jets (no jet cuts)',100,0,5)
    hjetm2_alldr  = ROOT.TH1F('hjetm2_alldr','Delta R between muon 2 and all jets (no jet cuts)',100,0,5)
    hdR_mu1jets   = ROOT.TH1F('hdR_mu1jets','Delta R between muon 1 and all jets',100,0,5)
    hdR_mu2jets   = ROOT.TH1F('hdR_mu2jets','Delta R between muon 2 and all jets',100,0,5)
    hdR_mumu      = ROOT.TH1F('hdR_mumu','Delta R between muons',100,0,7)
    
    #Composite 4vec masses
    hzlf_mass = ROOT.TH1F('hzlf_mass','Mass of Z + leading fatjet',98,50,2500)#25 GeV bins
    hzlj_mass = ROOT.TH1F('hzlj_mass','Mass of Z + leading AK4 jet',98,50,2500)
    
    hlist = [hfatjet_pt,
             hjet_pt,    
             hjet_mass,  
             hfat_mass,  
             hljet_mass, 
             hlfat_mass, 
             hljet_eta,  
             hlfat_eta,  
             hjet_multi, 
             hfat_multi, 
             hjet_passmulti, 
             hfat_passmulti, 
             hjetbtagvpt,  
             hMET,       
             hMET_eta,   
             hdimu_mass, 
             hz_pt,      
             hz_eta,
             hzMET_mt,
             hdphi_Zljet,   
             hdphi_ZMET,    
             hdeta_Zljet,   
             hdR_Zlfat,     
             hdR_Zfats,     
             hjetm1_alldr,  
             hjetm2_alldr,  
             hdR_mu1jets,   
             hdR_mu2jets,   
             hzlf_mass,
             hzlj_mass,
             hdR_mumu,
             hzptvdRmm,
             hmt2g,
             hmt2gll,
             hmt2gl,
             hmt2gh,
             hmt2ghh,
             hht]
    
    #Loop over all events in TChain
    for i, event in enumerate(ch):
        if i % 1000 == 0: print "reading event "+str(i)

        #analysis
        mus_evnt  = ch.Muon.GetEntries()#number of muons per event
        gjts_evnt = ch.GenJet.GetEntries()#num of gen jets per event
        jts_evnt  = ch.Jet.GetEntries()
        fat_evnt  = ch.FatJet.GetEntries()#num fat jets per event
        
        if mus_evnt > 1:
            #mu1 is highest pt muon, mu2 is subleading muon
            mu1, mu2 = muonFinder(ch,mus_evnt)
            if( mu1.M() or mu2.M()) == 0:#If for some reason the leading muons have same charge, go to next event. Need better fix
                print "AHHHH SAME CHARGE MUONS"
                continue
            if mu1.Pt() > 60 and mu2.Pt() > 20 and abs(mu1.Eta()) < 2.4 and abs(mu1.Eta()) < 2.4:
                zreco = mu1 + mu2
                zpt = zreco.Pt()
                if zpt >100:#Cut on Zpt
                    zmass = zreco.M()
                    hjet_multi.Fill(jts_evnt)
                    hfat_multi.Fill(fat_evnt)
                    evnt_pass_zcut += 1
                    if fat_evnt > 0:#Have to have at least one fat jet
                        lfat,numfat = fatJetFinder(fat_evnt,hfatjet_pt,hfat_mass,hdR_Zfats,mu1,mu2,zreco,ch)
                        if lfat.M() != 0:#Has a Jet that passed the eta cut
                            evnt_pass_fatcut += 1
                            hfat_passmulti.Fill(numfat)
                            fateta = lfat.Eta()
                            hlfat_eta.Fill(fateta)
                            hlfat_mass.Fill(lfat.M())
                            #compostie 4 vector manipulations
                            zf = zreco + lfat
                            hzlf_mass.Fill(zf.M())
                            dRZlfat = deltaR(zreco,lfat)
                            hdR_Zlfat.Fill(dRZlfat)
                            #MET manipulations
                            met, metphi, meteta = missingETFinder(ch)
                            metpx = met*cos(metphi)
                            metpy = met*sin(metphi)
                            dphiZMET = abs(zreco.Phi()-metphi)
                            #z manipulations
                            hz_pt.Fill(zpt)
                            hz_eta.Fill(zreco.Eta())
                            #muon manipulations
                            dRmumu = deltaR(mu1,mu2)
                            hdR_mumu.Fill(dRmumu)
                            hzptvdRmm.Fill(zpt,dRmumu)
                            #Transverse mass z and MET
                            mt = findMt(zpt,met,dphiZMET)
                            hzMET_mt.Fill(mt)
                            
                            if jts_evnt != 0:
                                ljet,numjet,ht = jetFinder(jts_evnt,hjetbtagvpt,hjet_pt,hjet_mass,hjetm1_alldr,hjetm2_alldr,hdR_mu1jets,hdR_mu2jets,mu1,mu2,ch)
                                if ljet.M() != 0:#if passed jet cut
                                    evnt_pass_jetcut +=1
                                    hjet_passmulti.Fill(numjet)
                                    jeteta = ljet.Eta()
                                    hljet_eta.Fill(jeteta)
                                    hljet_mass.Fill(ljet.M())
                                    zl = zreco +ljet
                                    hzlj_mass.Fill(zl.M())
                                    dphiZlj  = abs(zreco.Phi()-ljet.Phi())
                                    detaZlj  = abs(zreco.Eta()-jeteta)
                                    hht.Fill(ht)
                        
                        
                            if dphiZMET > pi:
                                dphiZMET = 2*pi-dphiZMET
                            if dphiZlj > pi:
                                dphiZlj = 2*pi-dphiZlj

                            #Fill Histograms
                            hdphi_ZMET.Fill(dphiZMET)
                            hdphi_Zljet.Fill(dphiZlj)
                            hdeta_Zljet.Fill(detaZlj)
                            hMET.Fill(met)
                            hMET_eta.Fill(meteta)
                            hdimu_mass.Fill(zmass)

                            #mt2, hopefully
                            mt2g = MT2Class.get_mT2(zreco.M(),zreco.Px(),zreco.Py(),lfat.M(),lfat.Px(),lfat.Py(),metpx,metpy,gmass,gmass,0)
                            mt2gll = MT2Class.get_mT2(zreco.M(),zreco.Px(),zreco.Py(),lfat.M(),lfat.Px(),lfat.Py(),metpx,metpy,gmasslowest,gmasslowest,0)
                            mt2gl  = MT2Class.get_mT2(zreco.M(),zreco.Px(),zreco.Py(),lfat.M(),lfat.Px(),lfat.Py(),metpx,metpy,gmasslow,gmasslow,0)
                            mt2gh  = MT2Class.get_mT2(zreco.M(),zreco.Px(),zreco.Py(),lfat.M(),lfat.Px(),lfat.Py(),metpx,metpy,gmasshigh,gmasshigh,0)
                            mt2ghh = MT2Class.get_mT2(zreco.M(),zreco.Px(),zreco.Py(),lfat.M(),lfat.Px(),lfat.Py(),metpx,metpy,gmasshighest,gmasshighest,0)
                            hmt2g.Fill(mt2g)
                            hmt2gll.Fill(mt2gll)
                            hmt2gl.Fill(mt2gl)
                            hmt2gh.Fill(mt2gh)
                            hmt2ghh.Fill(mt2ghh)

    #making output files
    savdir = str(date.today())+"/Delphes_analysis_output/"
    if not os.path.exists("analysis_output/"+savdir):
        os.makedirs("analysis_output/"+savdir)
    if outf:
        output = ROOT.TFile("analysis_output/"+savdir+outf,"RECREATE")
    else:
        outname = outfdefault+'_'+str(numevents)+'Events.root'
        output = ROOT.TFile("analysis_output/"+savdir+outname,"RECREATE")

    tc.cd()
    hht.Draw()
    #hmt2g.Draw()
    #hmt2g.SetLineColor(1)
    #hmt2gll.Draw("SAME")
    #hmt2gll.SetLineColor(2)
    #hmt2gl.Draw("SAME")
    #hmt2gl.SetLineColor(3)
    #hmt2gh.Draw("SAME")
    #hmt2gh.SetLineColor(4)
    #hmt2ghh.Draw("SAME")
    #hmt2ghh.SetLineColor(6)
    tc.SetLogy()
    #hjetbtagvpt.Draw()
    #hz_pt.Draw()
    tc.Update()
    #tc1.cd()
    #hMET.Draw()
    #tc1.Update()

    hnevents.SetBinContent(1,numevents)
    hnevents.Write()
    hxs.SetBinContent(1,xs)
    hxs.Write()
    
    #The saved results
    for hist in hlist:
        hist.Write()

    print "number of dilepton containing events, with Zpt > 100 GeV: ",evnt_pass_zcut
    print "number of legit fat jet events, with Zpt > 100 GeV: ",evnt_pass_fatcut
    print "number of legit jet events, with Zpt > 100 GeV: ",evnt_pass_jetcut
    print "hists saved in ",output
    print "hit Enter to exit"
    
    sys.stdin.readline()#Keeps canvas open
        
    output.Close()
