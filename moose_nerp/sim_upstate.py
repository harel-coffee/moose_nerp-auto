#!/usr/bin/env python3
"""
Simulate upstate conditions for Patch Samples 4-5 and Matrix Samples 2-3 models.

Modify local channel conductances at site of clustered input for each neuron 
to achieve upstate duration and amplitude consistent with experimental averages.

Do current injection with modified conductances to confirm modifying them does 
not greatly alter the fit to current injection data.

Simulate without blocking sodium channels.

Simulate with additional dispersed inputs.

Simulation steps:

For each neuron:
    - Randomly select parameters from within a range to vary
        - parameters to vary:
        - Random seed necessary for selecting parameters?
    For each set of parameters:
        - Use same random seeds to control synapse selection
        - [done] simulate upstate only: Need an upstate seed (same every sim/param set)
        - [done] Simulate dispersed only: Need a Dispersed seed (same every sim/param set for now)
        - [done] Simulate upstate and dispersed together: Use same upstate seed and same dispersed seed
        - [ ] range over dispersion frequency params
        
        - [later] Should we simulate "spatially disperse" the clustered inputs but at the same time as a control? Not for now
        - [done] Simulate single EPSP (EPSP seed?-same every sim)
        - [done] Simulate IV traces to compare to original model IV to see how much the optimization fit is messed up
        - [ ] simulate upstate plus current injection at increasing steps...

TO DO:

Save voltage at soma from each simulation

File name scheme:
param_set_X_sim_name_sim_variable_name_value_neuron-name_vm.txt
e.g.
param_set_1__upstate_plus_dispersed__dispersed_freq_375__D1PatchSample5_vm.txt



Make plotting optional argument

Save parameter variation values (and any necessary random seeds?) for each simulation

param_set_list.csv

set_ID (corresponds to param_set_X in filenames), var1name, var2name...
e.g.
0,      2, 3,...



"""

import importlib
import numpy as np


def rand_mod_dict():
    mod_dict = {"D1MatrixSample2": {}, "D1PatchSample5": {}}

    var_range = {
        "KaS": [0, 4],
        "NMDA": [0, 4],
        "CaR": [0, 20],
        "AMPA": [0.1, 1],
        "CaL12": [0, 4],
        "CaL13": [0, 4],
        "CaT32": [0, 4],
        "CaT33": [0, 4],
        "Kir": [0, 4],
        "KaF": [0, 4],
    }
    for mod in mod_dict:
        for var in var_range:
            mod_dict[mod][var] = np.random.uniform(*var_range[var])

    return mod_dict


def make_mod_dict():

    mod_dict = {
        "D1MatrixSample2": {},
        # "D1MatrixSample3": {},
        # "D1PatchSample4": {},
        "D1PatchSample5": {},
    }

    mod_dict["D1MatrixSample2"] = {
        "KaS": 0.5,  # 0.2,
        "NMDA": 2.25,
        "CaR": 10,  # 1,
        "AMPA": 0.4,  # 2,
        "CaL12": 1,  # 0.01,
        "CaL13": 1,  # 0.25,
        "CaT32": 0.5,  # 0.001,
        "CaT33": 1,  # 0.05,
        "Kir": 1,
    }
    # mod_dict["D1MatrixSample3"] = {
    #     "KaS": 1,
    #     "NMDA": 1,
    #     "CaR": 1,
    #     "AMPA": .25,#1,
    #     "CaL12": 1,
    #     "CaL13": 1,
    #     "CaT32": 1,
    #     "CaT33": 1,
    #     "Kir": 1,
    #     "KaF": 1,
    #     "CaCC": 0,
    # }
    # mod_dict["D1PatchSample4"] = {
    #     "KaS": 1,
    #     "NMDA": 2,
    #     "CaR": 100,
    #     "AMPA": .19,#1,
    #     "CaL12": 1,
    #     "CaL13": 1,
    #     "CaT32": 1,
    #     "CaT33": 1,
    #     "Kir": 1,
    #     "KaF": 1,
    # }
    mod_dict["D1PatchSample5"] = {
        "KaS": 1,
        "NMDA": 2.25,
        "CaR": 2,
        "AMPA": 0.4,  # .3,#1,
        "CaL12": 1,
        "CaL13": 1,
        "CaT32": 1,
        "CaT33": 1,
        "Kir": 1,
        "KaF": 1,  # 1,
    }

    return mod_dict


