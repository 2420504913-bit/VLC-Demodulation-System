import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os

class AIDemodulator:
    'AI\u667a\u80fd\u89e3\u8c03\u5668 - \u57fa\u7840MLP\u6a21\u578b'
    def __init__(self, model_type='MLP', modulation='QPSK'):
        self.model = None
        self.scaler = StandardScaler()
        self.trained = False
        self.model_type = model_type
        self.modulation = modulation
        self.constellation = self._get_constellation()
        self._init_model()
        
    def _get_constellation(self):
        from .signal_processing import SignalGenerator
        return SignalGenerator.get_constellation(self.modulation)
        
    def _init_model(self):
        if self.model_type == 'MLP':
            self._model_fn = MLPClassifier(
                hidden_layer_sizes=(64, 32), activation='relu',
                solver='adam', max_iter=500, random_state=42
            )
        elif self.model_type == 'CNN':
            # CNN-style: wider layers + dropout-like regularization
            self._model_fn = MLPClassifier(
                hidden_layer_sizes=(128, 64, 32), activation='relu',
                solver='adam', max_iter=800, random_state=42,
                alpha=0.001
            )
        elif self.model_type == 'LSTM':
            # LSTM-style: deeper sequential processing
            self._model_fn = MLPClassifier(
                hidden_layer_sizes=(96, 48, 48, 24), activation='tanh',
                solver='adam', max_iter=1000, random_state=42,
                learning_rate_init=0.005
            )
        else:
            self._model_fn = MLPClassifier(
                hidden_layer_sizes=(64, 32), activation='relu',
                solver='adam', max_iter=500, random_state=42
            )
        
    def _extract_features(self, symbols, model_type=None):
        '\u63d0\u53d6\u4fe1\u53f7\u7279\u5f81'
        mt = model_type or self.model_type
        features = []
        for i, sym in enumerate(symbols):
            base = [
                np.real(sym), np.imag(sym), np.abs(sym),
                np.angle(sym), np.real(sym)**2 + np.imag(sym)**2
            ]
            if mt == 'CNN':
                # Add convolution-like features (neighborhood differences)
                base.append(np.real(sym) * np.imag(sym))
                if i > 0:
                    base.append(np.real(sym) - np.real(symbols[i-1]))
                    base.append(np.imag(sym) - np.imag(symbols[i-1]))
                else:
                    base.append(0.0)
                    base.append(0.0)
                if i < len(symbols) - 1:
                    base.append(np.real(sym) - np.real(symbols[i+1]))
                    base.append(np.imag(sym) - np.imag(symbols[i+1]))
                else:
                    base.append(0.0)
                    base.append(0.0)
            elif mt == 'LSTM':
                # Add sequential/temporal features
                if i > 0:
                    base.append(np.angle(sym) - np.angle(symbols[i-1]))
                    base.append(np.abs(sym) - np.abs(symbols[i-1]))
                else:
                    base.append(0.0)
                    base.append(0.0)
                if i < len(symbols) - 1:
                    base.append(np.angle(symbols[i+1]) - np.angle(sym))
                    base.append(np.abs(symbols[i+1]) - np.abs(sym))
                else:
                    base.append(0.0)
                    base.append(0.0)
            features.append(base)
        return np.array(features)
    
    def set_modulation(self, modulation):
        self.modulation = modulation
        self.constellation = self._get_constellation()
        if self.trained:
            self.trained = False
            self.model = None
    
    def train(self, train_data, train_labels):
        '\u8bad\u7ec3AI\u89e3\u8c03\u6a21\u578b'
        features = self._extract_features(train_data)
        features = self.scaler.fit_transform(features)
        self._init_model()
        self._model_fn.fit(features, train_labels)
        self.model = self._model_fn
        self.trained = True
        return self.model
        
    def demodulate(self, received_symbols):
        'AI\u667a\u80fd\u89e3\u8c03'
        if not self.trained:
            return self._demodulate_baseline(received_symbols), np.ones(len(received_symbols)) * 0.85
        features = self._extract_features(received_symbols)
        features = self.scaler.transform(features)
        predictions = self.model.predict(features)
        probs = self.model.predict_proba(features)
        confidence = np.max(probs, axis=1)
        return predictions, confidence
    
    def _demodulate_baseline(self, symbols):
        '\u57fa\u51c6\u89e3\u8c03\uff08\u6700\u5c0f\u8ddd\u79bb\u5224\u51b3\uff09'
        predictions = []
        for sym in symbols:
            distances = np.abs(sym - self.constellation)
            predictions.append(np.argmin(distances))
        return np.array(predictions)
