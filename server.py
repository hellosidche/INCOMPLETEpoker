import socket
import threading
import time
import random


HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

#Common variables
acceptingconnections = True
players = 0
readyplayers = 0
playerdict = {} #playerdict format {conn: [playernumber, [card1, card2]]}
table = []
turns = []
bets = []
cards = []
smallblind = 0
bigblind = 0
whosturn = 0
pot = 0
betting = True
firstturn = False
roundover = False
howmanyturns = 0

#Common events
minplayersreached = threading.Event()
allplayersready = threading.Event()
gamestarting = threading.Event()
allclear = threading.Event()
startnewround = threading.Event()



def handtablesorter(handtable):
    sortedhandtable = []
    counter = -1
    for card in handtable:
        counter = counter + 1
        if len(sortedhandtable) == 0:
            sortedhandtable.append(card)
        elif card[0] > sortedhandtable[-1][0]:
            sortedhandtable.append(card)
        elif card[0] == sortedhandtable[-1][0]:
            indexinsert = counter
            inserted = 0
            while indexinsert > 0 and card[0] == sortedhandtable[(indexinsert - 1)][0] and inserted == 0:
                if card[1] > sortedhandtable[(indexinsert - 1)][1]:
                    sortedhandtable.insert(indexinsert, card)
                    inserted = 1
                else:
                    indexinsert = indexinsert - 1
            if inserted == 0:
                sortedhandtable.insert(indexinsert, card)
        else:
            indexinsert = counter
            while indexinsert > 0 and card[0] < sortedhandtable[(indexinsert - 1)][0]:
                indexinsert = indexinsert - 1
            if card[0] > sortedhandtable[(indexinsert - 1)][0]:
                sortedhandtable.insert(indexinsert, card)
            else:
                inserted = 0
                while card[0] == sortedhandtable[(indexinsert - 1)][0] and inserted == 0:
                    if card[1] >= sortedhandtable[(indexinsert - 1)][1]:
                        sortedhandtable.insert(indexinsert, card)
                        inserted = 1
                    else:
                        indexinsert = indexinsert - 1
                if inserted == 0:
                    sortedhandtable.insert(indexinsert, card)
    return sortedhandtable

def findflush(sortedhandtable):
    flush = []
    suits = [0, 0, 0, 0]
    for card in sortedhandtable:
        suits[card[1] - 1] = suits[card[1] - 1] + 1
    suitcounter = 0
    for suit in suits:
        suitcounter = suitcounter + 1
        if suit > 4:
            for card in sortedhandtable:
                if card[1] == suitcounter:
                    flush.append(card)
            return(flush)
    return(-1)

def noduplicateshandtable(sortedhandtable):
    noduplicateshandtable = []
    incrementer = -1
    best = sortedhandtable[incrementer]
    noduplicateshandtable.append(best)
    while incrementer > -7:
        incrementer = incrementer - 1
        if sortedhandtable[incrementer][0] != best[0]:
            best = sortedhandtable[incrementer]
            noduplicateshandtable.append(best)
    noduplicateshandtable.reverse()
    return(noduplicateshandtable)

def findstraights(sortedforstraights):
    if len(sortedforstraights) > 4:
        if sortedforstraights[0][0] == 2 and sortedforstraights[-1][0] == 14:
            counter = -1
            highhalf = [sortedforstraights[counter]]
            highhalfcomplete = 0
            while len(highhalf) < 5 and highhalfcomplete == 0:
                if sortedforstraights[counter][0] - 1 == sortedforstraights[counter - 1][0]:
                    highhalf.append(sortedforstraights[counter - 1])
                    counter = counter - 1
                else:
                    highhalfcomplete = 1
            highhalf.reverse()
            if len(highhalf) == 5:
                return(highhalf)
            counter = 0
            lowhalf = [sortedforstraights[counter]]
            lowhalfcomplete = 0
            while len(lowhalf) < 5 - len(highhalf) and lowhalfcomplete == 0:
                if sortedforstraights[counter][0] + 1 == sortedforstraights[counter + 1][0]:
                    lowhalf.append(sortedforstraights[counter + 1])
                    counter = counter + 1
                else:
                    lowhalfcomplete = 1
            if len(lowhalf) + len(highhalf) > 4:
                straight = lowhalf + highhalf
                return(straight)
        counter = -1
        straight = [sortedforstraights[counter]]
        while len(straight) < 5 and (-1 * counter) < len(sortedforstraights):
            if sortedforstraights[counter][0] - 1 == sortedforstraights[counter - 1][0]:
                straight.append(sortedforstraights[counter - 1])
                counter = counter - 1
            else:
                straight = [sortedforstraights[counter - 1]]
                counter = counter - 1
        if len(straight) == 5:
            straight.reverse()
            return(straight)
        else:
            return(-1)
    else:
        return(-1)

