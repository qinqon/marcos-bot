import audioop
import pyaudio

class CryDetector:

   def get_mic_device(self, mic_name):
      selected_device = 2
      info = self.paudio.get_host_api_info_by_index(0)
      numdevices = info.get('deviceCount')
      #for each audio device, determine if is an input or an output and add it to the appropriate list and dictionary
      for i in range (0,numdevices):
         if self.paudio.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
            device_name = self.paudio.get_device_info_by_host_api_device_index(0,i).get('name')
            if device_name.find(mic_name) > -1: 
               selected_device = i
            break

      device_info = self.paudio.get_device_info_by_index(selected_device)
      return selected_device
#

   def get_level(self, data):
      rms = audioop.rms(data, 2)  #width=2 for format=paInt16
      return rms

   def __init__(self, threshold):
         self.threshold = threshold
         self.callbacks = []
         self.paudio = pyaudio.PyAudio()
         mic_device = self.get_mic_device("USB")
         self.chunk = 1024

         self.stream = self.paudio.open(format=pyaudio.paInt16,
               input_device_index=mic_device,
               channels=1,
               rate=48000,
               input=True,
               output=False,
               frames_per_buffer=self.chunk)
   
   def start(self):
      print("Starting cry detector")
      while True:
         try:
            data = self.stream.read(self.chunk)
            level = self.get_level(data)
            if level > self.threshold:
               for callback in self.callbacks:
                  callback()
         except IOError:
            True

   def register(self, callback):
      self.callbacks.append(callback)     
   
   def clean(self):
      self.callbacks = []
