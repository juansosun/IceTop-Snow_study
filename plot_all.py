import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-if",dest="inputFile", help="Path to the csv file used to plot", type=str)
parser.add_argument("-of",dest="outputFile", help="Name of the output file", type=str, default="output_plot.pdf")
parser.add_argument("-npeCounts",dest="npeCounts", help="Boolean for NPE counts plots", type=bool, default=False)
parser.add_argument("-npeTime",dest="npeTime", help="Boolean for NPE times plots", type=bool, default=False)
parser.add_argument("-cpCounts",dest="cpCounts", help="Boolean for Cherenkov photons counts plots", type=bool, default=False)
parser.add_argument("-cpPos",dest="cpPos", help="Boolean for Cherenkov photons position plots", type=bool, default=False)
args = parser.parse_args()

########################################################################
data = pd.read_csv(args.inputFile, header = None) # from csv to pd
if args.npeCounts:
    
    #REMEMBER: Events in which only one DOM detected a PE were dropped    
    OM = input("Enter 1 for the first OM in your i3 file or 2 for the second one: ")   
    data.columns = ["NPE: OM1","NPE: OM2"]
    NPE_data = data["NPE: OM"+OM].to_list()

    NPE_data_zero = [ii for ii in NPE_data if ii==0]
    NPE_data_non_zero = [ii for ii in NPE_data if ii!=0]

    print("====================================================")
    print("Total number of events: ", len(NPE_data))
    print("Total number of non-zero evts:", len(NPE_data_non_zero))
    print("Total number of zero evts:", len(NPE_data_zero))
    print("====================================================")

    plt.grid(True,linewidth=0.1,linestyle="--")
    plt.xlabel("Number of Photoelectrons")
    plt.ylabel("Counts")
    plt.hist(NPE_data_non_zero,bins = np.linspace(-0.5, 270.5, 272), label=r"Pars: $\theta = 0^{\circ}$, $E=3$GeV, id$=\mu^{-}$", color="green")
    plt.legend()
    plt.savefig(args.outputFile)
elif args.npeTime:
    #Only times for one DOM
    data.columns = ["PE time"]
    PE_time = data["PE time"].to_list()
    plt.grid(True,linewidth=0.1,linestyle="--")
    plt.xlabel("PE time")
    plt.ylabel("Counts")
    plt.hist(PE_time,bins = 50, color="green")
    plt.savefig(args.outputFile)    
elif args.cpCounts:
    
    OM = input("Enter 1 for the first OM in your i3 file or 2 for the second one: ")   
    data.columns = ["CP: OM1","CP: OM2"]
    CP_data = data["CP: OM"+OM].to_list()

    CP_data_zero = [ii for ii in CP_data if ii==0]
    CP_data_non_zero = [ii for ii in CP_data if ii!=0]

    print("====================================================")
    print("Total number of events: ", len(CP_data))
    print("Total number of non-zero evts:", len(CP_data_non_zero))
    print("Total number of zero evts:", len(CP_data_zero))
    print("====================================================")

    plt.grid(True,linewidth=0.1,linestyle="--")
    plt.xlabel("Number of Cherenkov photons")
    plt.ylabel("Counts")
    plt.hist(CP_data_non_zero,bins = 2000, label=r"Pars: $\theta = 0^{\circ}$, $E=3$GeV, id$=\mu^{-}$", color="green", range = (0,75000))
    """
    (n, bins, patches) = plt.hist(CP_data_non_zero,bins = 2000, label=r"Pars: $\theta = 0^{\circ}$, $E=3$GeV,id$=\mu^{-}$", color="green", range = (0,75000))
    bins = list(bins)
    n = list(n)
    max_n = max(n)
    idx_max_n = n.index(max_n)
    """
    #print(bins[idx_max_n])
    plt.legend()
    plt.yscale('log')
    plt.savefig(args.outputFile)
elif args.cpPos:
    data.columns = ["par: x","par: y","CP: counts"]
    par_x = data["par: x"]
    par_y = data["par: y"]
    CP_counts = data["CP: counts"]

    cm = plt.cm.get_cmap('RdYlBu')
    sc = plt.scatter(par_x, par_y, c=CP_counts, cmap=cm,label=r"Pars: $\theta = 0^{\circ}$, $E=3$GeV, id$=\mu^{-}$")
    x1,x2,y1,y2 = plt.axis()  
    plt.axis((x1,x2,-57.8,-56.8))
    plt.axvline(x = 38.365, color = 'g', label = 'Tank edge',linewidth=1)
    plt.colorbar(sc)
    plt.grid(True,linewidth=0.1,linestyle="--")
    plt.xlabel("Particle x [m]")
    plt.ylabel("Particle y [m]")
    plt.legend()
    plt.savefig(args.outputFile)
