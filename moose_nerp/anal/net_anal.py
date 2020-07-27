import numpy as np
import glob
import mnerp_net_output as mno #must be imported first, because net_anal_utils imports from it
import net_anal_utils as nau #must be imported prior to na and isc - which import stuff from it
import net_anal_class as na
import input_spike_class as isc
import plot_utils as pu

####################################
# Parameters specifying set of files to analyze
#example 1 - ep plots

filedir='/home/avrama/moose/moose_nerp/moose_nerp/ep_net/output/'
file_root='ep'
param1=['GABA'] #condition - each of these occurs with each of the param2 sets.  
#param2 - each of these occurs with each of param1 sets.  The dictionary key is the word to use in constructing the filename and figure legends
param2=[{'PSP_':'GPe','_freq':20,'_plas':11},{'PSP_':'GPe','_freq':20,'_plas':10},{'PSP_':'str','_freq':20,'_plas':11},{'PSP_':'str','_freq':20,'_plas':10}]
suffix='_tg_GPe_lognorm*_ts_SPN_lognorm_ts_STN_lognorm'
'''
example 2: 3 conditions, but no "regular" stimulation
filedir='/home/avrama/moose/mn_output/ep_net/'
param1=['GABAosc','POST-HFSosc','POST-NoDaosc']
param2=[{'PSP_':'non','_freq':0,'_plas':1}]
suffix=''
'''
'''
#example 3 - bg network
filedir='/home/avrama/moose/moose_nerp/moose_nerp/bg_net/output/'
file_root='ctx7_Ctx_osc'
param1=['10.0_STN_lognorm28.0-fb']
param2=[{'_npas':3,'_lhx':0},{'_npas':3,'_lhx':5}]#,{'_npas':0,'_lhx':0},{'_npas':0,'_lhx':5}]
suffix='-500um'
infiles=['bg_net/Ctx10000_ramp_freq5.0_50dur0.3']
'''
#for input rasters, program will search for tt*.npy files with otherwise same name as output files
#alternatively, specify set of input files in list:
infiles=[]

# Other parameters
neur='ep' #which neuron type to analyze response to regular stimulation, calculate fft (consider eliminating neur spec) and input fire freq)
numbins=20 #number of bins (for histograms) if no overlap of bins
bin_overlap=0.5 #fraction of binsize to move for next bin, set to 1.0 for no overlap
#vmtables: may be multiple tables per neuron if single neuron sim
# or one table per neuron if network sim
#for doing FFT and STA, should only use the soma table
#specify 0 (or index of soma table if sorted alphabetically by compartment name, e.g. prior to May 21)
# or set to None to use all tables, e.g. for network sim
vmtab_index=0
maxfreq=100 #only save PSD from FFT from frequencies up to this number
#set sta_start=sta_end to avoid calculating spike triggered average
sta_start=-40e-3
sta_end=0
binsize_for_prespike_sta=(sta_end-sta_start)/numbins
entropy_bin_size=0.01 #Lavian J Neurosci used 10 ms bins
#numBinsForEnt=[int((1./freq)/entropy_bin_size)]#[2, 5, 10, 25] #set to [] to avoid calculating

#parameters to control output
raster_plots=0 #showing both input data and output spiking
individual_plots=0 #set of trials for single condition
group_plots=1 #plots comparing parameter sets
savetxt=True
calc_input_ff=True

