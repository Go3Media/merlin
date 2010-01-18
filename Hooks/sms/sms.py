# This file is part of Merlin.
# Merlin is the Copyright (C)2008-2009 of Robin K. Hansen, Elliot Rosemarine, Andreas Jacobsen.

# Individual portions may be copyright by individual contributors, and
# are included in this collective work with permission of the copyright
# owners.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
 
import re
import csv
import sys
from urllib import urlencode
from urllib2 import urlopen
from gvoice import *
import getpass
import os
from Core.config import Config
from Core.db import session
from Core.maps import User, SMS
from Core.loadable import loadable

@loadable.module("member")
class sms(loadable):
    """Sends an SMS to the specified user. Your username will be appended to the end of each sms. The user must have their phone correctly added and you must have access to their number."""
    usage = " <nick> <message>"
    paramre = re.compile(r"\s+(\S+)\s+(.+)")
    
    @loadable.require_user
    def execute(self, message, user, params):
        
        rec = params.group(1)
        public_text = params.group(2) + ' - %s' % (user.name,)
        text = public_text.encode('latin-1') + '/%s' %(user.phone,)
        receiver=User.load(name=rec,exact=False)
        if not receiver:
            message.reply("Who exactly is %s?" % (rec,))
            return

        if not receiver.pubphone and user not in receiver.phonefriends:
            message.reply("%s's phone number is private or they have not chosen to share their number with you. Supersecret message not sent." % (receiver.name,))
            return

        phone = self.prepare_phone_number(receiver.phone)
        if not phone or len(phone) <= 6:
            message.reply("%s has no phone number or their phone number is too short to be valid (under 6 digits). Super secret message not sent." % (receiver.name,))
            return

        if len(text) >= 160:
            message.reply("Max length for a text is 160 characters. Your text was %i characters long. Super secret message not sent." % (len(text),))
            return
        if not receiver.googlevoice:
            get = urlencode({"user": Config.get("clickatell", "user"),
                        "password": Config.get("clickatell", "pass"),
                        "api_id": Config.get("clickatell", "api"),
                        "to": phone,
                        "text": text,
            })
	
            status, msg = urlopen("https://api.clickatell.com/http/sendmsg", get).read().split(":")
	
            if status in ("OK","ID",):
	        message.reply("Successfully processed To: %s Message: %s" % (receiver.name,text))
	        self.log_message(user,receiver,phone, public_text)
            elif status in ("ERR",):
	        message.reply("Error sending message: %s" % (msg.strip(),))
            else:
	        message.reply("That wasn't supposed to happen. I don't really know what wrong. Maybe your mother dropped you.")
            return

	email = Config.get("googlevoice", "email")
        password = Config.get("googlevoice", "pass")
        gvoice = GoogleVoiceLogin(email, password)
        if not gvoice.logged_in:
            message.reply("Could not log in with provided credentials")
            return
        else:
            text_sender = TextSender(gvoice.opener, gvoice.key)
            text_sender.text = text
            number = phone
            text_sender.send_text(phone)
            if text_sender.response:
                message.reply("Sending message to {0} at {1}".format(receiver.name, phone),)
            else:
                message.reply("Failed!!")
    
    def prepare_phone_number(self,text):
        if not text:
            return text
        s = "".join([c for c in text if c.isdigit()])
        return s.lstrip("00")

    def log_message(self,sender,receiver,phone,text):
        session.add(SMS(sender=sender,receiver=receiver,phone=phone,sms_text=text))
        session.commit()
