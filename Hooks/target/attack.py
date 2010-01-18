import re
import datetime
from print_r import print_r
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import asc
from Core.config import Config
from Core.db import session
from Core.maps import Planet, User, Attack, AttackData
from Core.loadable import loadable

@loadable.module("member")
class attack(loadable):
#    """Book a target for attack. You should always book your targets, so someone doesn't inadvertedly piggy your attack."""
#    usage = " start_time booking_time coords <waves>"
#    paramre = re.compile(r"\s+(\d+)\s+(\d+)\s+(?:"+loadable.planet_coordre.pattern+"){1,}(?:\s+(\d+))?")
#    @loadable.require_user
#    def execute(self, message, user, params):
#        #for m in loadable.planet_coordre.finditer(message.get_msg().split(None, 3)[3]):