def sortedmatches(sortedhandtable):
    matches = []
    match = []
    for card in sortedhandtable:
        if len(match) == 0:
            match.append(card)
        elif card[0] == match[-1][0]:
            match.append(card)
        else:
            matches.append(match)
            match = [card]
    matches.append(match)
    return(matches)

def setfinder(handtable):
    sortedhandtable = handtablesorter(handtable)
    flush = findflush(sortedhandtable)
    if flush != -1:
        straightflush = findstraights(flush)
        if straightflush != -1:
            straightflush.insert(0, "Straight Flush")
            return(straightflush)
    matches = sortedmatches(sortedhandtable)
    singles = []
    doubles = []
    triples = []
    quadruples = []
    for match in matches:
        if len(match) == 1:
            singles.append(match)
        elif len(match) == 2:
            doubles.append(match)
        elif len(match) == 3:
            triples.append(match)
        else:
            quadruples.append(match)
    if len(triples) > 1:
        tripletodouble = triples[-2]
        tripletodouble.remove(tripletodouble[0])
        doubles.append(tripletodouble)
        triples.remove(tripletodouble)

    if len(quadruples) != 0:
        set = [quadruples[-1]]
        set.insert(0, "Quadruple")
        return(set)
    if len(triples) != 0 and len(doubles) != 0:
        set = doubles[-1] + triples[-1]
        set.insert(0, "Full House")
        return(set)
    if flush != -1:
        flush.insert(0, "Flush")
        return(flush)
    sortedforstraights = noduplicateshandtable(sortedhandtable)
    straight = findstraights(sortedforstraights)
    if straight != -1:
        straight.insert(0, "Straight")
        return(straight)
    if len(triples) != 0:
        set = triples[-1]
        set.insert(0, "Triple")
        return(set)
    if len(doubles) > 1:
        set = doubles[-2] + doubles[-1]
        set.insert(0, "Double Double")
        return(set)
    if len(doubles) != 0:
        set = doubles[-1]
        set.insert(0, "Double")
        return(set)
    set = sortedhandtable
    set.insert(0, "High Card")
    return(set)

def settypetoint(set):
    settype = set[0]
    if settype == "High Card":
        return(0)
    elif settype == "Double":
        return(1)
    elif settype == "Double Double":
        return(2)
    elif settype == "Triple":
        return(3)
    elif settype == "Straight":
        return(4)
    elif settype == "Flush":
        return(5)
    elif settype == "Full House":
        return(6)
    elif settype == "Quadruple":
        return(7)
    else:
        return(8)

