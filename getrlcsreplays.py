import requests
import json
import datetime
import dateutil.parser
import time

REGIONS = ("EU","NA","OCE","SAM","MENA","APAC","SSA")

# Your Ballchasing API key
AUTH = "w8L30IZjDg2dadG47cRVKx5wNEffZkgoroIkEFNO"

def calcSeriesScore(s):
    '''
    Calculates the score for a series

    :param s: Entry in "series" dictionary
    :return: Array of length 2 containing scores
    in format [blueteamscore,orangeteamscore]
    '''
    scores=[0,0]
    for gid in s["games"]:
        if gid=="G0":
            continue
        g=s["games"][gid]
        if g["bluescore"]>g["orangescore"]:
            scores[0]+=1
        else:
            scores[1]+=1
    return scores

def formatOT(t):
    '''
    Formats a string with overtime information

    :param t: Overtime length in seconds
    :return: Formatted string with overtime information
    '''
    if t==0:
        return ""
    ret=f" +{datetime.datetime.fromtimestamp(t).strftime('%#M:%S')}"
    return ret

def updateJSON():
    '''
    Writes all stored series info to 'series.json'

    :return: 0
    '''

    f = open('series.json','w')
    f.write(json.dumps(series))
    f.close()

    return 0

def printToTimeline(entry):
    '''
    Writes a string to 'timeline.txt'

    :param entry: String to be written
    :return: 0
    '''

    f = open('timeline.txt','a')
    f.write('\n'+entry)
    f.close()

    return 0

def formatMatchRLCS(s):
    '''
    Formats a string for RLCS replay upload tracking printouts

    :param s: Entry in "series" dictionary

    :return: Formatted string
    '''

    seriesscores=calcSeriesScore(s)

    ret = f"""{gametime.strftime("%H:%M").ljust(8)}\
{gametitle[0].ljust(8)}{gametitle[1].ljust(4)}\
{gametitle[-2].ljust(4)}{blueteam} {seriesscores[0]}-{seriesscores[1]} {orangeteam}"""

    if gametitle[1]!="G0":
        ret += f""" ({gamebluescore}-{gameorangescore}{formatOT(gameot)})"""

    return ret

def formatMatchCarballTV(s):
    '''
    Formats a string for CarballTV timeline printouts

    :param s: Entry in "series" dictionary

    :return: Formatted string
    '''

    seriesscores=calcSeriesScore(s)

    ret = f"""{gametime.strftime("%H:%M").ljust(8)}{gametitle[0].ljust(8)}\
{blueteam} {seriesscores[0]}-{seriesscores[1]} {orangeteam}"""

    if gametitle[-2]!="G0":
        ret += f""" ({gamebluescore}-{gameorangescore}{formatOT(gameot)})"""

    return ret

series={}

while True:

    now = datetime.datetime.now(datetime.timezone.utc)

    # To test on historical data, adjust THIS timedelta
    then = now # - datetime.timedelta(minutes=1)

    # That is to say, not this one!
    then2 = then - datetime.timedelta(minutes=1)

    url = "https://ballchasing.com/api/replays"

    headers = {"Authorization" : AUTH}

    params = {"uploader" : "76561199225615730",
              "playlist" : "private",
              "created-after": then2.isoformat(),
              "created-before": then.isoformat()}

    # Uncomment the below when debugging
    # print(f"{then2.strftime('%H:%M')} Making request...")

    response=requests.get(url,params=params,headers=headers)

    if response.status_code==200:

        data=json.loads(response.content)
        
        for g in range(len(data["list"])-1,-1,-1):
            game = data["list"][g]

            gametitle = game["replay_title"].split(' ')
            try:
                gameno = int(gametitle[-2][-1])
            except Exception:
                continue
            if len(gametitle)<2:
                continue
            # If this replay is not RLCS formatted discount it
            if not (gametitle[0] in REGIONS):
                continue
            
            gametime = dateutil.parser.isoparse(game["created"])

            try:
                blueteam = game["blue"]["name"]
                orangeteam = game["orange"]["name"]
            except KeyError:
                continue

            try:
                gamebluescore=game["blue"]["goals"]
            except KeyError:
                gamebluescore=0
            try:
                gameorangescore=game["orange"]["goals"]
            except KeyError:
                gameorangescore=0

            if game["overtime"]:
                try:
                    gameot=game['overtime_seconds']
                except KeyError:
                    gameot=0
            else:
                gameot=0

            # If this matchup has never taken place before
            # Create a new entry
            try:
                thisseries=series[blueteam,orangeteam]
                if len(thisseries["games"])+1<gameno:
                    continue
            except KeyError:
                series[blueteam,orangeteam]={"blue" : blueteam,
                                             "orange" : orangeteam,
                                             "time" : gametime,
                                             "games" : {}}

                thisseries=series[blueteam,orangeteam]

                if gametitle[-2] == "G0":
                    print(formatMatchRLCS(thisseries))
                    printToTimeline(formatMatchCarballTV(thisseries))

            # If this game does not have a duplicate ID we can skip verification
            try:
                oldgame=thisseries["games"][gametitle[-2]]

                # If more the 2 hours have passed since the last time this game was played
                # Or more than 20 minutes have passed since the last test lobby
                # Reset this matchup as a new series is expected to be starting soon or is ongoing
                if (thisseries["time"] + datetime.timedelta(hours=2) < gametime) or \
                    (gametitle[-2] == "G0" and \
                    (thisseries["time"] + datetime.timedelta(minutes=20) < gametime)):
                    series[blueteam,orangeteam]={"blue" : blueteam,
                                                "orange" : orangeteam,
                                                "time" : gametime,
                                                "games" : {}}

                    if gametitle[-2] == "G0":
                        print(formatMatchRLCS(thisseries))
                        printToTimeline(formatMatchCarballTV(thisseries))
                        continue

                # If the game ID, scores and OT status are the same,
                # it's basically the same game for our purposes
                elif oldgame["bluescore"]==gamebluescore and \
                    oldgame["orangescore"]==gameorangescore:
                    if not (game["overtime"] or oldgame["ot"]):
                        continue
                    elif gameot == oldgame["ot"]:
                        continue

            except KeyError:
                pass
            
            # Create a new game entry, or update the existing one
            series[blueteam,orangeteam]["games"][gametitle[-2]]={
                "bluescore" : gamebluescore,
                "orangescore" : gameorangescore,
                "ot" : gameot}

            # All handling for test lobbies should be done
            if gametitle[-2] == "G0":
                continue

            thisseries=series[blueteam,orangeteam]

            print(formatMatchRLCS(thisseries))
            printToTimeline(formatMatchCarballTV(thisseries))

    else:
        print(response.status_code)
    updateJSON()
    time.sleep(15)
    
