import sys
from PyQt4 import QtGui
#from testing import say
import dwf
import time
import matplotlib.pyplot as plt
#from testing import say
import os, sys
import numpy as np
from scipy.io.wavfile import write
from scipy.io import wavfile
#import pyaudio
import wave
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
import pygame


X_MIN = 0
X_MAX = 10
Y_MIN = -1
Y_MAX = 1
#constants
HZ_ACQ = 20e3 
N_SAMPLES = 100000
X_VALS = np.linspace(0,N_SAMPLES/HZ_ACQ,100);
import random


class Window(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.playedAlready = False
        # a figure instance to plot on
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button = QtGui.QPushButton('Start')
        self.button.clicked.connect(self.plot)
        self.button2 = QtGui.QPushButton('Play')
        self.button2.clicked.connect(self.play)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        layout.addWidget(self.button2)
        self.setLayout(layout)
    

    def play(self):
          def update_line(num, line):
              i = X_VALS[num]
              line.set_data( [i, i], [Y_MIN, Y_MAX])
              return line,
          Y_MIN = min(self.new_rgdSamples)
          Y_MAX = max(self.new_rgdSamples)
          l , v = self.ax.plot(0, Y_MIN, N_SAMPLES/HZ_ACQ, Y_MAX, linewidth=2, color= 'red')
          if self.playedAlready:
            self.line_anim.frame_seq = self.line_anim.new_frame_seq()
          self.line_anim = animation.FuncAnimation(self.figure, update_line, len(X_VALS),  
                                    fargs=(l, ), interval=9*(N_SAMPLES/HZ_ACQ),
                                    blit=True, repeat=False)
          def playSound(filename):
              #pygame.mixer.music.load(filename)
              pygame.mixer.Sound.play(pygame.mixer.Sound(filename))
          here = sys.path[0]
          sound_path = os.path.join(here, "test.wav")
          pygame.init()
          playSound(sound_path)
          self.playedAlready = True

    def plot(self):
          ''' plot some random stuff '''
          # random data
          #print DWF version
          print("DWF Version: " + dwf.FDwfGetVersion())

          

          #open device
          print("Opening first device")
          dwf_ao = dwf.DwfAnalogOut()

          print("Preparing to read sample...")

          # print("Generating sine wave...")
          # dwf_ao.nodeEnableSet(0, dwf_ao.NODE.CARRIER, True)
          # dwf_ao.nodeFunctionSet(0, dwf_ao.NODE.CARRIER, dwf_ao.FUNC.SINE)
          # dwf_ao.nodeFrequencySet(0, dwf_ao.NODE.CARRIER, 1.0)
          # dwf_ao.nodeAmplitudeSet(0, dwf_ao.NODE.CARRIER, 2.0)
          # dwf_ao.configure(0, True)

          #set up acquisition
          dwf_ai = dwf.DwfAnalogIn(dwf_ao)
          dwf_ai.channelEnableSet(0, True)
          dwf_ai.channelRangeSet(0, 5.0)
          dwf_ai.acquisitionModeSet(dwf_ai.ACQMODE.RECORD)
          dwf_ai.frequencySet(HZ_ACQ)
          dwf_ai.recordLengthSet(N_SAMPLES/HZ_ACQ)

          #wait at least 2 seconds for the offset to stabilize
          time.sleep(1)

          #begin acquisition
          dwf_ai.configure(False, True)
          print("   waiting to finish")

          self.rgdSamples = []
          cSamples = 0
          fLost = False
          fCorrupted = False
          while cSamples < N_SAMPLES:
              sts = dwf_ai.status(True)
              if cSamples == 0 and sts in (dwf_ai.STATE.CONFIG,
                                           dwf_ai.STATE.PREFILL,
                                           dwf_ai.STATE.ARMED):
                  # Acquisition not yet started.
                  continue

              cAvailable, cLost, cCorrupted = dwf_ai.statusRecord()
              cSamples += cLost
                  
              if cLost > 0:
                  fLost = True
              if cCorrupted > 0:
                  fCorrupted = True
              if cAvailable == 0:
                  continue
              if cSamples + cAvailable > N_SAMPLES:
                  cAvailable = N_SAMPLES - cSamples
              
              # get samples
              self.rgdSamples.extend(dwf_ai.statusData(0, cAvailable))
              cSamples += cAvailable

          print("Recording finished")
          if fLost:
              print("Samples were lost! Reduce frequency")
          if cCorrupted:
              print("Samples could be corrupted! Reduce frequency")

          with open("record.csv", "w") as f:
              for v in self.rgdSamples:
                  f.write("%s\n" % v)
          """plt.show()"""       
          scaled = np.int16(self.rgdSamples/np.max(np.abs(self.rgdSamples)) * 32767)
          here = sys.path[0]
          sound_path = os.path.join(here, "test.wav")
          write(sound_path, 20000, scaled)
          # create an axis
          self.ax = self.figure.add_subplot(2,1,1)
          # discards the old graph
          self.ax.clear()

          # plot data
          sample_time = np.arange(len(self.rgdSamples))/HZ_ACQ
          self.new_rgdSamples = [i*1000 for i in self.rgdSamples]
          self.ax.plot(sample_time, self.new_rgdSamples)
          self.ax.set_xlabel('Time (s)')
          self.ax.set_ylabel('Voltage (mV)')

          samplingFrequency, signalData = wavfile.read('test.wav')

          self.bx = self.figure.add_subplot(2,1,2)
          self.bx.specgram(signalData,NFFT = 512, noverlap = 256, Fs=samplingFrequency,cmap = plt.cm.get_cmap("jet"))
          self.bx.set_xlabel('Time (s)')
          self.bx.set_ylabel('Frequency (Hz)')
          self.figure.subplots_adjust(hspace=0.5)
          # refreshs canvas
          self.canvas.draw()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = Window()
    # main.show()
    main.showFullScreen()

    sys.exit(app.exec_())
