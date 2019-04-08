import glob
import leptophobe_analysis
import matplotlib.pyplot as plt

def findZpMass(dirc):
    dsamp      = dirc.split("_")
    msamp      = dsamp[2]
    msampsplit = msamp.split("Zp")
    m          = int(msampsplit[1])
    return m

if __name__=='__main__':
    listsignal1 = glob.glob('ZpAnomalon_lightjets*_gZp1')
    listsignal2 = glob.glob('ZpAnomalon_lightjets*_gZp0.4')

    listsignal2.sort(key = findZpMass)
    listsignal1.sort(key = findZpMass)
    #print listsignal

    masses1 = []
    xss1    = []
    for l in listsignal1:
        m          = findZpMass(l)
        xs         = float(leptophobe_analysis.xsFromBanner(l+'/Events/run_01/run_01_tag_1_banner.txt'))
        masses1.append(m)
        xss1.append(xs)

    masses2 = []
    xss2    = []
    for l in listsignal2:
        m          = findZpMass(l)
        xs         = float(leptophobe_analysis.xsFromBanner(l+'/Events/run_01/run_01_tag_1_banner.txt'))
        masses2.append(m)
        xss2.append(xs)

    djzp = [2000,2500,3000,3500,4000,4500,5000,5500]
    djxs = [0.15,0.03,0.02,0.008,0.01,0.002,0.0025,0.001]
        
    
    plottitle = "Madgraph XS for Zp to light jets"
    plt.plot(masses1,xss1, label = 'gZp 1')
    plt.plot(masses2,xss2, label = 'gZp 0.4')
    plt.plot(djzp,djxs,label = 'dijet xs limit')
    plt.title(plottitle)
    plt.xlabel('MZp (GeV)')
    plt.ylabel('expected XS (pb)')
    plt.yscale('log')
    plt.ylim(.00001,1000)
    plt.legend()
    plt.show()
        