def setcomparer(playerone, playertwo):
    playeronetype = settypetoint(playerone)
    playertwotype = settypetoint(playertwo)
    if playeronetype > playertwotype:
        return("P1 wins")
    elif playeronetype < playertwotype:
        return("P2 wins")
    else:
        if playeronetype in [1, 3, 7]:
            playeronenumber = playerone[1][0]
            playertwonumber = playertwo[1][0]
            if playeronenumber > playertwonumber:
                return("P1 wins")
            elif playeronenumber < playertwonumber:
                return("P2 wins")
            else:
                return("Tie")
        elif playeronetype in [0, 4, 5, 8]:
            counter = -1
            playeronenumber = playerone[counter][0]
            playertwonumber = playertwo[counter][0]
            while playeronenumber == playertwonumber and (-1 * counter) < len(playerone) - 1:
                counter = counter - 1
                playeronenumber = playerone[counter][0]
                playertwonumber = playertwo[counter][0]
            if playeronenumber > playertwonumber:
                return("P1 wins")
            elif playeronenumber < playertwonumber:
                return("P2 wins")
            else:
                return("Tie")
        else:
            if playerone[3][0] > playertwo[3][0]:
                return("P1 wins")
            elif playerone[4][0] < playertwo[4][0]:
                return("P2 wins")
            else:
                if playerone[1][0] > playertwo[1][0]:
                    return("P1 wins")
                elif playerone[1][0] < playertwo[1][0]:
                    return("P2 wins")
                else:
                    return("Tie")

def p1p2tablesplitter(p1p2table):
    playerone = p1p2table[0:2] + p1p2table[4:10]
    playertwo = p1p2table[2:4] + p1p2table[4:10]
    return([playerone, playertwo])


def gameinitializer():
    global smallblind
    global bigblind
    global whosturn
    global players
    global playerdict
    global table
    global turns
    global bets
    global cards

    deck = []
    for number in range(2, 15):
        for suit in range(1, 5):
            deck.append([number, suit])

    neededcards = (players * 2) + 5
    for i in range(0, neededcards):
        card = deck[random.randint(0, len(deck) - 1)]
        cards.append(card)
        deck.remove(card)

    n = 0
    turns = []
    for conn in playerdict:
        playerdict[conn].append([(cards[n]), cards[n+1]])
        turns.append(threading.Event())
        n = n + 2

    table = cards[-5:]

    for player in range(0, players):
        bets.append(0)

    smallblind = 1
    bigblind = 2
    if bigblind == players:
        whosturn = 1
    else:
        whosturn = 3

    gamestarting.set()
    bets[smallblind - 1] = 1
    bets[bigblind - 1] = 2
    turns[whosturn - 1].set()

def recv(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)
    msg_length = int(msg_length)
    msg = conn.recv(msg_length).decode(FORMAT)
    return(msg)

def biggestelement(listofnumbers):
    biggest = None
    for i in range(0, len(listofnumbers)):
        if listofnumbers[i] != None:
            if biggest == None:
                biggest = listofnumbers[i]
            elif listofnumbers[i] > biggest:
                biggest = listofnumbers[i]
    return biggest

def allthesame(listofnumbers):
    newlist = []
    for i in range(0, len(listofnumbers)):
        if listofnumbers[i] != None:
            newlist.append(listofnumbers[i])
    for i in range(0, len(newlist)):
        if i == 0:
            pass
        elif newlist[i] == newlist[i - 1]:
            pass
        else:
            return False
    return True

def sendtoallclients(message):
    for conn in playerdict:
        conn.send(message.encode(FORMAT))

def pushtopot(bets):
    global pot
    for i in range(0, len(bets)):
        if bets[i] != None:
            pot += bets[i]
            bets[i] = 0

def atleasttwoplayers(bets):
    active = 0
    for i in bets:
        if i != None:
            active += 1
    if active > 1:
        return True
    else:
        return False

def betweenturns():
    global howmanyturns
    global betting
    global firstturn
    global whosturn
    global bets
    global turns
    global smallblind
    howmanyturns = 0
    whosturn = smallblind
    set = False
    while set == False:
        if bets[whosturn - 1] != None:
            turns[whosturn - 1].set()
            set = True
        else:
            whosturn += 1
    betting = True
    firstturn = True

