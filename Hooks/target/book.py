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
import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import asc
from Core.config import Config
from Core.db import session
from Core.maps import Updates, Planet, User, Target, Attack, AttackData
from Core.loadable import loadable

@loadable.module("half")
class book(loadable):
    """Book a target for attack. You should always book your targets, so someone doesn't inadvertedly piggy your attack."""
    usage = " x:y:z (eta|landing tick) <later>"
    paramre = re.compile(loadable.planet_coordre.pattern+r"\s(\d+)(?:\s(yes|later))?(?:\s(yes|later))?")
    
    @loadable.require_user
    def execute(self, message, user, params):
        planet = Planet.load(*params.group(1,2,3))
        if planet is None:
            message.alert("No planet with coords %s:%s:%s" % params.group(1,2,3))
            return
        
        tick = Updates.current_tick()
        when = int(params.group(4))
        if when < 32:
            eta = when
            when += tick
        elif when <= tick:
            message.alert("Can not book targets in the past. You wanted tick %s, but current tick is %s." % (when, tick,))
            return
        else:
            eta = when - tick
        if when > 32767:
            when = 32767        
        
        if planet.intel and planet.alliance and planet.alliance.name == Config.get("Alliance","name"):
            message.reply("%s:%s:%s is %s in %s. Quick, launch before they notice the highlight." % (planet.x,planet.y,planet.z, planet.intel.nick or 'someone', Config.get("Alliance","name"),))
            return
                
        T = session.query(Attack)
        T = T.join(AttackData)
        T = T.filter(AttackData.planet_id == planet.id)
        T = T.filter(Attack.start_time < datetime.datetime.now())
        T = T.filter(Attack.book_time > datetime.datetime.now())
        tresult = T.all()
        if len(tresult) >= 1:
	    message.reply("Target %s:%s:%s is part of an upcoming attack" % (planet.x,planet.y,planet.z,))
	    return

        Q = session.query(User.name, Target.tick)
        Q = Q.join(Target.user)
        Q = Q.filter(Target.planet == planet)
        Q = Q.filter(Target.tick >= when)
        Q = Q.order_by(asc(Target.tick))
        result = Q.all()
        
        if len(result) >= 1:
            booker, land = result[0]
            if land == when:
	        if str(params.group(5)) == "later" or str(params.group(6)) == "later":
		    later = when+1
                    Q2 = session.query(User.name, Target.tick)
                    Q2 = Q2.join(Target.user)
                    Q2 = Q2.filter(Target.planet == planet)
                    Q2 = Q2.filter(Target.tick >= later)
                    Q2 = Q2.order_by(asc(Target.tick))
                    result2 = Q2.all()
		    if len(result2) >= 1:
                       laterbooker, laterland = result2[0]
                       if laterland == later:
                           message.reply("YOU CANNOT HIT %s:%s:%s. NOT EVEN SLOPPY SECOND'S. THIS TARGET IS MORE TAKEN THAN YOUR MUM, AMIRITE?" % (planet.x,planet.y,planet.z,))
                           return
                    try:
                        planet.bookings.append(Target(user=user, tick=later))
                        session.commit()
                        message.reply("YOU HAVE BEEN BEATEN TO THIS TARGET. YOU ARE NOW GETTING SLOPPY SECOND'S ON %s:%s:%s TAKING PLACE ON TICK %s" % (planet.x,planet.y,planet.z, later,))
                        return
                    except IntegrityError:
                        session.rollback()
                        raise Exception("Integrity error? Unable to booking for pid %s and tick %s"%(planet.id, later,))
                        return
		else:
                    message.reply("Target %s:%s:%s is already booked for landing tick %s by user %s" % (planet.x,planet.y,planet.z, land, booker,))
                    return
            if params.group(5) is None or (str(params.group(5)) == "later" and params.group(6) is None):
                reply="There are already bookings for that target after landing pt %s (eta %s). To see status on this target, do !status %s:%s:%s." % (when,eta, planet.x,planet.y,planet.z,)
                reply+=" To force booking at your desired eta/landing tick, use !book %s:%s:%s %s yes (Bookers: " %(planet.x,planet.y,planet.z, when,)
                prev=[]
                for booker, land in result:
                    prev.append("(%s user:%s)" % (land, booker,))
                reply += ", ".join(prev) + ")"
                message.reply(reply)
                return
        
        try:
            planet.bookings.append(Target(user=user, tick=when))
            session.commit()
            message.reply("Booked landing on %s:%s:%s tick %s for user %s" % (planet.x,planet.y,planet.z, when, user.name,))
            return
        except IntegrityError:
            session.rollback()
            raise Exception("Integrity error? Unable to booking for pid %s and tick %s"%(planet.id, when,))
            return
