# -*- coding: utf-8 -*-

from moose_nerp.prototypes.util import NamedDict
from moose_nerp.prototypes.chan_proto import (
    AlphaBetaChannelParams,
    StandardMooseTauInfChannelParams,
    TauInfMinChannelParams,
    ZChannelParams,
    BKChannelParams,
    ChannelSettings,
    TypicalOneD,
    TwoD,
    )

#contains all gating parameters and reversal potentials
# Gate equations have the form:
# AlphaBetaChannelParams (specify forward and backward transition rates):
# alpha(v) or beta(v) = (rate + B * v) / (C + exp((v + vhalf) / vslope))
# OR
# StandardMooseTauInfChannelParams (specify steady state and time constants):
# tau(v) or inf(v) = (rate + B * v) / (C + exp((v + vhalf) / vslope))
# OR
# TauInfMinChannelParams (specify steady state and time constants with non-zero minimum - useful for tau):
# inf(v) = min + max / (1 + exp((v + vhalf) / vslope))
# tau(v) = taumin + tauVdep / (1 + exp((v + tauVhalf) / tauVslope))
# or if tau_power=2: tau(v) = taumin + tauVdep / (1 + exp((v + tauVhalf) / tauVslope))* 1 / (1 + exp((v + tauVhalf) / -tauVslope))
#
# where v is membrane potential in volts, vhalf and vslope have units of volts
# C, min and max are dimensionless; and C should be either +1, 0 or -1
# Rate has units of per sec, and B has units of per sec per volt
# taumin and tauVdep have units of per sec
#

#units for membrane potential: volts
clrev=-60e-3
krev=-90e-3
narev=50e-3
carev=140e-3 #assumes CaExt=2 mM and CaIn=50e-3
ZpowCDI=2

VMIN = -120e-3
VMAX = 50e-3
VDIVS = 3401 #0.5 mV steps

#units for calcium concentration: mM
CAMIN = 0.01e-3   #10 nM
CAMAX = 40e-3  #40 uM, might want to go up to 100 uM with spines
CADIVS = 4001 #10 nM steps

#mtau: Ogata fig 5, no qfactor accounted in mtau, 1.2 will improve spike shape
#activation minf fits Ogata 1990 figure 3C (which is cubed root)
#inactivation hinf fits Ogata 1990 figure 6B
#htau fits the main -50 through -10 slope of Ogata figure 9 (log tau), but a qfact of 2 is already taken into account.

qfactNaF = 2.5

Na_m_params = TauInfMinChannelParams(SS_min = 0.0,
                                     SS_vdep = 1.0,
                                     SS_vhalf = -25e-3,
                                     SS_vslope = -10e-3,
                                     T_min = 0.1e-3/qfactNaF,
                                     T_vdep = 2.1025e-3/qfactNaF,
                                     T_vhalf = -62e-3,
                                     T_vslope = 8e-3,
                                     T_power=2)

Na_h_params = TauInfMinChannelParams(T_min = 2*0.2754e-3/qfactNaF,
                                     T_vdep = 2*1.2e-3/qfactNaF,
                                     T_vhalf = -42e-3,
                                     T_vslope = 3e-3,
                                     SS_min = 0.0,
                                     SS_vdep = 1.0,
                                     SS_vhalf = -60e-3,
                                     SS_vslope = 6e-3)

NaFparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=narev, name='NaF')

Kirparam = ChannelSettings(Xpow=1, Ypow=0, Zpow=0, Erev=krev, name='Kir')
qfactKir = 1

Kir_X_params = AlphaBetaChannelParams(A_rate = 0.008*qfactKir,
                                      A_B = 0,
                                      A_C = 0.0,
                                      A_vhalf = 0,
                                      A_vslope = 11.0e-3,
                                      B_rate = 1000*qfactKir,
                                      B_B = 0.0,
                                      B_C = 1.0,
                                      B_vhalf = -40e-3,
                                      B_vslope = -40e-3)

KaFparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KaF')

# activation constants for alphas and betas (obtained by
# matching m2 to Tkatch et al., 2000 Figs 2c, and mtau to fig 2b)