def betweenrounds():
    global pot
    global betting
    global firstturn
    global playerdict
    global table
    global smallblind
    global bigblind
    global whosturn
    global players
    global bets
    global turns
    global startnewround
    global cards
    global roundover
    global howmanyturns

    cards = []
    pot = 0
    betting = True
    firstturn = False
    roundover = False
    howmanyturns = 0
    for i in range(0, len(bets)):
        bets[i] = 0
    deck = []
    for number in range(2, 15):
        for suit in range(1, 5):
            deck.append([number, suit])

    neededcards = (players * 2) + 5
    for i in range(0, neededcards):
        card = deck[random.randint(0, len(deck) - 1)]
        cards.append(card)
        deck.remove(card)
    n = 0
    for conn in playerdict:
        playerdict[conn][1] = [(cards[n]), cards[n+1]]
        n = n + 2

    table = cards[-5:]
    if smallblind == players:
        smallblind = 1
    else:
        smallblind += 1
    if bigblind == players:
        bigblind = 1
    else:
        bigblind += 1
    if bigblind == players:
        whosturn = 1
    else:
        whosturn = bigblind + 1
    bets[smallblind - 1] = 1
    bets[bigblind - 1] = 2
    turns[whosturn - 1].set()
    startnewround.set()

def validbets():
    global bets
    j = 0
    for i in range(0, len(bets)):
        if bets[i] != None:
            j += 1
    return j

def turn(conn):
    global allclear
    global roundover
    global betting
    global turns
    global playerdict
    global bets
    global pot
    global firstturn
    global howmanyturns
    conn.send(("Bets: " + str(bets)).encode(FORMAT))
    time.sleep(0.1)
    conn.send(("Pot: " + str(pot)).encode(FORMAT))
    time.sleep(0.1)
    while betting == True:
        turns[playerdict[conn][0] - 1].wait()
        turns[playerdict[conn][0] - 1].clear()
        if betting == False:
            return 0
        howmanyturns += 1
        tempvar = 1
        while tempvar:
            nextplayerindex = (playerdict[conn][0] + tempvar)
            if nextplayerindex > len(turns):
                nextplayerindex = nextplayerindex % len(turns)
            if bets[nextplayerindex - 1] != None:
                tempvar = False
                if howmanyturns >= validbets():
                    firstturn = False
            else:
                tempvar += 1
            if len(bets) == 2 and bets[1] != 0:
                firstturn = False

        conn.send("Your turn".encode(FORMAT))
        #Receive call, fold, raise, or check
        action = recv(conn)
        if action == "call":
            bets[playerdict[conn][0] - 1] = biggestelement(bets)
        elif action[0:5] == "raise":
            bets[playerdict[conn][0] - 1] = biggestelement(bets) + float(action[5:])
        elif action == "fold":
            pot += bets[playerdict[conn][0] - 1]
            bets[playerdict[conn][0] - 1] = None
            if atleasttwoplayers(bets) == False:
                for i in range(0, len(bets)):
                    if bets[i] != None:
                        sendtoallclients("[WINNER]Player" + str(i + 1) + " wins this pot")
                        time.sleep(0.1)
                        break
                pushtopot(bets)
                sendtoallclients("Pot: " + str(pot))
                betting = False
                roundover = True
                for i in range(0, len(turns)):
                    turns[i].set()
                turns[playerdict[conn][0] - 1].clear()
                allclear.set()
                return 0

        else:
            pass
        #checking if round of betting is over
        if firstturn == False and allthesame(bets) == True:
            sendtoallclients("Bets: " + str(bets))
            time.sleep(0.1)
            pushtopot(bets)
            sendtoallclients("Pot: " + str(pot))
            time.sleep(0.1)
            sendtoallclients("Round of betting is over.")
            time.sleep(0.1)
            betting = False
            for i in range(0, len(turns)):
                turns[i].set()
            turns[playerdict[conn][0] - 1].clear()
            allclear.set()
            return 0
        else:
            sendtoallclients("Bets: " + str(bets))
            time.sleep(0.1)
            sendtoallclients("Pot: " + str(pot))
            time.sleep(0.1)
            turns[nextplayerindex - 1].set()