def mod_local_gbar(complist, mod_dict):
    # input_parent_dends = set([i.parent.parent for i in inputs])
    for comp in complist:
        for chan in mod_dict:
            for child in comp.children:
                if chan == child[0].name and "HHChannel" in str(child[0].__class__):
                    # print(child[0].Gbar)
                    child[0].Gbar *= mod_dict[chan]
                    # print(child[0].Gbar)
                    # print(child.path)


def mod_dist_gbar(model, mod_dict):
    for chan in mod_dict:
        if chan in model.Condset.D1.keys():
            #print("{} before: {}".format(chan, model.Condset.D1[chan]))
            model.Condset.D1[chan][model.param_cond.dist] *= mod_dict[chan]
            #print("modifying {} ".format(chan))
            #print("{} after: {}".format(chan, model.Condset.D1[chan]))


def setup_model(model, mod_dict, block_naf=False, filename=None):
    model = importlib.import_module("moose_nerp.{}".format(model))
    # from IPython import embed; embed()
    from moose_nerp.prototypes import create_model_sim
    from moose_nerp.prototypes import spatiotemporalInputMapping as stim
    import moose

    if filename is not None:
        model.param_sim.fname = filename
    model.param_sim.save_txt = True
    model.param_sim.plot_vm = False
    model.param_sim.plot_current = True
    model.param_sim.plot_current_message = "getIk"
    model.spineYN = True
    model.calYN = True
    model.synYN = True
    model.SpineParams.explicitSpineDensity = 1e6
    if any("patch" in v for v in model.morph_file.values()):
        # model.SpineParams.spineParent = "570_3"
        model.clusteredparent = "570_3"
    if any("matrix" in v for v in model.morph_file.values()):
        # model.SpineParams.spineParent = "1157_3"
        model.clusteredparent = "1157_3"

    model.SpineParams.spineParent = model.clusteredparent  # "soma"
    modelname = model.__name__.split(".")[-1]
    model.param_syn._SynNMDA.Gbar = 10e-09 * mod_dict[modelname]["NMDA"]
    model.param_syn._SynNMDA.tau2 *= 2
    model.param_syn._SynNMDA.tau1 *= 2
    model.param_syn._SynAMPA.Gbar = 1e-9 * mod_dict[modelname]["AMPA"]
    model.param_syn._SynAMPA.spinic=True #allow synapses on dendrites even if there are spines
    model.param_syn._SynNMDA.spinic=True
    mod_dist_gbar(model, mod_dict[modelname])

    if block_naf:
        for k, v in model.Condset.D1.NaF.items():
            model.Condset.D1.NaF[k] = 0.0

    model.param_syn.SYNAPSE_TYPES.nmda.MgBlock.C = 1

    # create_model_sim.setupOptions(model)

    # create_model_sim.setupNeurons(model)

    # create_model_sim.setupOutput(model)

    return model


def iv_main(model, mod_dict, block_naf=False, filename=None):
    print("filename: {}".format(filename))
    import numpy as np
    from moose_nerp.prototypes import create_model_sim
    from moose_nerp.prototypes import spatiotemporalInputMapping as stim
    import moose

    model = setup_model(model, mod_dict, block_naf=block_naf, filename=filename)
    model.param_sim.plot_current = False

    create_model_sim.setupOptions(model)
    create_model_sim.setupNeurons(model)
    create_model_sim.setupOutput(model)
    create_model_sim.setupStim(model)

    create_model_sim.runAll(model)


