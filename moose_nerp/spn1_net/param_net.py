#param_net.py
####################### Populations
from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.ttables import TableSet
from moose_nerp.prototypes import util as _util
from moose_nerp.prototypes.connect import dend_location,connect,ext_connect 

neur_distr=NamedList('neur_distr', 'neuronname spacing percent')

netname='/striatum'
confile='striatum_connect'
outfile='striatum_out'

spacing=25e-6
#0,1,2 refer to x, y and z
grid={}
grid[0]={'xyzmin':0,'xyzmax':100e-6,'inc':spacing}
grid[1]={'xyzmin':0,'xyzmax':100e-6,'inc':spacing}
grid[2]={'xyzmin':-300e-6,'xyzmax':-300e-6,'inc':0}

#Do not include a neuron type in pop_dict if the proto not created
D1pop=neur_distr(neuronname='D1', spacing=grid,percent=0.47)
D2pop=neur_distr(neuronname='D2', spacing=grid,percent=0.47)
FSIpop=neur_distr(neuronname='FSI', spacing=grid,percent=0.06)
pop_dict={
          'D1':D1pop,
          'D2': D2pop,
          'FSI': FSIpop,
          }

chanvarSPN = {
    'Krp': 0.04,
    'KaF': 0.04,
    'KaS': 0.04,
    'Kir': 0.04,
    #'CaL13': 0.04,
    'CaL12': 0.04,
    'CaR': 0.04,
    #'CaN': 0.04,
    #'CaT': 0.04,
    'NaF': 0.0,
    #'BKCa': 0.04,
    #'SKCa': 0.04,
}
chanvarFSI={
    'Krp': 0.04,
    'KaF': 0.04,
    'KaS': 0.04,
    'NaF': 0.04,
}
chanvar={
    'D1':chanvarSPN,
    'D2':chanvarSPN,
    'FSI':chanvarFSI,
}

####################### Connections
# add post_location to both of these - optionally specify e.g. prox vs distal for synapses

#list of time tables that provide extrinsic connections.  Each tt connected to syn_per_tt synapses
tt_Ctx_SPN = TableSet('CtxSPN', 'spn1_net/Ctx2000_exp_freq10.0',syn_per_tt=2)

distr=dend_location(mindist=0e-6,maxdist=400e-6,postsyn_fraction=1)#,half_dist=50e-6,steep=1)
FSI_distr = dend_location(mindist=0e-6,maxdist=80e-6,postsyn_fraction=1)

MSNconnSpaceConst=250e-6
FSIconnSpaceConst=400e-6
#connectins between network neurons (intrinsic connections)
D1pre_D1post=connect(synapse='gaba', pre='D1', post='D1', space_const=MSNconnSpaceConst)
D1pre_D2post=connect(synapse='gaba', pre='D1', post='D2', space_const=MSNconnSpaceConst)
D2pre_D1post=connect(synapse='gaba', pre='D2', post='D1', space_const=MSNconnSpaceConst)
D2pre_D2post=connect(synapse='gaba', pre='D2', post='D2', space_const=MSNconnSpaceConst)
FSIpre_D1post=connect(synapse='gaba', pre='FSI', post='D1', space_const=FSIconnSpaceConst,weight=3)
FSIpre_D2post=connect(synapse='gaba', pre='FSI', post='D2', space_const=FSIconnSpaceConst,weight=3)
FSIpre_FSIpost=connect(synapse='gaba', pre='FSI', post='FSI', space_const=FSIconnSpaceConst)
#time table input (extrinsic connections)
ctx_D1post=ext_connect(synapse='ampa',pre=tt_Ctx_SPN,post='D1', dend_loc = distr)
#thal_D1post=ext_connect(synapse='ampa',pre=tt_Thal_SPN,post='D1', dend_loc = distr)
ctx_D2post=ext_connect(synapse='ampa',pre=tt_Ctx_SPN,post='D2', dend_loc = distr)
#thal_D2post=ext_connect(synapse='ampa',pre=tt_Thal_SPN,post='D2', dend_loc = distr)
ctx_FSIpost=connect(synapse='ampa',pre=tt_Ctx_SPN,post='FSI',)


#one dictionary for each post-synaptic neuron class
D1={}
D2={}
FSI={}
connect_dict={}
##Collect the above connections into dictionaries organized by post-syn neuron, and synapse type
D1['ampa'] = {'extern1': ctx_D1post}    #'extern2': thal_D1post }

D1['gaba'] = {
    'D1':D1pre_D1post,
    'D2':D2pre_D2post,
    'FSI':FSIpre_D1post,
}

connect_dict['D1']=D1
D2['gaba']={'D1': D1pre_D2post, 'D2': D2pre_D2post,
            'FSI': FSIpre_D2post
}
D2['ampa']={'extern1': ctx_D2post}
connect_dict['D2']=D2
FSI['gaba']={'FSI': FSIpre_FSIpost}
FSI['ampa']={'extern': ctx_FSIpost}
connect_dict['FSI']=FSI

# m/sec - GABA and the Basal Ganglia by Tepper et al
cond_vel={'D1':0.8,'D2':0.8,'FSI':0.8}
mindelay={'D1':1e-3,'D2':1e-3,'FSI':1e-3}
