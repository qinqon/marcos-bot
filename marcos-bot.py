#!/usr/bin/env python3 
import os
import io
import argparse
import telepot
import time
import cry_detector
import periodic_timer
import pygame
import pygame.camera

from threading import Thread
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import per_from_id, create_open

pygame.camera.init()

class Marcos(telepot.helper.UserHandler, telepot.helper.AnswererMixin):
   def __init__(self, seed_tuple, timeout):
      super(Marcos, self).__init__(seed_tuple, timeout)
      self.alarm_text_list  = [u'\U0001F616' + " Bu", u'\U0001F622' + " Buaaa!", u'\U0001F62D' + " Buaaaaaa!!!"]
      self.alarm_text_index = 0
      self.cam = pygame.camera.Camera("/dev/video0",(640,480))
      self.started = False      

   def send_a_picture(self):
      img = self.cam.get_image()
      if img:
         img_url = "/tmp/" + str(self.user_id) + "_marcos.jpg"
         pygame.image.save(img, img_url)
         self.sender.sendPhoto(open(img_url, 'rb'))
   
   def stop_cry_detector(self):
      periodic_timer.cancel()
      cry_detector.clean()
   
   
   def setup_cry_detector(self):
      cry_detector.register(lambda: periodic_timer.start(lambda: self.send_alarm()))
   
   def send_start_slogan(self):
      slogan_text = 'Listening to the baby ' + u'\U0001F634'
      self.sender.sendMessage(slogan_text)
   
   def send_alarm(self):
      alarm_text = self.alarm_text_list[self.alarm_text_index]
      self.sender.sendMessage(alarm_text)
      self.alarm_text_index = (self.alarm_text_index + 1) % len(self.alarm_text_list)
      if self.alarm_text_index == len(self.alarm_text_list) - 1:
         self.send_a_picture()

   def start(self):  
      if not self.started: 
         self.send_start_slogan()
         self.stop_cry_detector()
         self.setup_cry_detector() 
         self.cam.start()  
         self.started = True
     
   def stop(self):
      if self.started:
         self.stop_cry_detector()
         self.cam.stop()  
         self.started = False     
   
   def on_chat_message(self, msg):
    global state_machine
    global args
    content_type, chat_type, chat_id = telepot.glance(msg) 
    user_id=msg['from']['id']
    permitted_user_ids=args.user_id.split(',')
    if not str(user_id) in permitted_user_ids:
        self.sender.sendMessage("Go away stalker " + str(user_id) + "!!!")
        return
    if (content_type == 'text'):
      text    = msg['text']
      if text == '/start':
         self.start()
      elif text == '/stop':
         self.stop()
         self.sender.sendMessage("Bye !!!")         
      elif text == '/reset':
         self.stop()
         self.start()         

parser = argparse.ArgumentParser(description='Instagram bot for Marcos operations.')
parser.add_argument("token", help="Telegram bot token string as generated by BotFather")
parser.add_argument("user_id", help="Telegram user ID to restrict the bot")
parser.parse_args()
args = parser.parse_args()


# Getting the token from command-line is better than embedding it in code,
# because tokens are supposed to be kept secret.

cry_detector = cry_detector.CryDetector(threshold=5000)
periodic_timer = periodic_timer.PeriodicTimer(interval=1)

cry_detector_thread = Thread(target = lambda: cry_detector.start())
cry_detector_thread.daemon = True
cry_detector_thread.start()

bot = telepot.DelegatorBot(args.token, [
    (per_from_id(), create_open(Marcos, timeout=360)),
])

bot.message_loop(run_forever="Listening...")
cry_detector_thread.join()