def winner():
    global bets
    global playerdict
    global turns
    global cards
    global table
    activecards = []
    ties = []
    indices = []
    tieindices = []
    del cards[-5:]
    print(cards)
    i = 0
    j = 0
    while j < len(bets):
        if bets[j] != None:
            activecards.append(setfinder([cards[i]] + [cards[i + 1]] + table))
            indices.append(j)
        i += 2
        j += 1
    while len(activecards) > 1:
        if setcomparer(activecards[0], activecards[1]) == "P1 wins":
            del activecards[1]
            del indices[1]
        elif setcomparer(activecards[0], activecards[1]) == "P2 wins":
            del activecards[0]
            del indices[0]
            ties = []
            tieindices = []
        elif setcomparer(activecards[0], activecards[1]) == "Tie":
            ties.append(activecards[1])
            tieindices.append(indices[1])
            del activecards[1]
            del indices[1]
        else:
            print("Bug")
    winners = activecards + ties
    winnerindices = indices + tieindices
    if len(winners) == 1:
        sendtoallclients("[WINNER]Player" + str(winnerindices[0] + 1) + " wins this pot " + str(winners[0]))
    else:
        for i in range(0, len(winners)):
            sendtoallclients("[WINNER]Player" + str(winnerindices[i] + 1) + " has tied for this pot. " + str(winners[i]))

def handle_client(conn, addr):
    global minplayersreached
    global firstturn
    global allplayersready
    global players
    global readyplayers
    global gamestarting
    global playerdict
    global smallblind
    global bigblind
    global whosturn
    global pot
    global betting
    global roundover
    global allclear

    print(f"[NEW CONNECTION] {addr} connected.")
    recv(conn)
    readyplayers += 1
    minplayersreached.wait()
    if readyplayers == players:
        allplayersready.set()
    gamestarting.wait()
    conn.send("Game is starting...".encode(FORMAT))
    time.sleep(0.1)
    conn.send(("Playernumber: " + str(playerdict[conn][0])).encode(FORMAT))
    time.sleep(0.1)
    while True:
        if playerdict[conn][0] == smallblind:
            conn.send("You are smallblind".encode(FORMAT))
            time.sleep(0.1)
        elif playerdict[conn][0] == bigblind:
            conn.send("You are bigblind".encode(FORMAT))
            time.sleep(0.1)
        else:
            conn.send("You are not blind".encode(FORMAT))
            time.sleep(0.1)
        conn.send(("Your cards are: " + str(playerdict[conn][1])).encode(FORMAT))
        time.sleep(0.1)
        turn(conn)
        if roundover == False:
            conn.send(("Table: " + str(table[0:3])).encode(FORMAT))
            allclear.wait()
            time.sleep(0.1)
            if playerdict[conn][0] == 1:
                allclear.clear()
                betweenturns()
            turn(conn)
            if roundover == False:
                conn.send(("Table: " + str(table[0:4])).encode(FORMAT))
                allclear.wait()
                time.sleep(0.1)
                if playerdict[conn][0] == 1:
                    allclear.clear()
                    betweenturns()
                turn(conn)
                if roundover == False:
                    conn.send(("Table: " + str(table)).encode(FORMAT))
                    allclear.wait()
                    time.sleep(0.1)
                    if playerdict[conn][0] == 1:
                        allclear.clear()
                        betweenturns()
                    turn(conn)
                    if roundover == False:
                        allclear.wait()
                        time.sleep(0.1)
                        if playerdict[conn][0] == 1:
                            allclear.clear()
                            print("Finding winner...")
                            winner()
        if playerdict[conn][0] == 1:
            print("between rounds")
            betweenrounds()
        startnewround.wait()
        time.sleep(0.1)
        if playerdict[conn][0] == 1:
            startnewround.clear()

def start():
    global playerdict
    global minplayersreached
    global acceptingconnections
    global players


    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while acceptingconnections:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        players += 1
        playerdict.update({conn: [players]})
        #checking if there are at least 2 players
        if players == 2:
            minplayersreached.set()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")

startthread = threading.Thread(target = start)
print("[STARTING] Server is starting...")
startthread.start()

#waiting for minimum players
minplayersreached.wait()
#waiting for game to start
allplayersready.wait()
acceptingconnections = False

gameinitializer()
