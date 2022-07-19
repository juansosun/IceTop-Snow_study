#!/usr/bin/env python

import os
if not 'I3_BUILD' in os.environ:
    raise Exception('To run this script start an IceTray environment')

from icecube import MuonGun, dataclasses, dataio, icetray, phys_services
from icecube.icetray.i3logging import *
from icecube.icetray import I3Units
from I3Tray import I3Tray
icetray.I3Logger.global_logger.set_level(icetray.I3LogLevel.LOG_INFO)
import argparse
import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str, metavar='FILE', help='I3 file')
parser.add_argument("-o", type=str, metavar='FILE', help='txt file')
args   = parser.parse_args()

#Module to grab single particles
class StoreParticleInfo(icetray.I3Module):
    def __init__(self,ctx):
        icetray.I3Module.__init__(self,ctx)

        self.FrameObject = "FrameObject"
        self.AddParameter("FrameObject", "FrameObject", self.FrameObject)

    def Configure(self):
        print("Making file", args.o)
        self.outputFile = open(args.o, "w")

        self.FrameObject = self.GetParameter("FrameObject")

    def DAQ(self, frame):
        if frame.Has(self.FrameObject):
            energyFrame = frame[self.FrameObject]
            # ~ energy_deposit = [pulses[0].charge for keys, pulses in energyFrame] 
            
            """
            =================
            Cherenkov photons
            =================
            """
            charge_CP = list()
            IceTopTankHit = frame["IceTopTankHitSeriesMap"]
            for DOM in IceTopTankHit.keys():
                for CP in IceTopTankHit[DOM]:
                    charge_CP.append(CP.charge)

            if len(charge_CP) == 0:
                charge_CP = [0,0]

            #print(charge_CP[0],",",charge_CP[1])
            #print(len(charge_CP))

            """
            =================
            Cherenkov photons
            =================
            """
            IceTopMCTree = frame["IceTopMCTree"]
            if len(IceTopMCTree)>1:
                p_xy = [IceTopMCTree[1].pos.x,IceTopMCTree[1].pos.y]
                print(p_xy[0],",",p_xy[1],",",charge_CP[0])
            
            """
            =================
            TESTS
            =================
            """

            particle = [p for p in frame["IceTopMCTree"]]
            obj = frame["IceTopMCHits"]
            #print(obj.keys())
            keys = [key for key in obj.keys()]
            #hist_dict = {ii: list() for ii in obj.keys()}
            NPE_DOMs = list()
            Hit_source_DOMS = list()
            time_DOM_1 = list()
            time_DOM_2 = list()

            for DOM in obj.keys():
                sum_NPE = 0;
                for head in obj[DOM]:
                    sum_NPE += head.npe
                    #print(head.hit_source)
                    if DOM==keys[0]:
                        time_DOM_1.append(head.time)
                    elif DOM==keys[1]:
                        time_DOM_2.append(head.time)
   
                    Hit_source_DOMS.append(head.hit_source)
                NPE_DOMs.append(sum_NPE)

            """
            =================================
                 Number of Photoelectrons
            =================================
            """
            if len(NPE_DOMs) == 0:
                NPE_DOMs = [0,0]
            elif len(NPE_DOMs) == 1: #if only one DOM detects PE, it is treated as a zero event
                NPE_DOMs = [0,0]
             #print(NPE_DOMs[0],",",NPE_DOMs[1]) // Uncomment to print NPE (csv)

            """
            =================================
                 Time of Photoelectrons
            =================================
            """
            #if len(time_DOM_1)!=0:
            #    for time in time_DOM_1:
                    #print(time)
            
            
            ## Saving to output file:
            self.outputFile.write(" {0:0.3f} {1:0.3f} {2:0.3f} {3:0.3f}".format(  particle[0].energy, particle[0].pos.x, particle[0].pos.y, particle[0].type) ) 
            self.outputFile.write("\n")

    def Finish(self):
        self.outputFile.close()



#Main loop. Reads in all the events and does the simulation
tray = I3Tray()

tray.Add('I3Reader', 'TheReader',
      FilenameList = [args.i]
      )

tray.AddModule(StoreParticleInfo, "StoreParticleInfo",
          FrameObject = "IceTopTankHitSeriesMap")

tray.Execute()
tray.Finish()
