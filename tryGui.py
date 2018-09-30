from GUI import Window, Button, Font, application
from GUI.StdFonts import system_font
from GUI.StdColors import red, black
from testing import say
import dwf
import time
import matplotlib.pyplot as plt
from GUI import Window, View, Image, application
from GUI.Geometry import offset_rect, rect_sized
from GUI.StdColors import yellow
from testing import say
import os, sys
import numpy as np
from scipy.io.wavfile import write
import pyaudio
import wave

rgdSamples = []

class TWindow(Window):

    def key_down(self, e):
        say(e)
        Window.key_down(self, e)


win = TWindow(width = 1000, height = 500, title = "Btns", 
    resizable = 0, zoomable = 0)



def start_recording():
    #print DWF version
  print("DWF Version: " + dwf.FDwfGetVersion())

  #constants
  HZ_ACQ = 20e3 
  N_SAMPLES = 100000

  #open device
  print("Opening first device")
  dwf_ao = dwf.DwfAnalogOut()

  print("Preparing to read sample...")

  print("Generating sine wave...")
  dwf_ao.nodeEnableSet(0, dwf_ao.NODE.CARRIER, True)
  dwf_ao.nodeFunctionSet(0, dwf_ao.NODE.CARRIER, dwf_ao.FUNC.SINE)
  dwf_ao.nodeFrequencySet(0, dwf_ao.NODE.CARRIER, 1.0)
  dwf_ao.nodeAmplitudeSet(0, dwf_ao.NODE.CARRIER, 2.0)
  dwf_ao.configure(0, True)

  #set up acquisition
  dwf_ai = dwf.DwfAnalogIn(dwf_ao)
  dwf_ai.channelEnableSet(0, True)
  dwf_ai.channelRangeSet(0, 5.0)
  dwf_ai.acquisitionModeSet(dwf_ai.ACQMODE.RECORD)
  dwf_ai.frequencySet(HZ_ACQ)
  dwf_ai.recordLengthSet(5)

  #wait at least 2 seconds for the offset to stabilize
  time.sleep(2)

  #begin acquisition
  dwf_ai.configure(False, True)
  print("   waiting to finish")

  rgdSamples = []
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
      rgdSamples.extend(dwf_ai.statusData(0, cAvailable))
      cSamples += cAvailable

  print("Recording finished")
  if fLost:
      print("Samples were lost! Reduce frequency")
  if cCorrupted:
      print("Samples could be corrupted! Reduce frequency")

  with open("record.csv", "w") as f:
      for v in rgdSamples:
          f.write("%s\n" % v)
    
  plt.plot(rgdSamples)
  plt.savefig('test.png', bbox_inches='tight')
  scaled = np.int16(rgdSamples/np.max(np.abs(rgdSamples)) * 32767)
  write('test.wav', 20000, scaled)
  """plt.show()"""
  update_pic()

def update_pic():
  here = sys.path[0]
  image_path = os.path.join(here, "test.png")
  image = Image(file = image_path)
  view = ImageTestView(size = win.size)
  view.add(btn1)
  view.add(btn5)
  win.add(image)
  view.become_target()
  win.show()

class ImageTestView(View):

    def draw(self, c, r):
        here = sys.path[0]
        image_path = os.path.join(here, "test.png")
        image = Image(file = image_path)
        c.backcolor = yellow
        c.erase_rect(r)
        main_image_pos = (30, btn1.bottom+30)
        src_rect = (0,0,571,416)
        #say("Image bounds =", src_rect)
        dst_rect = offset_rect(src_rect, main_image_pos)
        #say("Drawing", src_rect, "in", dst_rect)
        image.draw(c, src_rect, dst_rect)

def stop_recording():
  print("nothign usefull")

def play_recording():
  CHUNK = 1024
  here = sys.path[0]
  sound_path = os.path.join(here, "test.wav")
  wf = wave.open(here, 'rb')

  p = pyaudio.PyAudio()

  stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                  channels=wf.getnchannels(),
                  rate=wf.getframerate(),
                  output=True)

  data = wf.readframes(CHUNK)

  while data != '':
      stream.write(data)
      data = wf.readframes(CHUNK)

  stream.stop_stream()
  stream.close()

  p.terminate()

btn1 = Button(position = (30, 30), 
    title = "Start", action = start_recording, style = 'default')

btn4 = Button(position = (30, 30), 
    title = "Stop", action = stop_recording, style = 'default')
btn5 = Button(position = (230, 30), 
    title = "Play", action = play_recording, style = 'default')
    
"""btn2 = Button(x = 30, y = btn1.bottom + 30, width = 200, 
    title = "Goodbye", just = 'centre',
    action = say_goodbye,
    enabled = 0)
btn2.font = Font("Times", 1.2 * system_font.size, [])"""

btn3 = Button(x = 30, y = btn1.bottom + 30, width = 200,
    font = Font("Times", 1.2 * system_font.size, ['italic']),
    action = stop_recording, title = "Wrong", style = 'cancel')
btn3.color = red
btn3.just = 'right'
btn3.title = "Gidday Mate"




    
win.add(btn1)
"""win.add(btn2)"""
"""win.add(btn3)"""
win.add(btn5)
win.show()

instructions = """
There should be 3 buttons arranged vertically:
1. Title "Hello", natural width, style 'default'
2. Title "Goodbye" in a serif font, width 200, initially disabled
3. Title "Gidday Mate" in red italic, width 200, style 'cancel', right aligned
Pressing button 1 should print "Hello, world!" and enable button 2.
Pressing button 2 should print "Goodbye, world!" and disable button 2.
Pressing button 3 should simulate pressing button 1.
"""

say(instructions)
say("Testing readback of button 3 properties:")
say("title =", btn3.title)
say("font =", btn3.font)
say("color =", btn3.color)
say("just =", btn3.just)
say("End of readback test")
say()

application().run()
