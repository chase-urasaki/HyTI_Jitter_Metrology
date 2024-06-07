import time
from matplotlib import pyplot as plt
import numpy as np
import helper_functions as hf
from hardware import T7, PDP90A
import shutil
import os

if __name__ == "__main__":
    config = 'hardware.ini'
    spec = 'hardware.spec'
    validated_config = hf.validate_configfile(config, spec)

    goalfreq = validated_config['T7']['sample_freq']

    print("\nEnter the number of samples (eg 5000) or time (eg 5s)  you want to take data: ")
    inpy= input()
    if "s" in inpy:
        n_samples = int(inpy.replace("s",""))*goalfreq
    else:
        n_samples = int(inpy)
        
    dist = input('Enter distance to laser [inches]: ') + 'in'

    tstamp = time.strftime("%Y%m%d-%H%M%S")

    print("Loading instruments")
    T7 = T7(**validated_config['T7'])
    PDP90A = PDP90A(**validated_config['PDP90A'])

    print("Verifing loop speed is", goalfreq, " Hz")
    realfreq = T7.test_speed()

    assert np.abs(realfreq-goalfreq)/goalfreq<0.01, " Loop speed does not match that in the configuration file"
    #assert realfreq > 100

    print("Verifying or creating output directory")
    outputdir = os.path.join(os.getcwd(), 'output_data')
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    outputsubdir = os.path.join(outputdir, dist)
    if not os.path.exists(outputsubdir):
        os.makedirs(outputsubdir)
    
    
    
    print("Taking ", n_samples, " samples")
    t0 = time.time()
    samples = T7.get_samples(n_samples = n_samples)
    t1 = time.time()
    header0 = str(n_samples)+" samples taken in "+str(t1-t0)+" seconds at "+tstamp
    print(header0)

    samplenums = np.arange(len(samples))
    #number the samples
    samplearr = np.array(samples)
    #convert to positions
    posarr = np.array([PDP90A.get_centroid(*x) for x in samples])

    data = np.vstack([samplenums, samplenums/goalfreq, samplearr.T, posarr.T]).T
    outputfile = os.path.join(outputsubdir, 'data_'+dist+'_'+tstamp+'.csv')
    header1 = "Sample number, Approx sample time[s], Xvoltage[Volts], Yvoltage[Volts], Sumvoltage[Volts], Xcentroid[meters], Ycentroid[meters]"
    column_format = ["%d"]+["%.9f"]*6
    np.savetxt(outputfile, data, fmt=column_format,
               header = header0+"\n"+header1, delimiter=',')
    #copying configuration file to output directory
    shutil.copyfile(config, os.path.join(outputsubdir, tstamp+"_"+config))
    print("Data saved to ", outputfile)
