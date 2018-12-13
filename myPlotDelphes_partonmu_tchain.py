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
    xs,gzp = xsandgZpFromBanner(banpath)
    print "the LHE level cross section is ",xs
    print "the Zp coupling is ",gzp

    print "analyzing the sample in ",mc_dir
    ch = ROOT.TChain("Delphes")#Want to read many trees for more events
    for f in inputfiles:
        ch.Add(f)

    numevents =ch.GetEntries()
    
    #start counters
    zpcounter = 0
    poorzp = 0
    evnt_pass_munumcut = 0
    evnt_pass_muchcut = 0
    evnt_pass_mukincut = 0
    evnt_pass_zcut = 0
    evnt_pass_fatnumcut = 0
    evnt_pass_fatetacut = 0
    evnt_pass_jetnumcut = 0
    evnt_pass_jetetacut = 0
    evnt_pass_gmunumcut = 0
    evnt_pass_gmuchcut  = 0
    evnt_pass_gmuptcut  = 0
    evnt_pass_gmuetacut = 0
    #Define TCanvases
    tc  = ROOT.TCanvas('tc','canvas with testing hist',450,450)
    #tc1 = ROOT.TCanvas('tc1','MET canvas',450,450)

    #Hists to Store crap
    hnevents  = ROOT.TH1F('hnevents','number of events',1,0,1)
    hxs       = ROOT.TH1F('hxs','generated cross section',1,0,1)
    hgzp      = ROOT.TH1F('hgzp','gZp',1,0,1)
    hmuetacut = ROOT.TH1F('hmuetacut','events passing muon eta requirement',1,0,1)
    hgmunumcut = ROOT.TH1F('hmunumcut','events passing muon number requirement',1,0,1)
    hgmuptcut  = ROOT.TH1F('hmuptcut','events passing muon pt requirement',1,0,1)
    hgmuqcut   = ROOT.TH1F('hmuqcut','events passing muon charge requirement',1,0,1)
    hzptcut   = ROOT.TH1F('hzptcutut','events passing zpt requirement',1,0,1)
    hfatnumcut= ROOT.TH1F('hfatnumcut','events passing fat jet number requirement',1,0,1)
    hfatetacut= ROOT.TH1F('hfatetacut','events passing fat jet eta requirement',1,0,1)
    
    #Gen Level Hists
    #hgenjet_pt = ROOT.TH1F('hgenjet_pt','pt of generated, not reco jets',100,0,600)
    #hgenMET    = ROOT.TH1F('hgenMET_mass','Generated MET',100,0,1000)
    hgenzp_pt   = ROOT.TH1F('hgenzp_pt','Generated Zp pt',100,0,600)
    hgenzp_mass = ROOT.TH1F('hgenzp_mass','Generated Zp Mass',500,900,2100)

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
    hhtwl      = ROOT.TH1F('hhtwl','ht of AK4 jets and leptons',104,0,2600)
    #hfatbtag_pt  = ROOT.TH1F('hfatbtag_pt','pt of all Delphes btag fat jets',200,0,1500)
       
    #MET and Z Hists
    hMET       = ROOT.TH1F('hMET','Reconstructed MET',100,0,1000)#10 GeV bins
    hMET_eta   = ROOT.TH1F('hMET_eta','MET Eta',100,-3,3)
    hdimu_mass = ROOT.TH1F('hdimu_mass','mass of dimuon',100,50,130)
    hz_pt      = ROOT.TH1F('hz_pt','pt of reconstructed Z',93,70,1000)#10 GeV bins
    hdz_pt     = ROOT.TH1F('hzd_pt','pt of reconstructed delphes level Z',93,70,1000)#10 GeV bins
    hz_eta     = ROOT.TH1F('hz_eta','Z Eta',100,-6,6)
    hzptvdRmm  = ROOT.TH2F('hzptvdRmm','Delta R of muon pair vs. Z pt',38,100,1000,100,0,7)
    hzMET_mt   = ROOT.TH1F('hzMET_mt','Transverse mass of Z and MET',120,0,1200)#10 GeV bins
    hmt2g      = ROOT.TH1F('hmt2g','mt2 with missing mass guess '+str(gmass)+'  GeV',130,0,1300)#10 GeV bins
    hmt2gll    = ROOT.TH1F('hmt2gll','mt2 with missing mass guess '+str(gmasslowest)+'  GeV',130,0,1300)#10 GeV bins
    hmt2gl     = ROOT.TH1F('hmt2gl','mt2 with missing mass guess '+str(gmasslow)+'  GeV',130,0,1300)#10 GeV bins
    hmt2gh     = ROOT.TH1F('hmt2gh','mt2 with missing mass guess '+str(gmasshigh)+'  GeV',130,0,1300)#10 GeV bins
    hmt2ghh    = ROOT.TH1F('hmt2ghh','mt2 with missing mass guess '+str(gmasshighest)+'  GeV',130,0,1300)#10 GeV bins
    
    #Delta angle hists
    hdphi_Zljet   = ROOT.TH1F('hdphi_Zljet','Delta phi between Z and leading AK4 jet',100,0,3.141259)
    hdphi_ZMET    = ROOT.TH1F('hdphi_ZMET','Delta phi between Z and MET',100,0,3.141259)
    hdphi_hZMET   = ROOT.TH1F('hdphi_hZMET','Delta phi between Z+higgs and MET',100,0,3.141259)
    hdphi_Zlfjet  = ROOT.TH1F('hdphi_Zlfjet','Delta phi between Z and leading AK8 jet',100,0,3.141259)
    hdeta_Zljet   = ROOT.TH1F('hdeta_Zljet','Delta eta between Z and leading AK4 jet',100,0,3.141259)
    hdeta_Zlfjet  = ROOT.TH1F('hdeta_Zlfjet','Delta eta between Z and leading AK8 jet',100,0,3.141259)
    hdR_Zlfat     = ROOT.TH1F('hdR_Zlfat','Delta R between Z and leading fat jet',100,0,5)
    hdR_Zfats     = ROOT.TH1F('hdR_Zfats','Delta R between Z and all fat jets',100,0,5)
    hjetm1_alldr  = ROOT.TH1F('hjetm1_alldr','Delta R between muon 1 and all jets (no jet cuts)',100,0,5)
    hjetm2_alldr  = ROOT.TH1F('hjetm2_alldr','Delta R between muon 2 and all jets (no jet cuts)',100,0,5)
    hdR_mu1jets   = ROOT.TH1F('hdR_mu1jets','Delta R between muon 1 and all jets',100,0,5)
    hdR_mu2jets   = ROOT.TH1F('hdR_mu2jets','Delta R between muon 2 and all jets',100,0,5)
    hdR_mumu      = ROOT.TH1F('hdR_mumu','Delta R between muons',100,0,7)
    
    #Composite 4vec masses
    hzlf_mass = ROOT.TH1F('hzlf_mass','Mass of Z + leading fatjet',245,50,2500)#10 GeV bins
    hzlj_mass = ROOT.TH1F('hzlj_mass','Mass of Z + leading AK4 jet',245,50,2500)
    
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
             hdz_pt,
             hz_eta,
             hzMET_mt,
             hdphi_Zljet,
             hdphi_Zlfjet,   
             hdphi_ZMET,
             hdphi_hZMET,    
             hdeta_Zljet,
             hdeta_Zlfjet,   
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
             hhtwl,
             hht,
             hgenzp_pt,
             hgenzp_mass,
             ]

    #Loop over all events in TChain
    for i, event in enumerate(ch):
        mus_evnt = ch.Muon.GetEntries()
        genmuperevent = 0
        genzpperevent = 0
        if mus_evnt > 1:
            dmu1, dmu2 = muonFinder(ch,mus_evnt)
            #if ( dmu1.M() or dmu2.M()) == 0:
            #    continue
            if dmu1.Pt() > 60 and dmu2.Pt() > 20 and abs(dmu1.Eta()) < 2.4 and abs(dmu1.Eta()) < 2.4:
                dz = dmu1 + dmu2
                dzpt = dz.Pt()
                if dzpt > 100:
                    hdz_pt.Fill(dzpt)
        
        if i % 1000 == 0:
            print "reading event "+str(i)
        #parton level muons
        parts_evnt = ch.Particle.GetEntries()
        gmu1 = TLorentzVector()
        gmu2 = TLorentzVector()
        gmulist = []
        goodmu = 0
        zpfound = 0
        for p in range(parts_evnt):
            pid   = ch.GetLeaf("Particle.PID").GetValue(p)
            pstat = ch.GetLeaf("Particle.Status").GetValue(p)
            
            #print "pid: ",pid
            #print "status: ",pstat
            if abs(pid) == 13:
                if pstat == 1:
                    genmuperevent += 1
                    gmudict = {}
                    gmudict["eta"] = ch.GetLeaf("Particle.Eta").GetValue(p)
                    gmudict["pt"]  = ch.GetLeaf("Particle.PT").GetValue(p)
                    if (abs(gmudict["eta"]) < 2.4 and gmudict["pt"] > 20): 
                        gmudict["q"]   = ch.GetLeaf("Particle.Charge").GetValue(p)
                        gmudict["phi"] = ch.GetLeaf("Particle.Phi").GetValue(p)
                        gmudict["m"]   = 0.105 #in GeV
                        gmulist.append(gmudict)
                        goodmu += 1
            if abs(pid) == 9906663:#This is the madgraph level
                genzpperevent += 1
                #print "Zp status ",pstat
                zpfound = 1
                if pstat == 44:
                    zpcounter += 1
                    zpdict = {}
                    zp = TLorentzVector()
                    zpdict["eta"] = ch.GetLeaf("Particle.Eta").GetValue(p)
                    zpdict["pt"]  = ch.GetLeaf("Particle.PT").GetValue(p)
                    zpdict["q"]   = ch.GetLeaf("Particle.Charge").GetValue(p)
                    zpdict["phi"] = ch.GetLeaf("Particle.Phi").GetValue(p)
                    zpdict["E"]   = ch.GetLeaf("Particle.E").GetValue(p)
                    hgenzp_pt.Fill(zpdict["pt"])
                    zp.SetPtEtaPhiE(zpdict["pt"],zpdict["eta"],zpdict["phi"],zpdict["E"])
                    hgenzp_mass.Fill(zp.M())
                    zpfound = 1
                if pstat == (44 or 62):
                    zpfound = 1
        if zpfound == 0:
            print "non  intermediate zp found in event ",i
            poorzp += 1
        #print "muons in event ",genmuperevent
        #print "Zp per event ",genzpperevent
        if goodmu > 0:
            evnt_pass_gmuetacut +=1
            
        if len(gmulist) > 1:
            evnt_pass_gmunumcut +=1
            gmu1, gmu2 = zFinderQ(gmulist)#finds the muon combo that has opposite charge and is closest to Z mass
            if (gmu1.M() and gmu2.M()) != 0:
                evnt_pass_gmuchcut +=1
            else:
                #print "AHH, same charge muons"
                continue
            if gmu1.Pt() > 60 and gmu2.Pt() > 20:
                evnt_pass_gmuptcut +=1
            

                jts_evnt  = ch.Jet.GetEntries()
                fat_evnt  = ch.FatJet.GetEntries()#num fat jets per event
                zreco = gmu1 + gmu2
                zpt = zreco.Pt()
                if zpt >100:#Cut on Zpt
                    zmass = zreco.M()
                    hjet_multi.Fill(jts_evnt)
                    hfat_multi.Fill(fat_evnt)
                    evnt_pass_zcut += 1
                    if fat_evnt > 0:#Have to have at least one fat jet
                        lfat,numfat = fatJetFinder(fat_evnt,hfatjet_pt,hfat_mass,hdR_Zfats,gmu1,gmu2,zreco,ch)
                        evnt_pass_fatnumcut += 1
                        if lfat.M() != 0:#Has a Jet that passed the eta cut
                            evnt_pass_fatetacut += 1
                            hfat_passmulti.Fill(numfat)
                            fateta = lfat.Eta()
                            hlfat_eta.Fill(fateta)
                            hlfat_mass.Fill(lfat.M())
                            fatphi = lfat.Phi()
                            dphiZlfat = abs(zreco.Phi()-fatphi)
                            detaZlfat = abs(zreco.Eta()-fateta)
                            #composite 4 vector manipulations
                            zf = zreco + lfat
                            hzlf_mass.Fill(zf.M())
                            dRZlfat = deltaR(zreco,lfat)
                            hdR_Zlfat.Fill(dRZlfat)
                            #MET manipulations
                            met, metphi, meteta = missingETFinder(ch)
                            metpx = met*cos(metphi)
                            metpy = met*sin(metphi)
                            dphiZMET = abs(zreco.Phi()-metphi)
                            dphihZMET = abs((zreco+lfat).Phi()-metphi)
                            hdphi_hZMET.Fill(dphihZMET)
                            #z manipulations
                            hz_pt.Fill(zpt)
                            hz_eta.Fill(zreco.Eta())
                            #muon manipulations
                            dRmumu = deltaR(gmu1,gmu2)
                            hdR_mumu.Fill(dRmumu)
                            hzptvdRmm.Fill(zpt,dRmumu)
                            #Transverse mass z and MET
                            mt = findMt(zpt,met,dphiZMET)
                            hzMET_mt.Fill(mt)
                            
                            if jts_evnt != 0:
                                evnt_pass_jetnumcut += 1
                                ljet,numjet,ht,htwl = jetFinder(jts_evnt,hjetbtagvpt,hjet_pt,hjet_mass,hjetm1_alldr,hjetm2_alldr,hdR_mu1jets,hdR_mu2jets,gmu1,gmu2,ch)
                                if ljet.M() != 0:#if passed jet cut
                                    evnt_pass_jetetacut +=1
                                    hjet_passmulti.Fill(numjet)
                                    jeteta = ljet.Eta()
                                    hljet_eta.Fill(jeteta)
                                    hljet_mass.Fill(ljet.M())
                                    zl = zreco +ljet
                                    hzlj_mass.Fill(zl.M())
                                    dphiZlj  = abs(zreco.Phi()-ljet.Phi())
                                    detaZlj  = abs(zreco.Eta()-jeteta)
                                    hht.Fill(ht)
                                    hhtwl.Fill(htwl)
                        
                        
                            if dphiZMET > pi:
                                dphiZMET = 2*pi-dphiZMET
                            if dphiZlj > pi:
                                dphiZlj = 2*pi-dphiZlj
                            if dphiZlfat >pi:
                                dphiZlfat = 2*pi-dphiZlfat
                                                    
                            #Fill Histograms
                            hdphi_ZMET.Fill(dphiZMET)
                            hdphi_Zljet.Fill(dphiZlj)
                            hdphi_Zlfjet.Fill(dphiZlfat)
                            hdeta_Zljet.Fill(detaZlj)
                            hdeta_Zlfjet.Fill(detaZlfat)
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
        outname = outfdefault+'partonmu_'+str(numevents)+'Events.root'
        output = ROOT.TFile("analysis_output/"+savdir+outname,"RECREATE")

    leg = ROOT.TLegend(0.45,0.60,0.90,0.88)
        
    tc.cd()
    #hht.Draw()
    hmt2g.SetStats(0)
    mt2max = hmt2g.GetMaximum()
    hmt2g.SetMaximum(mt2max*100)
    hmt2g.SetMinimum(0.1)
    hmt2g.Draw()
    hmt2g.SetLineColor(1)
    leg.AddEntry(hmt2g,"missing mass guess "+str(gmass),"l")
    hmt2gll.Draw("SAME")
    hmt2gll.SetLineColor(2)
    leg.AddEntry(hmt2gll,"missing mass guess "+str(gmasslowest),"l")
    hmt2gl.Draw("SAME")
    hmt2gl.SetLineColor(3)
    leg.AddEntry(hmt2gl,"missing mass guess "+str(gmasslow),"l")    
    hmt2gh.Draw("SAME")
    hmt2gh.SetLineColor(4)
    leg.AddEntry(hmt2gh,"missing mass guess "+str(gmasshigh),"l")
    hmt2ghh.Draw("SAME")
    hmt2ghh.SetLineColor(6)
    leg.AddEntry(hmt2ghh,"missing mass guess "+str(gmasshighest),"l")
    tc.SetLogy()
    #hjetbtagvpt.Draw()
    #hz_pt.Draw()
    leg.SetBorderSize(0)
    leg.Draw()
    tc.Update()
    #tc1.cd()
    #hMET.Draw()
    #tc1.Update()
    #tc.SaveAS("analysis_output/"+savdir+outfdefault+"_mt2guess.png")

    hnevents.SetBinContent(1,numevents)
    hnevents.Write()
    hxs.SetBinContent(1,xs)
    hxs.Write()
    hgzp.SetBinContent(1,gzp)
    hgzp.Write()
    hmuetacut.SetBinContent(1,evnt_pass_gmuetacut)
    hmuetacut.Write()
    hgmunumcut.SetBinContent(1,evnt_pass_gmunumcut)
    hgmunumcut.Write()
    hgmuptcut.SetBinContent(1,evnt_pass_gmuptcut)
    hgmuptcut.Write()
    hgmuqcut.SetBinContent(1,evnt_pass_gmuchcut)
    hgmuqcut.Write()
    hzptcut.SetBinContent(1,evnt_pass_zcut)
    hzptcut.Write()
    hfatnumcut.SetBinContent(1,evnt_pass_fatnumcut)
    hfatnumcut.Write()
    hfatetacut.SetBinContent(1,evnt_pass_fatetacut)
    hfatetacut.Write()
    
    #The saved results
    for hist in hlist:
        hist.Write()

    #print "number of events with > 1 muon ",evnt_pass_munumcut
    print "numer of good Zprimes ",zpcounter
    print "numer of ad Zprimes ", poorzp
    print "total Zprimes ",zpcounter+poorzp
    print "number of parton level events with > 1 muon ",evnt_pass_gmunumcut
    #print "number of events with opp charge muons ",evnt_pass_muchcut
    print "number of parton level events with opp charge muons ",evnt_pass_gmuchcut
    #print "number of events with muons pass kinematic cuts ",evnt_pass_mukincut
#    print "number of parton level events with muons pass kinematic cuts ",evnt_pass_gmukincut
    print "number of parton level dilepton containing events, with Zpt > 100 GeV: ",evnt_pass_zcut
    print "number of events with > 0 fat jet ",evnt_pass_fatnumcut
    print "number of events with fat jets in eta region ",evnt_pass_fatetacut
    print "number of events with > 0 AK4 jet ",evnt_pass_jetnumcut
    print "number of events with jets in eta region  ",evnt_pass_jetetacut
    print "hists saved in ",output
    print "hit Enter to exit"
    
    sys.stdin.readline()#Keeps canvas open
        
    output.Close()
