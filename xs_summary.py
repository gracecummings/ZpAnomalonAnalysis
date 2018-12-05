import os
import argparse
import ROOT
import glob
import leptophobe_analysis

def findNDMass(filename):
    s1 = filename.split("_")[2]
    s2 = s1.split("ND")[1]
    return int(s2)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-mzp","--Zpmass",type=int,help = "Zp mass of samples you want")
    parser.add_argument("-mns","--NSmass",type=int,help = "NS mass of samples you want")
    args = parser.parse_args()

    mzp = args.Zpmass
    mns = args.NSmass
    listsignal = glob.glob('ZpAnomalonHZ_Zp'+str(mzp)+'_ND*_NS'+str(mns)+'/Events/run_01/run_01_tag*')#can put back in date thing later
    listsignal.sort(key = findNDMass)
    
    for f in listsignal:
        mnd = findNDMass(f)
        print mnd
        #xs = leptophobe_analysis.xsFromBanner(f)
        f1 = open(f,'r')
        lines = f1.readlines()
        for i,l in enumerate(lines):
            #f i % 100 == 0:
            #   print i
            if "ptllmin  ! Minimum pt for 4-momenta sum of leptons(l and vl)" in l:
                print l
                break
    