qfactKaF = 10
KaF_X_params = AlphaBetaChannelParams(A_rate = 1.8e3*qfactKaF,
                                      A_B = 0,
                                      A_C = 1.0,
                                      A_vhalf = 18e-3,
                                      A_vslope = -13.0e-3,
                                      B_rate = 0.45e3*qfactKaF,
                                      B_B = 0.0,
                                      B_C = 1.0,
                                      B_vhalf = -2.0e-3,
                                      B_vslope = 11.0e-3)

#inactivation consts for alphas and betas obtained by matching Tkatch et al., 2000 Fig 3b,
#and tau voltage dependence consistent with their value for V=0 in fig 3c.
#slowing down inact improves spike shape tremendously
KaF_Y_params = AlphaBetaChannelParams(A_rate = 0.105e3*qfactKaF,
                                      A_B = 0,
                                      A_C = 1.0,
                                      A_vhalf = 121e-3,
                                      A_vslope = 22.0e-3,
                                      B_rate = 0.065e3*qfactKaF,
                                      B_B = 0.0,
                                      B_C = 1.0,
                                      B_vhalf = 55.0e-3,
                                      B_vslope = -11.0e-3)

#KaS based on Shen 2004 data and Wolf 2005 model code. Note that the Wolf model
#code on ModelDB notes that, via personal correspondance with Shen 2004 author,
#parameters in Shen 2004 were misreported, and are subsequently corrected in
#the Wolf 2005 code. Alpha/Beta channel params were fit to be similar to the
#Wolf steady state and tau equations--see fitKaS.py for fitting script.
#Note: Fit looks ok with these parameters but could stand to be improved.
KaSparam = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=krev, name='KaS')
qfactKaS = 1 # Shen 2004/Wolf 2005
KaS_X_params = AlphaBetaChannelParams(A_rate = 22057.0306*qfactKaS,
                                      A_B = 0.*qfactKaS,
                                      A_C = 1,
                                      A_vhalf = -0.08789675579999999,
                                      A_vslope = -0.0162951634,
                                      B_rate = 348021313.0*qfactKaS,
                                      B_B = 0.*qfactKaS,
                                      B_C = 1,
                                      B_vhalf =0.39822177799999997,
                                      B_vslope = 0.0218235302)

KaS_Y_params = AlphaBetaChannelParams(A_rate = 25644952.0*qfactKaS,
                                      A_B = 0.*qfactKaS,
                                      A_C = 1.0,
                                      A_vhalf = 1.222,
                                      A_vslope = 0.0645391447,
                                      B_rate = 1.28951669*qfactKaS,
                                      B_B = 0.*qfactKaS,
                                      B_C = 1.0,
                                      B_vhalf = 0.000635602802,
                                      B_vslope = -0.0262013787)

#SS values from Churchill and MacVicar, assuming Xpow = 1
##time constants extrapolated from scarce measurements - Song & Surmeier
#SS values measured by Kasai and Neher are quite similar, except
#they use Xpow=2 to fit, thus params would be different
#they have nice time constant measurements which are ~2x slower than above
#but they measured at room temp, so qfact=1 on S&S and qfact=2 on K&N would equate them
#Vdep inact by Kasai ~10% and very slow (>50 ms). For now, have no Vdep inact.
# CDI measured by Kasai
#Note that CaL13 for D1 has mvhalf 10 mV more negative than for D2
#CaL12 does not differ between D1 and D2.
CaL12param = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=carev, name='CaL12')
qfactCaL = 2

CaL12_X_params =AlphaBetaChannelParams(A_rate = -220e3* 4.0003e-3 *qfactCaL,
                                         A_B = -220e3*qfactCaL,
                                         A_C = -1.0,
                                         A_vhalf = 4.0003e-3,
                                         A_vslope = -8e-3,
                                         B_rate = 71e3* -4.0003e-3 *qfactCaL,
                                         B_B = 71e3*qfactCaL,
                                         B_C = -1.0,
                                         B_vhalf = -4.0003e-3,
                                         B_vslope = 5e-3)


