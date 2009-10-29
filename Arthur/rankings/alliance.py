from datetime import datetime
from django.http import HttpResponseRedirect
from sqlalchemy.sql import asc, desc
from Core.paconf import PA
from Core.db import session
from Core.maps import Updates, Alliance, Planet, PlanetHistory, Alliance, Intel
from Arthur.auth import render

def alliance(request, name, page="1", sort="score", race="all"):
    page = int(page)
    offset = (page - 1)*50
    order =  {"score" : (asc(Planet.score_rank),),
              "value" : (asc(Planet.value_rank),),
              "size"  : (asc(Planet.size_rank),),
              "xp"    : (asc(Planet.xp_rank),),
              "race"  : (asc(Planet.race), asc(Planet.size_rank),),
              }
    if sort not in order.keys():
        sort = "score"
    order = order.get(sort)
    
    now = datetime.now()
    d1 = datetime(now.year, now.month, now.day, now.hour)
    d2 = datetime(now.year, now.month, now.day)
    hours = (d1-d2).seconds/60/60
    tick = Updates.current_tick() - hours
    
    alliance = Alliance.load(name)
    if alliance is None:
        return HttpResponseRedirect("/alliances/")
    
    Q = session.query(Planet, PlanetHistory, Intel.nick, Alliance.name)
    Q = Q.join(Planet.intel)
    Q = Q.join(Intel.alliance)
    Q = Q.outerjoin(Planet.history_loader)
    Q = Q.filter(PlanetHistory.tick == tick)
    Q = Q.filter(Intel.alliance == alliance)
    
    if race.lower() in PA.options("races"):
        Q = Q.filter(Planet.race.ilike(race))
    else:
        race = "all"
    
    count = Q.count()
    pages = count/50 + int(count%50 > 0)
    pages = range(1, 1+pages)
    
    for o in order:
        Q = Q.order_by(o)
    Q = Q.limit(50).offset(offset)
    return render("planets.tpl", request, planets=Q.all(), title=alliance.name, alliance=alliance, intel=True, offset=offset, pages=pages, page=page, sort=sort, race=race)
