'VLC系统仿真器'

import numpy as np
from .signal_processing import OFDMModulator, SignalGenerator
from .channel import VLCChannel, LEDModel, Photodetector

class VLCTransmitter:
    'VLC发射机'
    def __init__(self, n_fft=64, cp_len=16, n_data_carriers=48, modulation='QPSK'):
        self.ofdm = OFDMModulator(n_fft, cp_len, n_data_carriers)
        self.modulation = modulation
        self.constellation = SignalGenerator.get_constellation(modulation)
    def transmit(self, bits):
        symbols = SignalGenerator.bits_to_symbols(bits, self.constellation)
        return self.ofdm.modulate(symbols), symbols

class VLCReceiver:
    'VLC接收机'
    def __init__(self, n_fft=64, cp_len=16, n_data_carriers=48, modulation='QPSK'):
        self.ofdm = OFDMModulator(n_fft, cp_len, n_data_carriers)
        self.modulation = modulation
        self.constellation = SignalGenerator.get_constellation(modulation)
    def receive(self, signal):
        symbols = self.ofdm.demodulate(signal)
        return SignalGenerator.symbols_to_bits(symbols, self.constellation), symbols

class VLCSystemSimulator:
    'VLC系统仿真器'
    def __init__(self, modulation='QPSK'):
        self.modulation = modulation
        self.tx = VLCTransmitter(modulation=modulation)
        self.rx = VLCReceiver(modulation=modulation)
        self.channel = VLCChannel(); self.led = LEDModel(); self.pd = Photodetector()
    def set_modulation(self, modulation):
        self.modulation = modulation
        self.tx = VLCTransmitter(modulation=modulation)
        self.rx = VLCReceiver(modulation=modulation)
    def run_simulation(self, n_bits=1024, snr_db=20, modulation=None):
        '运行VLC通信仿真'
        if modulation and modulation != self.modulation:
            self.set_modulation(modulation)
        bits_per_sym = SignalGenerator.get_bits_per_symbol(self.modulation)
        n_syms = n_bits // bits_per_sym
        n_bits = n_syms * bits_per_sym
        self.channel.snr_db = snr_db
        tx_bits = SignalGenerator.generate_random_bits(n_bits)
        ofdm_signal, tx_symbols = self.tx.transmit(tx_bits)
        optical_signal = self.led.modulate_intensity(ofdm_signal)
        electrical_signal = self.pd.detect(self.channel.apply_channel(optical_signal))
        rx_bits, rx_symbols = self.rx.receive(electrical_signal)
        min_len = min(len(tx_bits), len(rx_bits))
        ber = np.sum(tx_bits[:min_len] != rx_bits[:min_len]) / min_len if min_len > 0 else 0
        return {'tx_bits': tx_bits, 'rx_bits': rx_bits, 'tx_symbols': tx_symbols,
                'rx_symbols': rx_symbols, 'ofdm_signal': ofdm_signal,
                'optical_signal': optical_signal, 'received_signal': electrical_signal,
                'ber': ber, 'snr_db': snr_db, 'constellation': self.tx.constellation,
                'modulation': self.modulation}
    def run_ber_sweep(self, snr_range=None):
        'BER扫描测试'
        if snr_range is None: snr_range = range(0, 26, 2)
        return [self.run_simulation(n_bits=2048, snr_db=snr) for snr in snr_range]