def upstate_main(
    model,
    mod_dict,
    block_naf=False,
    num_clustered=14,
    n_per_clustered=2,
    num_dispersed=100,
    freq_dispersed=375,
    n_per_dispersed=10,
    clustered_seed=None,
    dispersed_seed=None,
    filename=None,
    do_plots=False,
    injection_current = None,
):
    import numpy as np
    from moose_nerp.prototypes import create_model_sim, tables
    from moose_nerp.prototypes import spatiotemporalInputMapping as stim
    import moose

    model = setup_model(model, mod_dict, block_naf=block_naf, filename=filename)
    create_model_sim.setupOptions(model)

    create_model_sim.setupNeurons(model)

    modelname = model.__name__.split(".")[-1]

    branch_list = ["/D1[0]/{}[0]".format(model.clusteredparent)]

    if num_clustered > 0:
        inputs = stim.exampleClusteredDistal(
            model,
            nInputs=num_clustered,
            branch_list=branch_list,
            seed=clustered_seed,  # 6,
        )
        parent_dend = [i.parent.parent for i in inputs]
        parent_spine = [i.parent for i in inputs]
        parents = parent_dend + parent_spine
        input_parent_dends = set(parents)
        # mod_local_gbar(input_parent_dends, mod_dict[modelname])

    neuron = model.neurons["D1"][0]
    bd = stim.getBranchDict(neuron)
    comps = [moose.element(comp) for comp in bd[branch_list[0]]["CompList"]]
    spines = [sp[0] for comp in comps for sp in comp.children if "head" in sp.name]
    model.param_sim.plotcomps = [
        s.split("/")[-1] for s in bd[branch_list[0]]["BranchPath"]
    ]

    create_model_sim.setupOutput(model)
    # mod_local_gbar(set(comps+spines), mod_dict[modelname])
    # from IPython import embed; embed()

    # import pdb;pdb.set_trace()
    if num_clustered > 0:
        spine_cur_tab = []
        which_spine = inputs[0].parent
        for ch in ["SKCa", "CaL13", "CaL12", "CaR", "CaT33", "CaT32", "ampa", "nmda"]:
            chan = moose.element(which_spine.path + "/" + ch)
            tab = moose.Table("data/" + chan.path.replace("/", "__").replace("[0]", ""))
            moose.connect(tab, "requestOut", chan, "getIk")
            spine_cur_tab.append(tab)

        plotgates = ["CaR", "CaT32", "CaT33", "CaL12", "CaL13"]
        model.gatetables = {}

        for plotgate in plotgates:
            model.gatetables[plotgate] = {}
            gatepath = which_spine.path + "/" + plotgate
            gate = moose.element(gatepath)
            gatextab = moose.Table("/data/" + plotgate + "_gatex")
            moose.connect(gatextab, "requestOut", gate, "getX")
            model.gatetables[plotgate]["gatextab"] = gatextab
            gateytab = moose.Table("/data/" + plotgate + "_gatey")
            moose.connect(gateytab, "requestOut", gate, "getY")
            model.gatetables[plotgate]["gateytab"] = gateytab
            if model.Channels[plotgate][0][2] > 0:
                gateztab = moose.Table("/data/" + plotgate + "_gatez")
                moose.connect(gateztab, "requestOut", gate, "getZ")
                model.gatetables[plotgate]["gateztab"] = gateztab

    dispersed_inputs = stim.dispersed(
        model,
        nInputs=num_dispersed,
        exclude_branch_list=branch_list,
        seed=dispersed_seed,
    )
    if num_clustered > 0:
        input_times = stim.createTimeTables(
            inputs, model, n_per_syn=n_per_clustered, start_time=0.3
        )
    stim.createTimeTables(
        dispersed_inputs, model, n_per_syn=10, start_time=0.35, freq=freq_dispersed, duration_limit=0.3
    )
    # c = moose.element('D1/634_3')
    # c.Rm = c.Rm*100
    if injection_current is not None:
        model.param_sim.injection_current = [injection_current]
        model.param_sim.injection_delay = 0.3
        model.param_sim.injection_width = 0.1
        create_model_sim.setupStim(model)
        #print(u'◢◤◢◤◢◤◢◤ injection_current = {} ◢◤◢◤◢◤◢◤'.format(injection_current))
        model.pg.firstLevel = injection_current
        
        #from IPython import embed; embed()

    simtime = 1.5  # 1.5
    moose.reinit()
    moose.start(simtime)

    if do_plots:
        create_model_sim.neuron_graph.graphs(model, model.vmtab, False, simtime)
        from matplotlib import pyplot as plt

        ax = plt.gca()
        ax.set_title(modelname)
        ax.axvspan(
            input_times[0], input_times[-1], facecolor="gray", alpha=0.5, zorder=-10
        )
        import pprint

        # ax.text(.5,.5,pprint.pformat(mod_dict[modelname]), transform = ax.transAxes)
        plt.ion()
        plt.show()
        plt.figure()
        for i in model.spinevmtab[0]:
            t = np.linspace(0, 0.4, len(i.vector))
            plt.plot(t, i.vector)

        # n = model.neurons["D1"][0]
        # d_vs_len = [
        #     (p, c.diameter) for c, p in zip(n.compartments, n.geometricalDistanceFromSoma)
        # ]
        # d_vs_len = np.array(d_vs_len)
        # plt.figure()
        # plt.scatter(d_vs_len[:,0],d_vs_len[:,1])

        plt.figure()

        for cur in spine_cur_tab:
            plt.plot(cur.vector, label=cur.name.strip("_"))

        plt.legend()
        # create_model_sim.plot_channel.plot_gate_params(moose.element('/library/CaT32'),3)

        # for c,d in model.gatetables.items():
        #     plt.figure()
        #     plt.title(c)
        #     for g,t in d.items():
        #         plt.plot(t.vector,label=g)
        #     plt.legend()

        # from moose_nerp.prototypes import util
        plt.show(block=True)

    tables.write_textfiles(model, 0, ca=False, spines=False, spineca=False)
    print("upstate filename: {}".format(filename))
    # return model.vmtab['D1'][0].vector
    # return plt.gcf()
    #from IPython import embed
    #embed()


