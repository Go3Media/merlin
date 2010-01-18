import re
from sqlalchemy.sql import desc
from Core.config import Config
from Core.db import session
from Core.maps import Updates, User, Ship, UserFleet
from Core.loadable import loadable

@loadable.module("member")
class anti(loadable):
    """"""
    usage = " <class>"
    paramre = re.compile(r"\s+(\S+)")
    ship_classes = ['fi','co','fr','de','cr','bs']
    def execute(self, message, user, params):        
        requestedclass = params.group(1).lower()
        if requestedclass not in self.ship_classes:
             message.alert("Can't find class %s" % (name,))
             return
