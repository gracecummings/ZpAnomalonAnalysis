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

def findZpMass(filename):
    s1 = filename.split("_")[4]
    s2 = s1.split("Zp")[1]
    return s2

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-mns","--NSmass",type=int,help = "NS mass of samples you want")
    parser.add_argument("-L","--lumi", type=float,default = 35.9, help = "integrated luminosity for scale in fb^-1")
    parser.add_argument("-x","--xsec", type=float,help = "desired siganl cross section in fb")
    args = parser.parse_args()
    
    
    #Lists to organize your shit
    mns = args.NSmass
    sigl = g.glob('analysis_output/2018-11-*/Delphes_analysis_output/ZpAnomalonHZ_Zp*_ND*_NS'+mns+'*')#list of all signal files with appropraite NS mass
    cleanedl = map(findZpMass,sigl)
    sortsig  = list(set(cleanedl))#The different Zp masses featured

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


        
