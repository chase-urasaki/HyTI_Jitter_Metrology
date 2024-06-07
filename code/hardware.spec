[T7]
    sample_freq = integer
    resolution_index = integer
    range = float(min= 0, max=10)
    channels = string_list
    settling_time = integer

[PDP90A]
    #From manual Rev L, thorlabs.com, Lx = Ly = 10 mm
    Lx = float(min=0, max = 0.015)
    Ly = float(min=0, max = 0.015)
