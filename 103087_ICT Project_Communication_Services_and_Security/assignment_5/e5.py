import argparse
import matplotlib.pyplot as plt
import numpy as np

from dataclasses import dataclass
from aux import *

@dataclass
class Coef:
    a_0 : float
    a_n: list
    b_n: list
    index: list


class Signal:
    
    def __init__(self, freq, coef:Coef, e=10000) -> None:
        self._coef = coef
        self._freq = freq
        self._e = e
        self._center_freq = 0

    def plot_signal(self, n_periods=1, ax=None, title='', label=''):
        if ax is None:
            _, ax = plt.subplots(1, 1)
        signal = self.signal_t(n_periods)
        times = np.linspace(0, n_periods/self._freq, self._e)
        ax.plot(times, signal, label=label)
        ax.set_xlabel('Time(µs)')
        ax.set_title(title)
        ax.axhline(y=0, color='k')
        ax.grid()

    def plot_domain_freq(self, ax=None, title=''):
        if ax is None:
            _, ax = plt.subplots(1, 1)
        a_0 = self._coef.a_0
        a_n = np.array(self._coef.a_n)
        b_n = np.array(self._coef.b_n)
        freqs = self._coef.index
        X = a_n + b_n 
        if self._center_freq == 0:
            X = np.insert(X, 0, a_0)
            freqs = np.insert(freqs, 0, 0)
        ax.stem(freqs, X)
        ax.set_title(title)
        ax.set_xlabel('Freq')
        ax.grid()

    def signal_t(self, n_periods=1):
        times = np.linspace(0, n_periods/self._freq, self._e)
        a_0 = self._coef.a_0
        a_n = np.array(self._coef.a_n)
        b_n = np.array(self._coef.b_n)
        n = np.array(self._coef.index)
        # calculate serie from the fourier coeficients
        cos_part = np.array([(a_n * np.cos(n * 2 * np.pi * t)).sum() for t in times])
        sin_part = np.array([(b_n * np.sin(n * 2 * np.pi * t)).sum() for t in times])
        signal_values = a_0/2 + cos_part + sin_part
        return signal_values
    
    def set_coef(self, coef):
        self._coef = coef
    
    @property
    def coef(self):
        return self._coef
    
def signal_builder():
    n_points = 3
    period = 2 * 1/float("6e6")
    freq = 1/period
    a_0 = 0
    a_n =  [4  * np.sin(n * (np.pi/2)) / (n * np.pi) for n in range(1, n_points + 1) ]
    b_n = [0.0] * n_points
    index = [i * freq for i in range(1, n_points + 1)]
    coef = Coef(a_0, a_n, b_n, index)
    period = 2 * 1/float("6e6")
    signal = Signal(1/period, coef)
    return signal

def signal_interferen_builder():
    n_points = 5
    period = 3 * 1/float("6e6")
    freq = 1/period
    a_0 = -2/3
    a_n =  [4  * np.sin(n * (np.pi/3)) / (n * np.pi) for n in range(1, n_points + 1) ]
    b_n = [0.0] * n_points
    index = [i * freq for i in range(1, n_points + 1)]
    coef = Coef(a_0, a_n, b_n, index)
    signal = Signal(1/period, coef)
    return signal


def run_simulation(channel):
    interferent_channel_freq = float('2.412e+9') + (channel - 1) * float('5e6')
    signal = signal_builder()
    signal_interferent = signal_interferen_builder()

    # plot source signals
    fig, axs = plt.subplots(2,2, figsize=(15, 7))
    signal.plot_domain_freq(axs[0,0], title='Coef Original Signal BB')
    signal_interferent.plot_domain_freq(axs[0,1], title='Coef Interferent Signal BB')
    signal.plot_signal(n_periods=3, ax=axs[1,0], title='Original Signal Filtered')
    signal_interferent.plot_signal(n_periods=3, ax=axs[1,1], title='Interfered Signal Filtered')
    fig.tight_layout()
    plt.show()

    # apply modulations
    modulation(signal, float('2.412e+9'))
    pass_band(signal, float('2.412e+9'), float("2.0e7"))
    modulation(signal_interferent, interferent_channel_freq)
    pass_band(signal_interferent, interferent_channel_freq, float("2.0e7"))
    # plot modulations
    fig, axs = plt.subplots(2,2, figsize=(15, 7))
    signal.plot_domain_freq(axs[0,0], title='Coef Original Signal Mod')
    signal_interferent.plot_domain_freq(axs[0,1], title='Coef Interferent Signal Mod')

    # apply sum
    sum_signal(signal, signal_interferent)    
    pass_band(signal, float('2.412e+9'), float("2.0e7"))
    signal.plot_domain_freq(axs[1,0], title='Coef Original and Interferent Signal Mod')

    # invert modulation
    inverse_modulation(signal)
    signal.plot_domain_freq(axs[1,1], title='Coef Original and Interferent Signal BB')
    fig.tight_layout()
    plt.show()
    
    # plot results
    fig, axs = plt.subplots(1, 1, figsize=(15, 7))
    signal.plot_signal(ax=axs, n_periods=3, label='original + interferent')
    src_signal = signal_builder()
    src_signal.plot_signal(ax=axs, n_periods=3, label='original')
    axs.grid()
    axs.set_title('Original and Interferent Signal')
    plt.legend()
    plt.show()

def main():
    parser = argparse.ArgumentParser(
        prog='Problem 2',
        description='Run a simulation of the modulation of two signals and plot the result of the interference',
    )
    parser.add_argument('channel', help='Channel of the interferent signal')
    args = parser.parse_args()
    channel = int(args.channel)
    run_simulation(channel)
    

if __name__ == '__main__':
    main()