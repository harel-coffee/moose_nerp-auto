#param_net.py
####################### Populations
from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.ttables import TableSet
from moose_nerp.prototypes import util as _util
from moose_nerp.prototypes.connect import dend_location,connect,ext_connect 

neur_distr=NamedList('neur_distr', 'neuronname spacing percent')

netname='/gp'
confile='gp_connect'
outfile='gp_out'

spacing=54e-6 #Fig. 2 Hernandez Parvabinum+ Neurons and Npas1+ Neurons 2015
#pv+: 54e-6 n=41, npas1+: 60e-6 n=33, calculated by measuring distance between neuron pairs and calculating mean 
#0,1,2 refer to x, y and z
grid={}
grid[0]={'xyzmin':0,'xyzmax':340e-6,'inc':spacing}
grid[1]={'xyzmin':0,'xyzmax':340e-6,'inc':spacing}
grid[2]={'xyzmin':0,'xyzmax':0,'inc':0}

#Do not include a neuron type in pop_dict if the proto not created
neuron1pop=neur_distr(neuronname='proto', spacing=grid,percent=0.55) #Table 2 Hernandez Parvabinum+ Neurons and arky Neurons 2015
#calculated from percent composition of PV+=proto, Npas1+/FoxP2+=Npas, Lhx6=arky
neuron2pop=neur_distr(neuronname='Npas', spacing=grid,percent=0.25)
neuron3pop=neur_distr(neuronname='Lhx6', spacing=grid,percent=0.20)
pop_dict={'proto':neuron1pop,'Npas': neuron2pop,'Lhx6':neuron3pop}

#from arky140F - loc _0, unless CV close to 1
chanSTD_arky = {
    'KDr': 0.02,
    'Kv3': 0.0196,
    'KvS': 0.0373,
    'KvF': 0.0083,
    'KCNQ': 0.0137,
    'BKCa': 0.012,
    'SKCa': 0.15,
    'HCN1': 0.1254,
    'HCN2': 0.125,
    'Ca': 0.0835,
    'NaF': 0.0335,
    'NaS': 0.115,
}
#from proto154 - loc _0, unless CV close to 1
chanSTD_proto = {
    'KDr': 0.0247,
    'Kv3': 0.009,
    'KvS': 0.0153,
    'KvF': 0.0059,
    'HCN1': 0.07,
    'HCN2': 0.087,
    'KCNQ': 0.034,
    'Ca': .0294,
    'NaF': 0.0152,
    'NaS': 0.0654,
    'BKCa': 0.025,
    'SKCa': 0.1024,
}
chanvar={'proto':chanSTD_proto, 'Npas':chanSTD_arky, 'Lhx6':chanSTD_arky}

####################### Connections
#tables of extrinsic inputs
#first string is name of the table in moose, and 2nd string is name of external file
tt_STN = TableSet('tt_STN', 'gp_net/STN_lognorm',syn_per_tt=3)

#description of intrinsic inputs
ConnSpaceConst=300e-6
neur1pre_neur1post=connect(synapse='gaba', pre='proto', post='proto', space_const=ConnSpaceConst)#internal post syn fraction in 10% Shink Smith 1995
neur1pre_neur2post=connect(synapse='gaba', pre='proto', post='Npas', space_const=ConnSpaceConst)
neur1pre_neur3post=connect(synapse='gaba', pre='proto', post='Lhx6', space_const=ConnSpaceConst)
neur2pre_neur1post=connect(synapse='gaba', pre='Npas', post='proto', space_const=ConnSpaceConst)
neur2pre_neur2post=connect(synapse='gaba', pre='Npas', post='Npas', space_const=ConnSpaceConst)
neur2pre_neur3post=connect(synapse='gaba', pre='Npas', post='Lhx6', space_const=ConnSpaceConst)
neur3pre_neur1post=connect(synapse='gaba', pre='Lhx6', post='proto', space_const=ConnSpaceConst)
neur3pre_neur2post=connect(synapse='gaba', pre='Lhx6', post='Npas', space_const=ConnSpaceConst)
neur3pre_neur3post=connect(synapse='gaba', pre='Lhx6', post='Lhx6', space_const=ConnSpaceConst)

#description of synapse and dendritic location of extrinsic inputs
STN_distr=dend_location(postsyn_fraction=1)
ext2_neur1post=ext_connect(synapse='ampa',pre=tt_STN,post='proto', dend_loc=STN_distr)# Corbit Whalen 2016 Table 2 connectivity parameters: Chumhma 2011, Shink Smith 1995, Miguelez 2012 
#ext1_neur1post=ext_connect(synapse='gaba',pre=tt_Str_SPN,post='proto', dend_loc=Str_distr)#ext1 = Str
ext2_neur2post=ext_connect(synapse='ampa',pre=tt_STN,post='Npas', dend_loc=STN_distr)#ext2 STN
#ext1_neur2post=ext_connect(synapse='gaba',pre=tt_Str_SPN,post='Npas', dend_loc=Str_distr)
ext2_neur3post=ext_connect(synapse='ampa',pre=tt_STN,post='Lhx6', dend_loc=STN_distr)#ext2 STN

#Collect all connection information into dictionaries
#1st create one dictionary for each post-synaptic neuron class
proto={}
Npas={}
Lhx6={}
#connections further organized by synapse type
#the dictionary key for tt must have 'extern' in it
proto['gaba']={'proto': neur1pre_neur1post, 'Npas': neur2pre_neur1post,'Lhx6': neur3pre_neur1post}
#proto['gaba']={'proto': neur1pre_neur1post, 'Npas': neur2pre_neur1post, 'extern': ext1_neur1post}
proto['ampa']={'extern': ext2_neur1post}
Npas['gaba']={'proto': neur1pre_neur2post, 'Npas': neur2pre_neur2post, 'Lhx6': neur3pre_neur2post}
#Npas['gaba']={'proto': neur1pre_neur2post, 'Npas': neur2pre_neur2post, 'extern': ext1_neur2post}
Npas['ampa']={'extern': ext2_neur2post}
Lhx6['gaba']={'proto': neur1pre_neur3post, 'Npas': neur2pre_neur3post, 'Lhx6': neur3pre_neur3post}
#Npas['gaba']={'proto': neur1pre_neur2post, 'Npas': neur2pre_neur2post, 'extern': ext1_neur2post}
Lhx6['ampa']={'extern': ext2_neur3post}

#Then, collect the post-synaptic dictionaries into a single dictionary.
#for NetPyne correspondance: change connect_dict to connParams
connect_dict={'proto': proto,'Npas':Npas,'Lhx6':Lhx6}

# m/sec - GABA and the Basal Ganglia by Tepper et al
cond_vel={'proto':0.8,'Npas':0.8, 'Lhx6':0.8} #conduction velocity
mindelay={'proto':1e-3,'Npas':1e-3,'Lhx6':1e-3}
