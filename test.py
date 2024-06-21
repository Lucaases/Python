import numpy as np


samples_size = 30
duration = 0.1

symbols = np.random.uniform(-1, 1, size = samples_size).round(5)
analog_sequence = [(symbol, duration) for symbol in symbols]
print(analog_sequence)