############# loop over sets of files ##################
for cond in param1:
    for params in param2:
        key=''.join([str(k)+str(v) for k,v in params.items()])
        #### Determine dictionary keys for accumulating results of multiple parameter combos
        # assumes that either param1 or param2 has more than one entry
        # if neither has more than one entry, no need to accumulate and plot group plots
        # if both have more than one entry, ftitle will not exist - problem
        if len(param1)>1:
            accum_key=cond
        else:
            accum_key=''
            ftitle=cond
        if len(param2)>1:
            accum_key=accum_key+key
        else:
            ftitle=key
        pattern=filedir+file_root+cond+key+suffix
        files=sorted(glob.glob(pattern+'*.npz'))
        if len(files)==0:
            print('************ no files found using',pattern)
        else:
            num_trials=len(files)
        ####create network_output object for each file
        data=[]
        for f in files:
            data.append(mno.network_output(f,numbins,bin_overlap,vmtab_index))
            data[-1].spikerate_func()
        #### Now create object that contains data from set of files
        #If neurtypes and files specified before na.network_output,
        #   could create alldata, and add to alldata without appending to data above
        alldata=na.network_fileset(files,data[0].neurtypes)
        for dat in data:
            alldata.st_arrays(dat)
            if len(dat.vmdat) and sta_end>sta_start:
                dat.calc_sta(sta_start,sta_end)
                alldata.sta_array(dat)
        ######### fft requires that vm was saved
        # could be calculated for all neur types
        #if np.any([len(vm) for vm in alldata.vmdat.values()]):
        if len(alldata.vmdat[neur]):
            alldata.fft_func(neur,init_time=0.05,maxfreq=maxfreq)#edit fft to only return 1st 500 values?  Or freq up to 500 Hz?
        print('cond,params',cond,key,'num neurons',alldata.num_neurs)
        ######################################
        ######## calculate summary measures (mean, std across trials)
        ######################################
        alldata.ISI_histogram(numbins)
        alldata.spikerate_mean()
        if np.any([len(sta_set) for sta_set in alldata.sta.values()]):
            alldata.sta_mean()
            xsta={nr:alldata.time[0:len(stawave)] for nr,stawave in alldata.sta_mean.items()}
        ######## Some measures only relevant if regular stimulation
        if len(alldata.pre_post_stim): #only analyze a single neur type
            alldata.latency(neur)
            alldata.ISI_vs_time(neur)
            alldata.lat_isi_mean()
            alldata.calc_lat_shift(neur,entropy_bin_size)
        ####### transfer summary measures to dictionary to plot multiple conditions on one graph
        for indata,dictname in zip(alldata.accum_list,alldata.accum_names):
            if dictname not in vars():
                vars()[dictname]={}
            vars()[dictname]=nau.accumulate_over_params(indata,vars()[dictname],accum_key)
        ############## input files - for raster or spike triggered average input
        if not len(infiles):
            inpattern=filedir+'tt'+file_root+cond+key+suffix
            infiles=sorted(glob.glob(inpattern+'*.npy'))
        if len(infiles):
            syn_input=isc.input_spikes(infiles,alldata.sim_time)
            if calc_input_ff: #This is slow, so provide option to skip
                syn_input.input_fire_freq(neur,binsize_for_prespike_sta)
                prespike_sta,prespike_mean,prespike_std,prespike_xvals=nau.sta_fire_freq(syn_input.inst_rate,alldata.spiketimes[neur],sta_start,sta_end,syn_input.xbins)
                accum_names=syn_input.accum_names+['prespike_sta_mean','prespike_sta_std']
                accum_list=syn_input.accum_list+[prespike_mean,prespike_std]
                for indata,dictname in zip(accum_list,accum_names):
                    if dictname not in vars():
                        vars()[dictname]={}
                    vars()[dictname]=nau.accumulate_over_params(indata,vars()[dictname],accum_key)
        ###################################################
        ######## Single parameter set plots
        ###################################################
        if individual_plots:
            pu.plot_dict_of_dicts(alldata.isi_hist_mean,alldata.isihist_bins,ylabel='counts',std_dict=alldata.isi_hist_std,xlabel='ISI (sec)',ftitle=cond+' '+key)
            #pu.plot_dict(alldata.spikerate_mean,alldata.ratebins,ylabel='Spike Rate (Hz)',std_dict=alldata.spikerate_std,ftitle=cond+key)
            if len(alldata.pre_post_stim):
                pu.plot_dict(alldata.isi_time_mean,alldata.timebins[neur],std_dict=alldata.isi_time_std,ylabel='counts',ftitle='ISI '+cond+key)
                pu.plot_dict(alldata.lat_mean,alldata.pre_post_stim[neur],std_dict=alldata.lat_std,ylabel='Latency (sec)',ftitle=cond+key)
            if len(alldata.vmdat[neur]):
                pu.fft_plot(alldata,maxfreq=60,title=cond+key,mean_fft=True) #COMPARE TO ELIFE
                pu.plot_dict(alldata.sta_mean,xsta,std_dict=alldata.sta_std,ylabel='Vm (Volts)',ftitle='STA '+cond+' '+key)
        if raster_plots:
            pu.plot_raster(syn_input.spiketimes[0],alldata.sim_time[neur],ftitle='output '+cond+key)
            pu.plot_raster(alldata.spiketimes,alldata.sim_time[neur],syntt=dat.syntt_info,ftitle='input '+cond+key)
