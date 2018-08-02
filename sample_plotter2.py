# alternate example of python Delphes analysis
# I ran this on genereted a z+jets sample generated using
# MG5_aMC>generate p p >  Z j , Z > mu+ mu-
# Note:
# generate p p >  Z j  gives Z-> mumu decays in the MG5 output,
# but Z decay is ignored by PYTHIA.  Specify the Z decay to get it right


# this is based on an example found at https://pythonexample.com/code/delphes/

# setup dependencies, use appropriate paths
from ROOT import *
gInterpreter.AddIncludePath("/opt/delphes")
gInterpreter.AddIncludePath("/opt/delphes/external")
gROOT.ProcessLine(".L lester_mt2_bisect.h+")
gSystem.Load("/opt/delphes/libDelphes.so")

# utility function to fill a 1D histogram
# overflows are added to the last bin
# maybe there is a built in feature to do this in ROOT?
def Fill(h,x,wgt=1):
    x=min( x, h.GetBinCenter(h.GetNbinsX()) )
    h.Fill(x,wgt)

    

# Create chain of root tree(s)
#delphes = TChain("Delphes")
#delphes.Add("Zjets_test2/Events/run_01/tag_1_delphes_events.root")
# or open a TFile and get the Tree
tfbkg = TFile("Zjets_test2/Events/run_01/tag_1_delphes_events.root")
ttbkg = tfbkg.Get("Delphes")
tfsig = TFile("PROC_ZpAnomalonHZ_UFO_0/Events/run_01/tag_1_delphes_events.root")
ttsig = tfsig.Get("Delphes")

LUMI=100*1000     # = 100 fb-1
XSsig=0.0052124   # pb
XSZj=390.88       # pb
WgtSig=XSsig*LUMI/ttsig.GetEntries() * 1/XSsig  # scaling to XS=1pb
WgtBkg=XSZj*LUMI/ttbkg.GetEntries()


# Output File
tfout=TFile("sample_plotter2.root","recreate")


# Book histograms
dtbkg={}
dtbkg["ptjet1"] = TH1F("Zj_pTjet1", "p_{T}^{j1}", 100, 0.0, 250.0)
dtbkg["mll"] = TH1F("Zj_mll", "M_{inv}(#mu_{1}, #mu_{2})", 100, 0.0, 200.0)
dtbkg["mll_gen"] = TH1F("Zj_mllgen", "Generated M_{inv}(#mu_{1}, #mu_{2})", 100, 0.0, 200.0)
dtbkg["ptmiss"] = TH1F("Zj_pTmiss", "p_{T}^{miss}", 100, 0.0, 1000)
dtbkg["mt2"] = TH1F("Zj_mt2", "MT2", 50, 25, 2525)


dtsig={}
dtsig["ptjet1"] = TH1F("sig_pTjet1", "p_{T}^{j1}", 100, 0.0, 250.0)
dtsig["mll"] = TH1F("sig_mll", "M_{inv}(#mu_{1}, #mu_{2})", 100, 0.0, 200.0)
dtsig["mll_gen"] = TH1F("sig_mllgen", "Generated M_{inv}(#mu_{1}, #mu_{2})", 100, 0.0, 200.0)
dtsig["ptmiss"] = TH1F("sig_pTmiss", "p_{T}^{miss}", 100, 0.0, 1000)
dtsig["mt2"] = TH1F("sig_mt2", "MT2", 50, 25, 2525)



# Note: if you need a counter while looping use
# python's enumerate() function in the main loop, e.g.:
# for i, evt in enumerate(t):

# now loop thru the events in the tree:
def FillHists(hdict,ttree,wgt=1):
    MT2Class=asymm_mt2_lester_bisect()
    MT2Class.disableCopyrightMessage()

    #for evt in ttree:
    for i, evt in enumerate(ttree):
        if i%1000==0: print "processing:",i,"of",ttree.GetEntries()
        #if i==1000: break


        # grab jets greater than 50:
        # cool, never used lambdas before!
        jets_pt50 = filter(lambda j: j.PT > 50 and abs(j.Eta)<2.4, evt.Jet)
        #for j in jets_pt50: histJetPT.Fill(j.PT)
        if len(jets_pt50)>0: hdict["ptjet1"].Fill(jets_pt50[0].PT,wgt)

        # filter generated muons
        # this is trial and error, I don't fully understand the particle status flags
        # in the Delphes tree
        muons_gen = filter(lambda mu: mu.Status==23 and abs(mu.PID)==13, evt.Particle)
        # note for now we ignore the possibility of more than two leptons
        if len(muons_gen)>1:
            m1=TLorentzVector(muons_gen[0].Px,muons_gen[0].Py,muons_gen[0].Pz,muons_gen[0].E)
            m2=TLorentzVector(muons_gen[1].Px,muons_gen[1].Py,muons_gen[1].Pz,muons_gen[1].E)
            MZgen=(m1+m2).M()
            hdict["mll_gen"].Fill(MZgen,wgt)

        hdict["ptmiss"].Fill( evt.MissingET[0].MET , wgt)
            
        # filter muons w/ pT > 20 at detector level:
        muons_pt20 = filter(lambda mu: mu.PT > 20, evt.Muon)
        #if muons_pt20[0].PT()<60: del muons_pt20[0:]  # require leading muon > PT cut
        if len(muons_pt20)>1:
            Z2ll=muons_pt20[0].P4()+muons_pt20[1].P4()
            hdict["mll"].Fill( Z2ll.M() , wgt)
            #print "Found %d muons w/ pT>20" % len(muons_pt20)            
            # we also need a fat jet for mt2
            if evt.FatJet_size>0:   # use 1st fatjet - double check conversion!
                fjPx=evt.FatJet[0].PT*TMath.Cos(evt.FatJet[0].Phi)
                fjPy=evt.FatJet[0].PT*TMath.Sin(evt.FatJet[0].Phi)
                metx=evt.MissingET[0].MET*TMath.Cos(evt.MissingET[0].Phi)
                mety=evt.MissingET[0].MET*TMath.Sin(evt.MissingET[0].Phi)
                                
        
                # calculate a range of mT2 results, m_chiA = m_ChiB = M_ND
                for mND in range(50,2501,50):
                    mt2 = MT2Class.get_mT2(Z2ll.M(),Z2ll.Px(),Z2ll.Py(),
                                           evt.FatJet[0].Mass, fjPx, fjPy,
                                           metx,mety,
                                           mND,mND)
                    hdict["mt2"].Fill( mt2 , wgt)
        
            
FillHists(dtbkg,ttbkg,WgtBkg)
FillHists(dtsig,ttsig,WgtSig)
        
      
tfout.Write()
tfout.Close()
