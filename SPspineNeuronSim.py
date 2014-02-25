######## SPspineNeuronSim.py ############
## Code to create two SP neuron classes 
##          using dictionaries for channels and synapses
##          calcium based learning rule/plasticity function
##          spines, optionally with ion channels and synpases
## Synapses implemented to test the plasticity function
##This one should be used to tune parameters and channel kinetics (but using larger morphology)
##Presently, AHPs too deep, I don't know about spike width
##Also, fires too early with slightly higher current injection
import sys
sys.path.append('./')
import os
os.environ['NUMPTHREADS'] = '1'
from pylab import *
import numpy as np
import matplotlib.pyplot as plt
from string import *

import moose 
from moose import utils

from SPcondParamSpine import *
from SPchanParam import *
from SynParamSpine import *
from CaPlasParam import *
execfile('ChanGhkProtoLib.py')
execfile('PlotChannel2.py')
execfile('CaFuncSpine.py')
execfile('makeSpine.py')
execfile('CellProtoSpine.py')
execfile('SynProtoSpine.py')
execfile('CaPlasFunc.py')
execfile('injectfunc.py')

############ Parameters for simulation control #################
#plas=plasticity elements and synaptic input, curr=ionic currents
#calcium and plasyesno are originally defined in CaPlasParam.py
#Note that you will get spines, but no plasticity if calcium=0 and plasyesno=1
calcium=1
plasyesno=1
#ghkYesNo and spineYN are originally defined in SPcondparams.py
#note that if ghkYesNo=0, make sure that ghKluge = 1
spineYN=1
if spineYN==0:
    #put all the synaptic channels in the dendrite.  These lists are in SynParamSpine.py
    DendSynChans=list(set(DendSynChans+SpineSynChans))
    SpineSynChans=[]
#Which parts of the simulation should be shown?
plotplas=1
#to prevent you from plotting plasticity if not created:
if (plasyesno==0):
    plotplas=0
#plotcurr indicates whether to plot time dependent currents (or conductances)
plotcurr=0
currmsg='get_Gk'
currlabel='S'

#whether to plot the various ion channel activation and inactivation curves
pltchan=0
pltpow=1

#showclocks=1 will show which elements are assigned to which clock
showclocks=0

#simulation time, current injection, and synaptic input
simtime = 0.5999 #0.4999
curr1=0.20e-9
curr2=curr1+0.09e-9
currinc=0.1e-9
#With these params, 1st PSP has no AP, 2nd PSP has AP after, 3d PSP has AP before
delay=0.20
width=0.02
stimtimes=[0.04,0.19,0.46]

###dt and solver
plotdt = 0.2e-3
simdt = 0.25e-5
hsolve=1

################### Clocks.  Note that there are no default clocks ##########
inited = False
def assign_clocks(model_container_list, dataName, simdt, plotdt,hsolve):
    global inited
    # `inited` is for avoiding double scheduling of the same object
    if not inited:
        print 'SimDt=%g, PlotDt=%g' % (simdt, plotdt)
        moose.setClock(0, simdt)
        moose.setClock(1, simdt)
        moose.setClock(2, simdt)
        moose.setClock(3, simdt)
        moose.setClock(4, simdt)
        moose.setClock(5, simdt)
        moose.setClock(6, plotdt)
        for path in model_container_list:
            print 'Scheduling elements under:', path
            if hsolve:
                print "USING HSOLVE"
                hsolve = moose.HSolve( '%s/hsolve' % (path))
                moose.useClock( 1, '%s/hsolve' % (path), 'process' )
                hsolve.dt=simdt
            moose.useClock(0, '%s/##[ISA=Compartment]' % (path), 'init')
            moose.useClock(1, '%s/##[ISA=Compartment],%s/##[TYPE=CaConc]' % (path,path), 'process')
            moose.useClock(2, '%s/##[TYPE=SynChan],%s/##[TYPE=HHChannel]' % (path,path), 'process')
            moose.useClock(3, '%s/##[TYPE=Func],%s/##[TYPE=MgBlock],%s/##[TYPE=GHK]' % (path,path,path), 'process')
            moose.useClock(4, '%s/##[TYPE=SpikeGen],%s/##[TYPE=TimeTable]' % (path,path), 'process')
        moose.useClock(5, '/##[TYPE=PulseGen]', 'process')
        moose.useClock(6, '%s/##[TYPE=Table]' % (dataName), 'process')
        inited = True
    moose.reinit()

