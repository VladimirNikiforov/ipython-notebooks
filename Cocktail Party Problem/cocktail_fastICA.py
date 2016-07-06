"""
Cocktail Party Problem solved via Independent Component Analysis.
The fastICA algorithm is implemented here, using negentropy as a measure of non-gaussianity.
"""
# Import packages.
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy import linalg as LA
from numpy.random import randn as RNDN


def g(x):
    out = np.tanh(x)
    return out


def dg(x):
    out = 1 - g(x) * g(x)
    return out

#Dimension
dim =2

# Input the data from the first receiver.
samplingRate, signal1 = wavfile.read('mic1.wav')
print "Sampling rate= ", samplingRate
print "Data type is ", signal1.dtype

# Convert the signal so that amplitude lies between 0 and 1.
# uint8 takes values from 0 through 255; sound signals are oscillatory
signal1 = signal1 / 255.0 - 0.5

# Output information about the sound samples.
a = signal1.shape
n = a[0]
print "Number of samples: ", n
n = n * 1.0

# Input data from the first receiver and standardise it's amplitude.
samplingRate, signal2 = wavfile.read('mic2.wav')
signal2 = signal2 / 255.0 - 0.5

# x is our initial data matrix.
x = [signal1, signal2]

# Plot the signals from both sources to show correlations in the data.
plt.figure()
plt.plot(x[0], x[1], '*b')
plt.ylabel('Signal 2')
plt.xlabel('Signal 1')
plt.title("Original data")

# Calculate the covariance matrix of the initial data.
cov = np.cov(x)
# Calculate eigenvalues and eigenvectors of the covariance matrix.
d, E = LA.eigh(cov)
# Generate a diagonal matrix with the eigenvalues as diagonal elements.
D = np.diag(d)

Di = LA.sqrtm(LA.inv(D))
# Perform whitening. xn is the whitened matrix.
xn = np.dot(Di, np.dot(np.transpose(E), x))

# Plot whitened data to show new structure of the data.
plt.figure()
plt.plot(xn[0], xn[1], '*b')
plt.ylabel('Signal 2')
plt.xlabel('Signal 1')
plt.title("Whitened data")
# plt.show()

# Now that we have the appropriate signal, we proceed to implement fastICA on the source signal 'x'
# Creating random weight vector
w1 = RNDN(dim, 1)
w1 = w1 / LA.norm(w1)

w0 = RNDN(dim, 1)
w0 = w0 / LA.norm(w0)

# Running the fixed-point algorithm
while (abs(abs(np.dot(np.transpose(w0), w1)) - 1) > 0.01):
    w0 = w1
    w1 = np.dot(xn, np.transpose(g(np.dot(np.transpose(w1), xn)))) / \
        n - np.transpose(np.mean(np.dot(dg(np.transpose(w1)), xn), axis=1))*w1
    w1 = w1 / LA.norm(w1)

w2 = RNDN(dim, 1)
w2 = w2 / LA.norm(w2)

w0 = RNDN(dim, 1)
w0 = w0 / LA.norm(w0)

while (abs(abs(np.dot(np.transpose(w0), w2)) - 1) > 0.01):
    w0 = w2
    w2 = np.dot(xn, np.transpose(g(np.dot(np.transpose(w2), xn)))) / \
        n - np.transpose(np.mean(np.dot(dg(np.transpose(w2)), xn), axis=1))*w2
    w2 = w2 - np.dot(np.transpose(w2), w1)*w1
    w2 = w2 / LA.norm(w2)

w = np.transpose([np.transpose(w1), np.transpose(w2)])
s = np.dot(w, x)
s1 = np.asarray(s[0], dtype=np.int16)
s2 = np.asarray(s[1], dtype=np.int16)

wavfile.write('out1.wav', samplingRate, np.transpose(s1))
wavfile.write('out2.wav', samplingRate, np.transpose(s2))