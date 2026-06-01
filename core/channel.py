'VLC信道仿真模块'

import numpy as np

class VLCChannel:
    '可见光通信信道模型'
    def __init__(self, snr_db=20, los_attenuation=0.7, multipath=False):
        self.snr_db = snr_db; self.los_attenuation = los_attenuation; self.multipath = multipath
    def apply_channel(self, signal):
        '应用信道效应'
        signal = signal * self.los_attenuation
        if self.multipath and len(signal) > 5:
            delays = [0, 3, 7]; gains = [1.0, 0.3, 0.1]
            filtered = np.zeros_like(signal)
            for d, g in zip(delays, gains):
                if d == 0: filtered += signal * g
                else: filtered[:-d] += signal[d:] * g
            signal = filtered
        noise_power = 10 ** (-self.snr_db / 10)
        noise = np.sqrt(noise_power / 2) * (np.random.randn(*signal.shape) + 1j * np.random.randn(*signal.shape))
        return signal + noise

class LEDModel:
    'LED光源模型'
    def __init__(self, power_mw=100, wavelength_nm=450, beam_angle_deg=120):
        self.power_mw = power_mw; self.wavelength_nm = wavelength_nm; self.beam_angle_deg = beam_angle_deg
    def modulate_intensity(self, signal):
        '强度调制'
        signal_norm = np.real(signal)
        signal_norm = (signal_norm - signal_norm.min()) / (signal_norm.max() - signal_norm.min() + 1e-10)
        return (signal_norm * 2 - 1) * 0.8 + 0.2

class Photodetector:
    '光电探测器模型'
    def __init__(self, responsivity=0.5, area_mm2=10, dark_current_nA=10):
        self.responsivity = responsivity; self.area_mm2 = area_mm2; self.dark_current_nA = dark_current_nA
    def detect(self, optical_signal):
        '光电转换'
        dark_noise = self.dark_current_nA * 1e-9 * np.random.randn(*optical_signal.shape)
        return optical_signal * self.responsivity + dark_noise
