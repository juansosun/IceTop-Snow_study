import numpy as np
import math
import glob    
import os    
import getpass    
import subprocess 

#=====================================================================================
ABS_PATH_HERE=str(os.path.dirname(os.path.realpath(__file__)))    
gcd =  ABS_PATH_HERE + "/GeoCalibDetectorStatus_2012.56063_V1_OctSnow.i3.gz"
n_events = 1 # number of events for z = 0°
#steps_z = 5 # steps for lists of zenith angles
#steps_E = 45 # steps for lists of zenith angles
steps_E = 1 # TEST: steps for lists of zenith angles
E_min = 0.001 # minimun energy for detected particles, i.e, photons
E_max = 1e6 # 1PeV=1e6GeV same for all injected particles
#z_range = [round(theta,3) for theta in range(0,80+steps_z,steps_z)] #list of zenith angles 
z_range = [0.0] # TEST: list of zenith angles 
E_range = [round(E,3) for E in np.linspace(E_min,E_max,steps_E)] #list of energies
#particles = ["MuMinus","MuPlus","EMinus","EPlus","Gamma"] #list of particles
particles = ["MuMinus"] # TEST: list of particles
tank_height = 1.3
snow_height = 0.379 #snow height from gcd file for tank 36A
tank_radius = 0.93
# Condor Submission
whoami = getpass.getuser() 
logDir = ABS_PATH_HERE + "/logfiles"
#=====================================================================================


def max_radius(snow_h:float,z_angle:float)->float:
    """
        This function gives the maximum radius in which a injected particle 
        could reach the tanks. It is simple geometry.
        ===============
            Input
        ===============
        - snow_h (float): snow height in meters
        - z_angle (float): zenith angle of the injected particle in degrees       
        ===============
            Output
        ===============
        - max_r (float): maximum radius in which a injected particle enter the tank
    """
    angle_rad = math.radians(z_angle)
    tan_z = math.tan(angle_rad)
    r = tan_z * (snow_h + tank_height)
    tank_rad_sim = 0.93 + 0.3 # from gcd file + sim
    max_r = tank_rad_sim + r
    max_r = round(max_r,2)

    return max_r


def output_file_name(par:str,E:float,z:float,r:float,sh:float)->str:
    """
        Simple function to make a str for the output file from the arguments
        ===============
            Input
        ===============
        - par (str): particle name
        - E (float): energy 
        - z (float): zenith angle
        - r (float): maximum radius of injected particles (see max_radius)
        - sh (float): snow height 
        ===============
            Output
        ===============
        - of_name (str): output file name
    """
    E_str = str(E)
    z_str = str(z)
    r_str = str(r)
    sh_str = str(sh)
    of_name = par+"_"+E_str+"_"+z_str+"_"+r_str+"_"+sh_str+".i3"

    return of_name

def num_events(rad:float,z:float)->str:
    #TODO: documentation
    """
        ===============
            Input
        ===============
        - rad (float): radius
        - z (float): zenith angle 
        ===============
            Output
        ===============
        - n (str): number of events
    """
    z2rad = math.radians(z)
    r = (snow_height+tank_height)*math.tan(z2rad)
    R = tank_radius + 0.3 + r
    A_a = np.pi*R**2
    A_l = math.cos(z2rad)*A_a+2*(tank_height+0.6)*(r+0.3)*math.sin(z2rad)

    final_n_events = str(int(n_events*(A_a/A_l)))

    return final_n_events


def MakeCondorSubmission(pars:list)->None:    
    #TODO: documentation
    """
        ===============
            Input
        ===============
        - pars (list): list of parameter, in total 8:
    """
    # Arguments
    gcd = pars[0] 
    p = pars[1]
    n = pars[2]
    z = pars[3]
    E = pars[4]
    r = pars[5]
    of = pars[6]
    sh  =pars[7]
    process_id = of[0:-3] #remove .i3

    # Submission
    file = open("TempSub.sub", "w")        
    file.write("#!/bin/bash\n")    
    file.write("Executable = python {}/simple_injection.py\n".format(ABS_PATH_HERE))
    file.write("Error = {0}/{1}.err\n".format(logDir, process_id))
    file.write("Output = {0}/{1}.out\n".format(logDir, process_id))
    file.write("Log = /scratch/{}/log.log\n".format(whoami))    
    file.write("request_memory = 4GB\n")    
    file.write("Arguments = --gcd {} -p {} -n {} -z {} -E {} -r {} -of {}\n".format(gcd,p,n,z,E,r,of))
    file.write("Queue 1")    
    file.close() 

def print_all(par_list:list,E_list:list,z_list:list)->None:

    for p in par_list:
        for E in E_list:
            for z_angle in z_list:
                r = max_radius(snow_height,z_angle)
                of = output_file_name(p,E,z_angle,r,snow_height)
                print("python simple_injection.py"+" --gcd "+gcd+" -p "+p+" -n "+num_events(r,z_angle)+" -z "+str(z_angle)+" -E "+str(E)+" -r "+str(r)+" -of "+of)
                args = [gcd,p,num_events(r,z_angle),str(z_angle),str(E),str(r),of,snow_height]
                MakeCondorSubmission(args)
                #subprocess.call(["condor_submit", "TempSub.sub", "-batch-name","of")
    return None

print_all(particles,E_range,z_range)