def subprocess_main(function, model, mod_dict, kwds,time_limit):
    from multiprocessing import Process, Queue
    import time
    # q = Queue()
    p = Process(target=function, args=(model, mod_dict), kwargs=kwds)
    p.start()
    # result = q.get()
    # print(result)
    remaining = time_limit - time.time()
    if remaining <=0:
        p.terminate()
        return
    p.join(timeout=remaining-10)
    p.terminate()

    # return result


def mpi_main(mod_dict, sims):
    if __name__ == "__main__":
        from mpi4py import MPI
        from mpi4py.futures import MPICommExecutor
        import time
        import pickle

        with MPICommExecutor(MPI.COMM_WORLD, root=0) as executor:
            time_limit = time.time() + 60 * 60 * 8#3.75  # 3.75 hours
            
            if executor is not None:
                results = []
                make_new_params = False
                if make_new_params:
                    param_set_list = [rand_mod_dict() for i in range(2)]#10000)]
                    with open("params.pickle", "wb") as f:
                        pickle.dump(param_set_list, f)
                else:
                    with open("params.pickle",'rb') as f:
                        param_set_list = pickle.load(f)
                # print(param_set_list)
                for i, param_set in enumerate(param_set_list[:1020]):#1020
                    for key in mod_dict:
                        for sim in sims:
                            #                    param_set_1__upstate_plus_dispersed__dispersed_freq_375__D1PatchSample5_vm.txt
                            filename = (
                                "param_set_"
                                + str(i)
                                + "__"
                                + sim["name"]
                                + "__dispersed_freq_"
                                + str(sim["kwds"].get("freq_dispersed"))
                                + "__injection_current_"
                                + str(sim["kwds"].get("injection_current"))
                                + "__"
                                + key
                            )
                            kwds = {k: v for k, v in sim["kwds"].items()}
                            kwds["filename"] = filename
                            # r = p.apply_async(upstate_main, args=(key, mod_dict),kwds={'num_dispersed':0})
                            # r = p.apply_async(sim["f"], args=(key, param_set), kwds=kwds)
                            r = executor.submit(
                                subprocess_main, *(sim["f"], key, param_set, kwds, time_limit)
                            )
                            results.append(r)

                while True:
                    if all([res.done() for res in results]):
                        print('all results returned done; breaking')
                        break

                    if time.time() >= time_limit:
                        print("****************** TIME LIMIT EXCEEDED***********")
                        for res in results:
                            res.cancel()
                            #print('canceling', res)
                            
                        #executor.shutdown(wait=False)
                        print('shutting down')
                        MPI.COMM_WORLD.Abort()
                        print('aborting')
                        break
                print('done')
                return
            #while True:
            #    if time.time() >= time_limit:
            #        break
            #MPI.COMM_WORLD.Abort()

