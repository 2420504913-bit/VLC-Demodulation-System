# -*- coding: utf-8 -*-
'信号处理模块 - OFDM调制解调和信号变换基础功能'

import numpy as np
from scipy.fft import fft, ifft

class OFDMModulator:
    'OFDM调制器'
    def __init__(self, n_fft=64, cp_len=16, n_data_carriers=48):
        self.n_fft = n_fft
        self.cp_len = cp_len
        self.n_data_carriers = n_data_carriers
    def modulate(self, symbols):
        'OFDM调制'
        n_symbols = len(symbols) // self.n_data_carriers
        ofdm_symbols = symbols[:n_symbols * self.n_data_carriers].reshape(n_symbols, -1)
        freq_domain = np.zeros((n_symbols, self.n_fft), dtype=complex)
        freq_domain[:, 1:self.n_data_carriers+1] = ofdm_symbols
        time_domain = ifft(freq_domain, axis=1)
        cp = time_domain[:, -self.cp_len:]
        ofdm_signal = np.concatenate([cp, time_domain], axis=1)
        return ofdm_signal.flatten()
    def demodulate(self, signal):
        'OFDM解调'
        total_len = len(signal)
        symbol_len = self.n_fft + self.cp_len
        n_symbols = total_len // symbol_len
        signal = signal[:n_symbols * symbol_len].reshape(n_symbols, -1)
        time_domain = signal[:, self.cp_len:]
        freq_domain = fft(time_domain, axis=1)
        return freq_domain[:, 1:self.n_data_carriers+1].flatten()

class SignalGenerator:
    '\u6d4b\u8bd5\u4fe1\u53f7\u751f\u6210\u5668\uff0c\u652f\u6301\u591a\u79cd\u8c03\u5236\u65b9\u5f0f'
    @staticmethod
    def get_constellation(modulation='QPSK'):
        '\u6839\u636e\u8c03\u5236\u65b9\u5f0f\u8fd4\u56de\u661f\u5ea7\u70b9'
        if modulation == 'BPSK':
            return np.array([-1, 1])
        elif modulation == 'QPSK':
            return np.array([1+1j, 1-1j, -1+1j, -1-1j]) / np.sqrt(2)
        elif modulation == '16QAM':
            re = np.array([-3, -1, 1, 3])
            im = np.array([-3, -1, 1, 3])
            const = (re[:, None] + 1j * im[None, :]).flatten()
            return const / np.sqrt(np.mean(np.abs(const)**2))
        elif modulation == '64QAM':
            re = np.array([-7, -5, -3, -1, 1, 3, 5, 7])
            im = np.array([-7, -5, -3, -1, 1, 3, 5, 7])
            const = (re[:, None] + 1j * im[None, :]).flatten()
            return const / np.sqrt(np.mean(np.abs(const)**2))
        else:
            return SignalGenerator.get_constellation('QPSK')
    @staticmethod
    def qpsk_constellation():
        return SignalGenerator.get_constellation('QPSK')
    @staticmethod
    def generate_random_bits(n_bits):
        return np.random.randint(0, 2, n_bits)
    @staticmethod
    def bits_to_symbols(bits, constellation):
        n_bits_per_sym = int(np.log2(len(constellation)))
        n_symbols = len(bits) // n_bits_per_sym
        symbols = np.zeros(n_symbols, dtype=complex)
        for i in range(n_symbols):
            idx = 0
            for j in range(n_bits_per_sym):
                idx = (idx << 1) | bits[i * n_bits_per_sym + j]
            symbols[i] = constellation[idx]
        return symbols
    @staticmethod
    def symbols_to_bits(symbols, constellation):
        n_bits_per_sym = int(np.log2(len(constellation)))
        bits = np.zeros(len(symbols) * n_bits_per_sym, dtype=int)
        for i, sym in enumerate(symbols):
            distances = np.abs(sym - constellation)
            idx = np.argmin(distances)
            for j in range(n_bits_per_sym):
                bits[i * n_bits_per_sym + (n_bits_per_sym - 1 - j)] = (idx >> j) & 1
        return bits
    @staticmethod
    def get_bits_per_symbol(modulation='QPSK'):
        if modulation == 'BPSK': return 1
        if modulation == 'QPSK': return 2
        if modulation == '16QAM': return 4
        if modulation == '64QAM': return 6
        return 2

