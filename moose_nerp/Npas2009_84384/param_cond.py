# Generated from npzfile: fitgp-Npas-cmaes_Npas2009_84384_24.npz of fit number: 9008
#Do not define EREST_ACT or ELEAK here - they are in the .p file
# Contains maximal conductances, name of .p file, and some other parameters
# such as whether to use GHK, or whether to have real spines

import numpy as np

from moose_nerp.prototypes import util as _util

#if ghkYesNo=0 then ghk not implemented
#Note that you can use GHK without a calcium pool, it uses a default of 5e-5 Cin
if False: # param_sim.Config['ghkYN']:
    ghKluge=0.35e-6
else:
    ghKluge=1

#using 0.035e-9 makes NMDA calcium way too small, using single Tau calcium
ConcOut=2e-3     # mM, default for GHK is 2e-3
Temp=30         # Celsius, needed for GHK objects, some channels

neurontypes = None
morph_file ={'Npas':'GP1_41comp_24_Npas_7270_24_Npas_9008.p'}
##{'proto': 'GP1_41comp_24_proto_7395.p', 'arky': 'GP_arky_41comp.p', 'Npas':'GP1_41comp_24_Npas_7270_24_Npas_9008.p'}
NAME_SOMA='soma'

#CONDUCTANCES
#Kdr is Kv2
# helper variables to index the Conductance and synapses with distance
# UNITS: meters
#soma spherical so x,y=0,0, 1e-6 means prox=soma
prox = (0,1e-6)
#med =  (0,50e-6)
dist = (1e-6, 1000e-6)
axon = (0.,1., 'axon')
#If using swc files for morphology, specify structure using: _1 as soma, _2 as apical dend, _3 as basal dend and _4 as axon

#CONDUCTANCE VALUES - UNITS of Siemens/meter squared
# _proto for prototypical GP neuron
'''_proto = _util.NamedDict(
    'proto',
    KDr={prox: 252.11742766709327, dist: 189.58923312652283, axon: 256.04921275490784},
    Kv3={prox: 847.5656407446413, dist: 827.3424242663868, axon: 1215.4767445923346},  # , med:847.5656407446413},
    KvF={prox: 32.74023152805182, dist: 38.986090675424656, axon: 88.32946939915182},  # , med: 32.74023152805182},
    KvS={prox: 0.004268194532763626, dist: 7.2201454857388425, axon: 14.330839867323718},  # , med: 0.004268194532763626
    KCNQ={prox: 0.33327276651857024, dist: 0.33327276651857024, axon: 0.33327276651857024},  # , med: 0.33327276651857024
    NaF={prox: 8677.968478081542, dist: 13.051035835032058, axon: 6518.153479823622},  # , med: 8677.968478081542
    NaS={prox: 4.896882716585459, dist: 4.428424596320797, axon: 0.7584080351316547},  # med: 4.896882716585459,
    Ca={prox: 0.022734861190674006, dist: 0.00030035624117286574, axon: 0},  # med: 0.022734861190674006,
    HCN1={prox: 0.7768751202592691, dist: 1.5515693745222825, axon: 0},  # , med: 0.7768751202592691
    HCN2={prox: 2.5734741500058576, dist: 3.88790810050192, axon: 0},  # med: 2.5734741500058576,
    SKCa={prox: 0.07619950383116704, dist: 3.7819926981266327, axon: 0},  # med: 0.07619950383116704,
    BKCa={prox: 67.60005704890932, dist: 111.9306268912748, axon: 0},
    #BKCa={prox: 140, dist: 224, axon: 0},  # med: 67.60005704890932,
)

_arky = _util.NamedDict(
    'arky',
    KDr={prox: 300, dist: 58.2, axon: 580},
    Kv3={prox: 266, dist: 46.6, axon: 466},
    KvF={prox: 2.5, dist: 2.5, axon: 25},
    KvS={prox: 0.75, dist: 0.75, axon: 7.5},
    KCNQ={prox: 0.04, dist: 0.04, axon: 0.04},
    NaF={prox: 40000, dist: 400, axon: 40000},
    NaS={prox: 0.15, dist: 0.15, axon: 0.5},
    Ca={prox: 0.1, dist: 0.06, axon: 0},
    HCN1={prox: 0.2, dist: 0.2, axon: 0},
    HCN2={prox: 0.25, dist: 0.25, axon: 0},
    SKCa={prox: 35, dist: 3.5, axon: 0},
    BKCa={prox: 200, dist: 200, axon: 0},
)'''

_Npas = _util.NamedDict(
    'Npas',
    KDr={prox: 816.8989463450805, dist: 183.56532746623026, axon: 95.07562539984812},
    Kv3={prox: 962.9149438861408, dist: 1829.745700092937, axon: 47.45103207685233},
    KvF={prox: 42.97526266471602, dist: 2.280852251569698, axon: 34.16530807350059},
    KvS={prox: 40.284776681371156, dist: 21.373527768713025, axon: 34.22143427615285},
    KCNQ={prox: 0.47885294740721396, dist: 0.47885294740721396, axon: 0.47885294740721396},
    NaF={prox: 9625.992231488503, dist: 113.49532291398887, axon: 130.9127747554772},
    NaS={prox: 5.762416276551132, dist: 9.924224846159817, axon: 6.286563275472181},
    Ca={prox: 0.6115537210367485, dist: .1.004388868053604, axon: 0},
    HCN1={prox: 3.616564763613245, dist: .0.07570199482239642, axon: 0},
    HCN2={prox: 1.5401682747767147, dist: 2.250952687443836, axon: 0},
    SKCa={prox: 8.632807039288561, dist: 0.36845844940143807, axon: 0},
    BKCa={prox: 611.840463634394, dist: 37.90765325053504, axon: 0},
    #BKCa={prox: 611.840463634394, dist: 37.90765325053504, axon: 0}, ethanol
)
Condset  = _util.NamedDict(
    'Condset',
    proto = _proto,
    Npas=_Npas
)