CaL12_Y_params = TauInfMinChannelParams(T_min = 44.3e-3/qfactCaL,
                                        T_vdep = 0,
                                        T_vhalf = 4.0003e-3,
                                        T_vslope = -7.5e-3,
                                        SS_min = 0.83,
                                        SS_vdep = 0.17,
                                        SS_vhalf = -55.000e-3,
                                        SS_vslope = 8e-3)

# Using Xpow=1 produced too high a basal calcium,
# so used Xpow=2 and retuned params - much better basal calcium
CaL13param = ChannelSettings(Xpow=2, Ypow=1, Zpow=0, Erev=carev, name='CaL13')

CaL13_X_params = AlphaBetaChannelParams(A_rate = 1500*qfactCaL,
                                        A_B = 0*qfactCaL,
                                        A_C = 1,
                                        A_vhalf =- 5.e-3,
                                        A_vslope = -18e-3,
                                        B_rate = 2000*qfactCaL,
                                        B_B = 0*qfactCaL,
                                        B_C = 1.0,
                                        B_vhalf = 52.e-3,
                                        B_vslope = 8.e-3)
CaL13_Y_params = TauInfMinChannelParams(T_min = 44.3e-3/qfactCaL,
                                        T_vdep = 0,
                                        T_vhalf = 37.0e-3,
                                        T_vslope = 5.0e-3,
                                        SS_min =  0,
                                        SS_vdep = 1,
                                        SS_vhalf = -37e-3,
                                        SS_vslope = 5.e-3)
#Params from McRory J Biol Chem, alpha1I subunit
# CaN SS parameters tuned so m2 fits Bargas and Surmeier 1994 boltzmann curve
# CaN tau from kasai 1992.
# Kasai measures calcium dependent inactivation
#McNaughton has act and inact, tau and ss for human CaN
# CaR SS (Act and Inact) parameters from Foerhing et al., 2000
# Was Xpow=3 taken into account during fit?
# CaR tau from a few measurements from pyramidal neurons by Foerhing
# CaR inact tau from Brevi 2001
#Inact params are a bit too steep for ss, and not steep enough for tau
CaRparam = ChannelSettings(Xpow=3, Ypow=1, Zpow=0, Erev=carev, name='CaR')
qfactCaR = 2
CaR_X_params = AlphaBetaChannelParams(A_rate = 240*qfactCaR,
                                      A_B =    0,
                                      A_C =  0.0,
                                      A_vhalf =  0.0,
                                      A_vslope = -28.0e-3,
                                      B_rate = 8e6* 158e-3 *qfactCaR,
                                      B_B = 8e6*qfactCaR,
                                      B_C = -1.0,
                                      B_vhalf = 158e-3,
                                      B_vslope = 13.6e-3)

CaR_Y_params = AlphaBetaChannelParams(A_rate = 10000 * 0.11,
                                      A_B = 10000,
                                      A_C = -1.0,
                                      A_vhalf = 0.11,
                                      A_vslope = 17e-3,
                                      B_rate =20,
                                      B_B = 0,
                                      B_C = 0.0,
                                      B_vhalf = 0.0,
                                      B_vslope = -30.0e-3)

#Dictionary of "standard" channels, to create channels using a loop
#NaF doesn't fit since it uses different prototype form
#will need separate dictionary for BK

Channels = NamedDict(
    'Channels',
    KaF =   TypicalOneD(KaFparam, KaF_X_params, KaF_Y_params),
    KaS =   TypicalOneD(KaSparam, KaS_X_params, KaS_Y_params),
    Kir =   TypicalOneD(Kirparam,  Kir_X_params, []),
    CaL12 = TypicalOneD(CaL12param,CaL12_X_params, CaL12_Y_params, calciumPermeable=True),
    CaL13 = TypicalOneD(CaL13param, CaL13_X_params,CaL13_Y_params, calciumPermeable=True),
    CaR =   TypicalOneD(CaRparam, CaR_X_params, CaR_Y_params, calciumPermeable=True),
    NaF =   TypicalOneD(NaFparam, Na_m_params, Na_h_params),
)