#################################-----------create the model
##create 2 neuron prototypes with synapses and calcium
##only create synapses to create plasticity, hence pass plasyesno to function
[MSNsyn,neuron,pathlist,capools,synarray]=neuronclasses(pltchan,pltpow,calcium,plasyesno,spineYN,ghkYesNo)

#for testing, create one synaptic connection, a time table, and one plasticity device
#No point doing this unless calcium has been implemented
if (calcium==1 and plasyesno==1):
    syn={}
    plas={}
    stimtab={}
    for neurtype in neurontypes:
        stimtab[neurtype]=moose.TimeTable('%s/TimTab' %(neurtype))
        stimtab[neurtype].vec=stimtimes
        for key in SynChanDict.keys()[0:2]:
            synchan=MSNsyn[neurtype][key][1]
            synap=moose.SynChan(synchan)
            synap.synapse.num=1
            synap.synapse[0].delay=0.001
            m = moose.connect(stimtab[neurtype], 'event', moose.element(synap.path + '/synapse'),  'addSpike')
            if key=='nmda':
                synchanCa=moose.SynChan(MSNsyn[neurtype][key][1].path+'CaCurr')
                synchanCa.synapse.num=1
                synchanCa.synapse[0].delay=0.001
                m = moose.connect(stimtab[neurtype], 'event', moose.element(synchanCa.path + '/synapse'),  'addSpike')
        syn[neurtype]=moose.SynChan(MSNsyn[neurtype]['ampa'][1])
        ###Synaptic Plasticity
        plas[neurtype]=plasticity(MSNsyn[neurtype]['ampa'][1],highThresh,lowThresh,highfactor,lowfactor)

#------------------Current Injection
pg=setupinj(delay,width,curr1)

###############--------------output elements
data = moose.Neutral('/data')

execfile('SingleGraphs.py')
[vmtab,catab,plastab,currtab,plaslegend]=graphtables(neuron,plotplas,plotcurr,calcium,capools,currmsg)
if spineYN==1:
    spinecatab=[]
    spinevmtab=[]
    for neurtype,neurnum in zip(neurontypes,range(len(neurontypes))):
        spinecatab.append(moose.Table('/data/SpCa%s' % (neurtype)))
        spinevmtab.append(moose.Table('/data/SpVm%s' % (neurtype)))
        spname=MSNsyn[neurtype]['ampa'][1].path[0:rfind(MSNsyn[neurtype]['ampa'][1].path,'/')+1]
        cal=moose.element(spname+caName)
        spine=moose.element(spname)
        moose.connect(spinecatab[neurnum], 'requestData', cal, 'get_Ca')
        moose.connect(spinevmtab[neurnum], 'requestData', spine, 'get_Vm')
#
########## clocks are critical
## these function needs to be tailored for each simulation
## if things are not working, you've probably messed up here.
assign_clocks(pathlist,'/data', simdt, plotdt,hsolve)

#Make sure elements have been assigned clocks
tk = moose.element('/clock/tick')
if (showclocks):
    for ii in range(3,6):
        print 'Elements on tick ', ii
        for e in tk.neighbours['proc%s' % (ii)]:
            print ' ->', e.path

###########Actually run the simulation
for inj in arange(curr1,curr2,currinc):
    pg.firstLevel = inj
    moose.reinit()
    moose.start(simtime)
    #
    graphs(vmtab,catab,plastab,currtab,plotplas,plotcurr,plaslegend,calcium,currlabel)
if spineYN==1:
    figure()
    t = np.linspace(0, simtime, len(spinecatab[0].vec))
    subplot(211)
    for neurnum in range(len(neurontypes)):
        plt.plot(t,spinecatab[neurnum].vec,label=neurontypes[neurnum])
    subplot(212)
    for neurnum in range(len(neurontypes)):
        plt.plot(t,spinevmtab[neurnum].vec,label=neurontypes[neurnum])
    plt.legend()
    plt.show()
#End of inject loop
###### Demonstration of loop with parameter adjustment ###
if plasyesno==0:
    execfile('AdjustParams.py')
    ChanList=['KaF','CaL12']
    minfac=0.8
    maxfac=0.7
    incfac=0.5
    for factor in arange(minfac,maxfac,incfac):
        factorList=[factor,2*factor]
        adjustParams('D1',GnaCondD1,CondD1,factorList,ChanList)
        moose.reinit()
        moose.start(simtime)
    #
        graphs(vmtab,catab,plastab,currtab,plotplas,plotcurr,plaslegend,calcium,currlabel)
#Replace graphs with table output to files to inspection later
#Add in comparison of results with a standard to further automate the parameter turning