import numpy as np


def simple_fourier_serie(signal, n_periods=1):
    times = np.linspace(0, n_periods/signal._freq, signal._e)
    a_0 = signal._coef.a_0
    a_n = np.array(signal._coef.a_n)
    b_n = np.array(signal._coef.b_n)
    n = np.array(signal._coef.index)
    # calculate serie from the fourier coeficients
    cos_part = np.array([(a_n * np.cos(n * 2 * np.pi * t)).sum() for t in times])
    sin_part = np.array([(b_n * np.sin(n * 2 * np.pi * t)).sum() for t in times])
    signal_values = a_0/2 + cos_part + sin_part
    return signal_values

def modulation(signal, carrier_freq):
    coef = signal._coef
    a_0 = coef.a_0 / 2
    a_n = np.array(coef.a_n)
    b_n = np.array(coef.b_n)
    # apply modulation
    a_n /= 2.0
    b_n /= 2.0
    a_n = np.concatenate((a_n[::-1], [a_0], a_n))
    b_n = np.concatenate((b_n[::-1], [0], b_n))
    n = np.arange(-(len(a_n)//2), 1 + (len(a_n)//2))
    index = carrier_freq + (n * signal._freq)
    # update coeficients
    coef.a_n = a_n.tolist()
    coef.b_n = b_n.tolist()
    coef.index = index.tolist()
    signal._center_freq = carrier_freq

def pass_band(signal, center_freq, bandwidth):
    coef = signal._coef
    freq = signal._freq
    freqs = np.array(coef.index)
    a_0 = coef.a_0
    a_n = np.array(coef.a_n)
    b_n = np.array(coef.b_n)
    diff = freqs - center_freq
    index = np.where(diff <= (bandwidth // 2))[-1][-1]
    center_index = np.where(freqs == center_freq)[0][0]
    lower_limit, upper_limit = int(center_index - (index - center_index)), int(index + 1) 
    lower_limit = 0 if lower_limit < 0 else lower_limit
    # apply filter
    a_n = a_n[lower_limit : upper_limit]
    b_n = b_n[lower_limit : upper_limit]
    signal._coef.a_n = a_n
    signal._coef.b_n = b_n
    index_freqs = coef.index
    signal._coef.index = index_freqs[lower_limit : upper_limit]


def insert_coef(a_n, b_n, signal):
    a_n_src = signal._coef.a_n
    b_n_src = signal._coef.b_n
    index = signal._coef.index
    for i in range(len(a_n_src)):
        freq = index[i]
        a_n[freq] = a_n.setdefault(freq, 0) + a_n_src[i]
        b_n[freq] = b_n.setdefault(freq, 0) + b_n_src[i]
        

def sum_signal(signal_1, signal_2):
    a_n = {}
    b_n = {}

    insert_coef(a_n, b_n, signal_1)
    insert_coef(a_n, b_n, signal_2)

    # get new coeficients
    a_n = sorted([coef for coef in a_n.items()], key=lambda x: x[0])
    b_n = sorted([coef for coef in b_n.items()], key=lambda x: x[0])
    freqs = list(map(lambda x: x[0], a_n))
    a_n = list(map(lambda x: x[1], a_n))
    b_n = list(map(lambda x: x[1], b_n))

    coef = signal_1._coef
    coef.a_0 = 0
    coef.a_n = a_n
    coef.b_n = b_n
    coef.index = freqs


def inverse_modulation(signal):
    center_freq = signal._center_freq
    coef = signal._coef
    a_0 = coef.a_0
    a_n = np.array(coef.a_n)
    b_n = np.array(coef.b_n)
    # apply modulation
    freqs = np.array(coef.index)
    start_index = np.where(freqs == center_freq)[0][0]
    a_n_src = coef.a_n
    b_n_src = coef.b_n
    index = coef.index
   
    a_0 = a_n_src[start_index]
    a_n_src = a_n_src[:start_index + 1]
    b_n_src = b_n_src[:start_index + 1]
    index = coef.index[:start_index + 1]

    a_n = {freq:value for freq, value in zip(coef.index, coef.a_n)}
    b_n = {freq:value for freq, value in zip(coef.index, coef.b_n)}
    for i in range(len(index)):
        freq = index[i]
        simetric_freq = center_freq + (center_freq - freq)
        a_n[simetric_freq] = a_n.setdefault(simetric_freq, 0) + a_n_src[i]
        b_n[simetric_freq] = b_n.setdefault(simetric_freq, 0) + b_n_src[i]
    
    # get new coeficients
    a_n = sorted([coef for coef in a_n.items()], key=lambda x: x[0])
    b_n = sorted([coef for coef in b_n.items()], key=lambda x: x[0])
    freqs = np.array(list(map(lambda x: x[0], a_n))) - center_freq
    a_n = list(map(lambda x: x[1], a_n))
    b_n = list(map(lambda x: x[1], b_n))
    coef.a_0 = 2 * a_0
    coef.a_n = a_n[start_index + 1:]
    coef.b_n = b_n[start_index + 1:]
    coef.index = freqs[start_index + 1:].tolist()
    signal._center_freq = 0
