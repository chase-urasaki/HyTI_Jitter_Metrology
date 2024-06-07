import ipdb
import time
from matplotlib import pyplot as plt
import numpy as np
import helper_functions as hf
from hardware import T7, PDP90A

def varstats(name, data):
    #prints out interesting stats about
    median = np.median(data)
    #stdev = hf.robust_sigma(data)
    stdev = np.std(data)
    return name+": "+'%.3e'%median+"+/-"+'%.3e'%stdev

def printer(results):
    trimmed_results = np.array(results[-100:])
    cxs = trimmed_results[:, 0]
    cys = trimmed_results[:, 1]
    sums = trimmed_results[:, 2]
    print(varstats("cx[meters]", cxs))
    print(varstats("cy[meters]", cys))
    print(varstats("sum[volts]", sums))
    pass

if __name__ == "__main__":
    config = 'hardware.ini'
    spec = 'hardware.spec'
    validated_config = hf.validate_configfile(config, spec)

    T7 = T7(**validated_config['T7'])
    PDP90A = PDP90A(**validated_config['PDP90A'])
    Plotter = hf.Plotter()

    resultlist = []
    i = 0
    t0 = time.time()
    while True:
        results = T7.get_data()
        #print("AIN0 : %f V, AIN1 : %f V" % (results[0], results[1]))
        x, y, sv = results
        #compute centroid
        cx, cy = PDP90A.get_centroid(x, y, sv)
        print(cx, cy)
        Plotter.update(cx, cy, sv)
        resultlist.append((cx, cy, sv))
        if i >100:
            printer(resultlist)
        i = i+1
        print("Speed: ", '%.1f'%(float(i)/(time.time()-t0)), " samples/sec")

