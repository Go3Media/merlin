## Googlevoice API made by Scott Hillman 
## http://everydayscripting.blogspot.com

import csv
import sys
import re
import urllib
import urllib2

class GoogleVoiceLogin:
  def __init__(self, email, password):
      # Set up our opener
      self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
      urllib2.install_opener(self.opener)
    
      # Define URLs
      self.loing_page_url = 'https://www.google.com/accounts/ServiceLogin'
      self.authenticate_url = 'https://www.google.com/accounts/ServiceLoginAuth'
      self.gv_home_page_url = 'https://www.google.com/voice/#inbox'
    
      # Load sign in page
      login_page_contents = self.opener.open(self.loing_page_url).read()

      # Find GALX value
      galx_match_obj = re.search(r'name="GALX"\s*value="([^"]+)"', login_page_contents, re.IGNORECASE)
    
      galx_value = galx_match_obj.group(1) if galx_match_obj.group(1) is not None else ''
    
      # Set up login credentials
      login_params = urllib.urlencode( {
          'Email' : email,
          'Passwd' : password,
          'continue' : 'https://www.google.com/voice/account/signin',
          'GALX': galx_value
      })

      # Login
      self.opener.open(self.authenticate_url, login_params)

      # Open GV home page
      gv_home_page_contents = self.opener.open(self.gv_home_page_url).read()

      # Fine _rnr_se value
      key = re.search('name="_rnr_se".*?value="(.*?)"', gv_home_page_contents)
    
      if not key:
          self.logged_in = False
      else:
          self.logged_in = True
          self.key = key.group(1)
    
            
class TextSender():
  def __init__(self, opener, key):
      self.opener = opener
      self.key = key
      self.sms_url = 'https://www.google.com/voice/sms/send/'
      self.text = ''
    
  def send_text(self, phone_number):
      sms_params = urllib.urlencode({
          '_rnr_se': self.key,
          'phoneNumber': phone_number,
          'text': self.text
      })
      # Send the text, display status message  
      self.response  = self.opener.open(self.sms_url, sms_params).read()