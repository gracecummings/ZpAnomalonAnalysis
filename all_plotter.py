#This is designed to just be a general plotting tool

import sys
from ROOT import *

#Load in files
input1 = sys.argv[1]#File that needs hists made
fin1   = TFile(input1)
input2 = sys.argv[2]#File that already has hists made
fin2   = TFile(input2)
input3 = sys.argv[3]#Second file that already has hists made
fin3   = TFile(input3)

t1     = fin1.Get("passedEvents")#ttree from file that needs hists, made via TG
t2     = fin2.Get("passedEvents")
t3     = fin3.Get("passedEvents")

#What I want to plot
tc0 = TCanvas("tc0","MET Ratios",900,900)
tc0.Divide(2,2)

hMET1 = TH1F('hMET1','LHE Level Met Tongguang Gen MZp 2000, MND 500, MNS 200',100,0,1000)
hMET2 = TH1F('hMET2','LHE Level Met Grace Gen MZp 2000, MND 500, MNS 200',100,0,1000)
hMET3 = TH1F('hMET3','LHE Level Met Grace Gen MZp 1000, MND 300, MNS 100',100,0,1000)


#Building and fetching histos
for i,event in enumerate(t1):
    if i % 1000 == 0: print "reading event "+str(i)

    met1 =t1.GetLeaf("ptMET").GetValue()
    hMET1.Fill(met1)

for i,event in enumerate(t2):
    if i % 1000 == 0: print "reading event "+str(i)

    met2 =t2.GetLeaf("ptMET").GetValue()
    hMET2.Fill(met2)

for i,event in enumerate(t3):
    if i % 1000 == 0: print "reading event "+str(i)

    met3 =t3.GetLeaf("ptMET").GetValue()
    hMET3.Fill(met3)


hMET1_norm = 1/hMET1.Integral()
hMET1.Scale(hMET1_norm)
#hMET2 = fin2.Get("hMET")
hMET2_norm = 1/hMET2.Integral()
hMET2.Scale(hMET2_norm)
hMET3_norm = 1/hMET3.Integral()
hMET3.Scale(hMET3_norm)

#hMET4 = fin2.Get("hgenMET_mass")
#hMET3 = fin3.Get("h_psmiss")

#Let's draw this shit
tc0.cd(1)
hMET1.Draw("HIST")
hMET1.SetLineColor(3)
tc0.Update()
tc0.cd(2)
hMET2.SetLineColor(2)
hMET2.Draw("HIST")
tc0.Update()
tc0.cd(3)
hMET3.Draw("HIST")
hMET3.SetLineColor(1)
tc0.Update()
#tc0.cd(3)
#hMET4.Draw()
#hMET4.SetLineColor(1)
#tc0.Update()

tc0.cd(4)
hMET3.Draw("HIST")
hMET3.SetLineColor(1)
hMET3.SetStats(0)
hMET3.SetTitle("Overlay of LHE Level Generation")
hMET1.Draw("HIST SAME")
hMET1.SetLineColor(3)
hMET1.SetStats(0)
hMET2.Draw("HIST SAME")
hMET2.SetLineColor(2)
hMET2.SetStats(0)
tc0.Update()
#hMET4.SetLineColor(1)
#hMET4.Draw("SAME")
#hMET4.SetStats(0)

leg = TLegend(0.52,0.6,0.98,0.9)
leg.AddEntry(hMET1,"LHE Level MET,Tongguang Gen MZp 2000","l")
leg.AddEntry(hMET2,"LHE Level MET Grace Gen MZp 2000","l")
leg.AddEntry(hMET3,"LHE Level MET, Grace Gen MZp 1000","l")
#leg.AddEntry(hMET4,"GenMET output in Delphes ntuple w/cuts","l")
#gStyle.SetLegendTextSize(4)
#gStyle.SetLegendBorderSize(0)
leg.Draw()

tc0.Update()


sys.stdin.readline()#Keeps canvas open
