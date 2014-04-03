#SpineParams.py
from SPcondParamSpine import ghKluge

spineDensity=0.1e6      #should make this distance dependent
necklen=0.3e-6          #define all these parameters elsewhere
neckdia=0.1e-6
headdia=0.5e-6
nameneck='neck'
namehead='head'
spineRA=4*4    #additional factor of 4 due to exptl higher than expected Ra Spine
spineRM=2.8
spineCM=0.01
spineELEAK=-50e-3
spineEREST=-80e-3

#if spinesYN=0, no spines will be created (all synapses on dendrites)
spineYesNo=1
spineChanList=[] #['CaL13']
spineCond=[0.1*ghKluge]