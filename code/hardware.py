from labjack import ljm
import helper_functions as hf
import time

class PDP90A:
    def __init__(self, Lx, Ly):
        self.Lx = Lx
        self.Ly = Ly

    def get_centroid(self, deltax, deltay, sumvolts):
        denom = 2*sumvolts
        return self.Lx*deltax/denom, \
               self.Ly*deltay/denom

class T7:
    def __init__(self,
                 sample_freq = None,
                 resolution_index = None,
                 range = None,
                 channels = None,
                 settling_time = None):

        self.handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
        self.info = ljm.getHandleInfo(self.handle)
        print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
              "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
              (self.info[0], self.info[1], self.info[2],
              ljm.numberToIP(self.info[3]), self.info[4], self.info[5]))
        self.sample_freq = sample_freq
        self.resolution_index = resolution_index
        self.range = range
        self.channels = channels
        self.settling_time = settling_time
        self.names = self.configure_names()
        self.aValues = self.configure_values()
        self.writeNumFrames = len(self.names)
        self.readNumFrames = len(self.channels)
        #Set T7 Mode from parameters above.
        ljm.eWriteNames(self.handle, self.writeNumFrames, self.names, self.aValues)
        #User-defined interval identifier (can be anything)
        self.intervalHandle = 1
        #sets the number of microseconds in the interval
        ljm.startInterval(self.intervalHandle, int(1e6/self.sample_freq))  # Delay between readings (in microseconds)

    def configure_names(self):
        #takes the names and puts them in the correct syntax to program the T7
        #returns a list
        suffixes = ["_NEGATIVE_CH", "_RANGE", "_RESOLUTION_INDEX", "_SETTLING_US"]
        output_names= []
        for channel in self.channels:
            for suffix in suffixes:
                output_names.append(channel+suffix)
        return output_names

    def configure_values(self):
        #sets the values corresponding to configure_names in the proper config
        output_vals = [199, self.range, self.resolution_index, self.settling_time]
        #repeat these values for each channel
        return output_vals*len(self.channels)

    def get_data(self):
        #returns a single data point
        results = ljm.eReadNames(self.handle, self.readNumFrames, self.channels)
        ljm.waitForNextInterval(self.intervalHandle)
        return results

    def test_speed(self, n_samples=1000):
        #tests the speed of the loop by taking n_samples
        t0=time.time()
        self.get_samples(n_samples)
        t1 = time.time()
        print(str(n_samples)+" samples read in ", t1-t0, " seconds")
        freq = n_samples/(t1-t0)
        print("Loop speed: ", freq, " Hz")
        return freq

    def get_samples(self, n_samples=1000):
        #returns n_samples from teh machine
        i = 0
        output = []
        while i<n_samples:
            results = ljm.eReadNames(self.handle, self.readNumFrames, self.channels)
            ljm.waitForNextInterval(self.intervalHandle)
            if i % 1000 == 0:
                print(i)
            output.append(results)
            i = i + 1
        return output

if __name__ == "__main__":
    config = 'hardware.ini'
    spec = 'hardware.spec'
    validated_config = hf.validate_configfile(config, spec)
    T7 = T7(**validated_config['T7'])