def specify_sims(sim_type,clustered_seed,dispersed_seed,single_epsp_seed):
    if sim_type=='rheobase_only':
        sims = [
            {
                "name": "rheobase_only",
                "f": upstate_main,
                "kwds": {
                    "num_dispersed": 0,
                    "block_naf": False,
                    "num_clustered": 0,
                    "clustered_seed": clustered_seed,
                    "injection_current": inj,
                },
            } for inj in np.arange(0,226e-12,25e-12)]
    elif sim_type=='upstate_plus_rheobase':
        sims = [
         {
                 "name": "upstate_plus_rheobase",
                 "f": upstate_main,
                 "kwds": {
                     "num_dispersed": 0,
                     "block_naf": False,
                     "num_clustered": 14,
                     "clustered_seed": clustered_seed,
                     "injection_current": 25e-12,
                 },
             } for inj in np.arange(0,226e-12,25e-12)]
    elif sim_type=='upstate_plus_new_dispersed_300ms':
        sims = [
             {
                 "name": "upstate_plus_new_dispersed_300ms",
                 "f": upstate_main,
                 "kwds": {
                     "num_dispersed": 100,
                     "freq_dispersed": 200,
                     "dispersed_seed": dispersed_seed,
                     "clustered_seed": clustered_seed,
                 },
             } for freq in np.arange(200,501,50)]
    elif sim_type=='new_dispersed_300ms_only':
        sims = [
            {
                "name": "new_dispersed_300ms_only",
                "f": upstate_main,
                "kwds": {
                    "num_dispersed": 100,
                    "num_clustered": 0,
                    "freq_dispersed": 250,
                    "dispersed_seed": dispersed_seed,
                    "clustered_seed": clustered_seed,
                },
            } for freq in np.arange(200,501,50)]
    elif sim_type=='upstate_only':
        sims = [
            {
                "name": "upstate_only",
                "f": upstate_main,
                "kwds": {
                    "num_dispersed": 0,
                    "block_naf": True,
                    "num_clustered": 14,
                    "clustered_seed": clustered_seed,
                },
            }]
    elif sim_type=='single_epsp':
        sims = [
            {
                "name": "single_epsp",
                "f": upstate_main,
                "kwds": {
                    "num_dispersed": 0,
                    "block_naf": True,
                    "num_clustered": 1,
                    "n_per_clustered": 1,
                    "clustered_seed": single_epsp_seed,
                },
            }]
    else:
        sims=[ {"name": "iv_curves", "f": iv_main, "kwds": {}}]
    return sims
    
if __name__ == "__main__":
    mod_dict = make_mod_dict()
    clustered_seed = 135
    dispersed_seed = 172
    single_epsp_seed = 314
    sim_type='rheobase_only'
    sims=specify_sims(sim_type,clustered_seed,dispersed_seed,single_epsp_seed)

    import sys

    args = sys.argv
    # args.append('--single')
    if len(args) > 1 and args[1] == "--single": ########### FIXME, unable to create dispersed spines ###########
        # upstate_main(list(mod_dict.keys())[0],mod_dict)
        upstate_main("D1PatchSample5", mod_dict, do_plots=True)

    elif len(args) > 1 and args[1] == "--iv":
        # upstate_main(list(mod_dict.keys())[0],mod_dict)
        iv_main("D1PatchSample5", mod_dict, filename="test")

    elif len(args) > 1 and args[1] == "--mp":
        results = []
        from multiprocessing import Pool

        with Pool(16, maxtasksperchild=1) as p:
            param_set_list = [rand_mod_dict() for i in range(10000)]

            import pickle

            with open("params.pickle", "wb") as f:
                pickle.dump(param_set_list, f)

            #print(param_set_list)
            for i, param_set in enumerate(param_set_list):
                for key in mod_dict:
                    for sim in sims:
                        # param_set_1__upstate_plus_dispersed__dispersed_freq_375__D1PatchSample5_vm.txt

                        filename = (
                            "param_set_"
                            + str(i)
                            + "__"
                            + sim["name"]
                            + "__dispersed_freq_"
                            + str(sim["kwds"].get("freq_dispersed"))
                            + "__"
                            + key
                        )
                        kwds = {k: v for k, v in sim["kwds"].items()}
                        kwds["filename"] = filename
                        # r = p.apply_async(upstate_main, args=(key, mod_dict),kwds={'num_dispersed':0})
                        r = p.apply_async(sim["f"], args=(key, param_set), kwds=kwds)
                        results.append(r)
            for res in results:
                res.wait()
    else:
        mpi_main(mod_dict, sims)
        print('done?')

