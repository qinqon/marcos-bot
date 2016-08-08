import time

from threading import Thread

class PeriodicTimer:
   def __init__(self, interval):
      self.interval = interval
      self.stop = False   
      self.thread = None
   def repeat_execution(self):
      while not self.stop:
         self.action()
         time.sleep(self.interval)
   
   def start(self, action):
      if self.stop: 
         self.stop = False
         self.action = action
         self.thread = Thread(target=lambda: self.repeat_execution())
         self.thread.daemon = True
         self.thread.start()

   def cancel(self):
      self.stop = True
      if self.thread != None:
         self.thread.join()