#####################
# plots comparing data across param2
#####################
if group_plots:
    rate_xvals=sorted([bin[0] for binset in alldata.timebins[neur].values() for bin in binset ]) #list
    pu.plot_dict_of_dicts(spikerate_mean,xarray=rate_xvals,ylabel='Hz',std_dict=spikerate_std,ftitle='spike rate: '+ftitle) #COMPARE TO ELIFE (CTRL)
    elph_xvals=np.linspace(0,alldata.sim_time[neur],np.shape(alldata.spikerate_elph[neur])[1]) #array
    pu.plot_dict_of_dicts(spikerate_elphmean,xarray=elph_xvals,ylabel='Hz',std_dict=spikerate_elphstd,ftitle='ELPH spike rate: '+ftitle,trials=num_trials) #COMPARE TO ELIFE (CTRL)
    hist_xvals={p:{k:[bin for bin in binset] for k,binset in alldata.isihist_bins[neur].items()} for p in isihist_mean[neur].keys()} #dict of dicts
    pu.plot_dict_of_dicts(isihist_mean[neur],std_dict=isihist_std[neur],xarray=hist_xvals,xlabel='ISI (sec)',ylabel='count',ftitle='ISI histogram: '+ftitle)
    if 'sta_mean' in vars():
        pu.plot_dict_of_dicts(sta_mean,xarray=xsta,ylabel='Vm (V)',std_dict=sta_std,ftitle='STA: '+ftitle)
    if 'inputrate_mean' in vars():
        pu.plot_dict_of_dicts(inputrate_mean,xarray=syn_input.xbins,ylabel='Hz',std_dict=inputrate_std,ftitle='Input firing rate')
        pu.plot_dict_of_dicts(prespike_sta_mean,xarray=prespike_xvals,ylabel='Firing Rate (Hz)',std_dict=prespike_sta_std,ftitle='STA Input: '+ftitle)
    if 'mean_fft' in vars():
        pu.plot_dict_of_epochs(mean_fft,std_dict=std_fft,xarray=alldata.freqs,ylabel='PSD',xlabel='Frequency (Hz)', ftitle='PSD: '+ftitle)
    if len(alldata.pre_post_stim):
        stim_xvals={k: [val[0] for val in values] for k,values in alldata.timebins[neur].items()}
        pu.plot_dict_of_epochs(lat_mean,std_dict=lat_std,xarray=stim_xvals,ylabel='latency',ftitle='latency: '+ftitle)
        pu.plot_dict_of_epochs(isi_time_mean,std_dict=isi_time_std,xarray=stim_xvals,ylabel='mean ISI',ftitle='mean isi: '+ftitle)
        pu.plot_dict_of_dicts(entropy,ylabel='bits',ftitle='entropy: '+ftitle)
########################################## Write output to file for generating nicer plots 
if savetxt:
    nau.write_dict_of_dicts(spikerate_mean,rate_xvals,'spike_rate','rate',spikerate_std) 
    nau.write_dict_of_dicts(spikerate_elphmean,elph_xvals,'elph_spike_rate','Erate',spikerate_elphstd)
    nau.write_triple_dict(isihist_mean,'isi_histogram','isiN',isihist_std,xdata=hist_xvals,xheader='isi_bin') #possibly delete triple dict and loop over neur type?
    nau.write_dict_of_dicts(sta_mean,xsta,'sta_vm','stavm',sta_std)
    nau.write_dict_of_dicts(prespike_sta_mean,prespike_xvals,'sta_spike','stapre',prespike_sta_std)
    nau.write_dict_of_dicts(mean_fft,alldata.freqs,'fft','fft',std_fft,xheader='freq') #this may need triple dict if do fft for multiple neur types
    if len(alldata.pre_post_stim):
        #x values will be the same for all data.  Possibly concatenate pre, post and stim?  write_dict_of_epochs.
        num_conditions=len(param1)*len(param2)
        nau.write_dict_of_epochs(lat_mean,stim_xvals,'latency','lat',num_conditions,stddata=lat_std) 
        nau.write_dict_of_epochs(isi_time_mean,stim_xvals,'isi_time','itiT_N',num_conditions,stddata=isi_time_std)
        ent_xvals=sorted([v for val in stim_xvals.values() for v in val])
        nau.write_dict_of_dicts(entropy,ent_xvals,'entropy','ent')

'''
NEXT:
2c: latency vs latency phase - check calculation - compare with previous code, change from % to / for phase?
3. Edit fft func to allow multiple neurons per type (possibly create new function?)
'''
