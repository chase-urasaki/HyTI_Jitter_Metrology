import numpy as np
import scipy.signal as sp
import matplotlib.pyplot as plt
import sys


def one_sided_fft(t, x):
    full_amplitude_spectrum = np.abs(np.fft.fft(x)) / x.size
    full_freqs = np.fft.fftfreq(x.size, np.mean(np.ediff1d(t)))
    oneinds = np.where(full_freqs >= 0.0)
    one_sided_freqs = full_freqs[oneinds]
    one_sided_amplitude_spectrum = 2 * full_amplitude_spectrum[oneinds]
    return one_sided_freqs, one_sided_amplitude_spectrum


def power_spectrum(t, x):
    onef, oneamps = one_sided_fft(t, x)
    return onef, oneamps**2


def lomb_scargle_pspec(t, x):
    tstep = np.mean(np.ediff1d(t))
    freqs = np.fft.fftfreq(x.size, tstep)
    idxx = np.argsort(freqs)
    one_sided_freqs = freqs[idxx]
    one_sided_freqs = one_sided_freqs[one_sided_freqs > 0]
    one_sided_freqs += 0.00001 * np.random.random(one_sided_freqs.size)  # KLUDGE
    pgram = sp.lombscargle(t, x, one_sided_freqs * 2 * np.pi)
    return one_sided_freqs, pgram / (t.size / 4)


if __name__ == "__main__":
    # Get filename and distance from command line arguments
    if len(sys.argv) < 3:
        print("Usage: script.py <filename> <distance_in_inches>")
        sys.exit(1)
    
    fname = sys.argv[1]
    distance = float(sys.argv[2]) * 0.0254 + 35.2e-3 + 73e-3  # convert to meters

    try:
        with open(fname) as f:
            data = np.genfromtxt(f, skip_header=2, delimiter=',')
    except OSError:
        print("File", fname, "not found")
        sys.exit(1)

    tdata = data[:, 1]
    xdata = data[:, -2]
    ydata = data[:, -1]
    vsumdata = data[:, -3]

    xpsd = power_spectrum(tdata, xdata - np.mean(xdata))
    ypsd = power_spectrum(tdata, ydata - np.mean(ydata))

    xstd = np.std(xdata)
    ystd = np.std(ydata)
    vsumstd = np.std(vsumdata)

    # Calculate angular displacement
    xtheta = xdata / distance
    ytheta = ydata / distance

    xtheta_arcsec = xtheta * 206625
    ytheta_arcsec = ytheta * 206625

    xtheta_psd = power_spectrum(tdata, xtheta_arcsec - np.mean(xtheta_arcsec))
    ytheta_psd = power_spectrum(tdata, ytheta_arcsec - np.mean(ytheta_arcsec))

    xtheta_STD = np.std(xtheta_arcsec)
    ytheta_STD = np.std(ytheta_arcsec)

    # Plot frequency spectrum
    plt.figure('Frequency Spectrum')
    plt.plot(xpsd[0], xpsd[1], alpha=0.5, label='x')
    plt.plot(ypsd[0], ypsd[1], alpha=0.5, label='y')
    plt.legend()
    plt.xlabel("Frequency [Hz]")
    plt.ylabel(r'm$^2$')

    # Plot spatial position
    plt.figure('Spatial Position')
    plt.title("Laser's Position on Sensor", fontsize=16)
    plt.scatter(tdata, (xdata - np.mean(xdata)) * 1e6, label='x', alpha=0.5, s=1)
    plt.scatter(tdata, (ydata - np.mean(ydata)) * 1e6, label='y', alpha=0.5, s=1)
    plt.xlabel('Time [s]', fontsize=14)
    plt.ylabel(u'Position [\u03BCm]', fontsize=14)
    annstr = f'''Std:
        X = {xstd * 1e9:.2f} nm
        Y = {ystd * 1e9:.2f} nm 
        V = {vsumstd * 1e3:.2f} mV'''
    plt.annotate(annstr, (0.705, 0.155), xycoords='figure fraction', size=10,
                 bbox=dict(boxstyle='round', fc='white', ec='grey', alpha=0.9))
    plt.legend(loc='upper right', markerscale=3, fontsize=12)
    plt.tight_layout()

    # Plot angular displacement
    plt.figure('Angular Displacement')
    plt.title("Laser's Angular Displacement", fontsize=16)
    plt.scatter(tdata, (xtheta_arcsec - np.mean(xtheta_arcsec)), label='x [arcsec]', alpha=0.5, s=1)
    plt.scatter(tdata, (ytheta_arcsec - np.mean(ytheta_arcsec)), label='y [arcsec]', alpha=0.5, s=1)
    annstr_psd = f'''Std:
        X = {xtheta_STD:.2f} arcsec
        Y = {ytheta_STD:.2f} arcsec
        V = {vsumstd * 1e3:.2f} mV'''
    plt.annotate(annstr_psd, (0.705, 0.155), xycoords='figure fraction', size=10,
                 bbox=dict(boxstyle='round', fc='white', ec='grey', alpha=0.9))
    plt.legend(loc='upper right', markerscale=3, fontsize=12)
    plt.axhline(0.75 / distance, ls='--', c='r')
    plt.axhline(-0.75 / distance, ls='--', c='r')
    plt.xlabel('Time [s]')
    plt.ylabel('Angular Displacement [arcsec]')

    # Plot angular PSD
    plt.figure('Angular PSD')
    plt.title('PSD from Angular Displacement', fontsize=16)
    plt.plot(xtheta_psd[0], xtheta_psd[1], alpha=0.5, label='x')
    plt.plot(ytheta_psd[0], ytheta_psd[1], alpha=0.5, label='y')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel(r'arcsec$^2$')
    plt.legend(loc='upper right', markerscale=3, fontsize=12)

    plt.show()
