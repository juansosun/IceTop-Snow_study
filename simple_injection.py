#!/usr/bin/env python
'''
Injects particles into tank 36A.

Type of particle, number of particles per event, and number
of events are provided as command line options.
'''

import os, sys
from os.path import expandvars
import unittest
import argparse
import random 

from I3Tray import I3Tray
from icecube import icetray, dataclasses, dataio, tableio, phys_services, simclasses, sim_services
from icecube.icetray import I3Units
from icecube import topsimulator, g4_tankresponse


parser = argparse.ArgumentParser()
parser.add_argument("-p", dest="particle", default="mu-",
                    help="particle type (see help of g4-tankresponse)")
parser.add_argument("-n", dest="nevents", type=int, default=1,
                    help="number of events")
parser.add_argument("-k", dest="nhits", type=int, default=1,
                    help="number of particle hits per event")
parser.add_argument("-t", dest="tankkey", type=str, default="36A",
                    help="TankKey/ScintKey for the particle injector")
parser.add_argument("--gcd", dest="gcd", type=str, help="GCD file",
                  default=expandvars('$I3_TESTDATA/GCD/GeoCalibDetectorStatus_IC86.55697_corrected_V2_Surface_Scintillator.i3.gz'))
parser.add_argument("-z", dest="zenith_angle_range", type=float,
                  default=0.0, help="zenith angle")
parser.add_argument("-E", dest="energy_range", type=float, 
                  default=3.0, help="initial energy")
parser.add_argument("-r", dest="max_radius", type=float, 
                  default=1.21, help="maximum radius of injection")
parser.add_argument("-of", dest="output_file", type=str, 
                  default="g4-tankresponse-test.i3", help="output file name")

args = parser.parse_args()
gcd_file = args.gcd
#expandvars('$HOME/ScintGCDFile.i3.gz')

random.seed(args.output_file)
tray = I3Tray()


tray.AddService("I3GSLRandomServiceFactory", "random_injector",
                Seed=random.randint(1,1000000),
                InstallServiceAs = "random_injector"
                )

tray.AddService("I3GSLRandomServiceFactory", "random_tankresponse",
                Seed=random.randint(1,1000000),
                InstallServiceAs = "random_tankresponse"
                )

tray.AddModule("I3InfiniteSource", "source",
               Stream=icetray.I3Frame.DAQ,
               prefix=gcd_file
               )

tray.AddService("I3InjectorFactory<I3ParticleInjector>", "injector",
                RandomServiceName='random_injector',
                NumParticles=args.nhits,
                NumEvents=args.nevents,
                ParticleType=args.particle,
                EnergyRange = [args.energy_range,args.energy_range],
                StartHeight=10.0 * I3Units.m,
                TankKeys=[args.tankkey],
                PhiRange = [0.0,360.0],
                ZenithRange   = [args.zenith_angle_range,args.zenith_angle_range],
                AzimuthRange  = [0.0, 360.0],
                RadiusRange   = [0.*I3Units.m, args.max_radius*I3Units.m] 
                )

tray.AddService("I3IceTopResponseFactory<I3G4TankResponse>", "topresponse",
                RandomServiceName="random_tankresponse",
                #VisMacro = "vis.mac",
                #ScintOutputMethod=True, # True=Photon number or False=dEdX in keV!!
                CherenkovMethod=True, # True=Photon number or False=dEdX
                UseScintillator=False
                )

# The actual topsimulator module (depends on injector- and tank
# response services)
tray.AddModule("I3TopSimulator", "top-simulator",
               InjectorServiceName="injector",
               ResponseServiceName="topresponse",
               PrimaryName="MCPrimary",
               IceTopPESeriesName="MCTopPESeriesMap",
               IceTopScintPESeriesName="",
               IceTopCherenkovHitSeriesName="IceTopTankHitSeriesMap",
               IceTopScintHitSeriesName="",
               IceTopScintHitSeriesNamePhotons="",
               InIceMCTreeName="InIceMCTree",
               IceTopMCTreeName="IceTopMCTree",
               IceTopTestPulsesName="IceTopTestPulses",
               CompressPEs=0
               )

tray.AddModule("I3Writer","i3-writer",
               filename = args.output_file,
               streams = [icetray.I3Frame.DAQ]
               )

tray.Execute()

sys.exit(0)
