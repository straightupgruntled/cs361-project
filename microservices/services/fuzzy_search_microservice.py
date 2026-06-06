from thefuzz import fuzz
import zmq

# Simple ratio


context = zmq.Context()

socket = context.socket(zmq.REP)
socket.bind("tcp://*:7053")

print("FuzzySearch Microservice running on tcp://localhost:7053")


while True:
    message = socket.recv_string()
    if len(message) > 0:
        recieved = message
        if recieved[0] == "R":
            state = 0
            compare = ""
            currentWord = ""
            wordList = []
            readingWord = False
            for char in recieved[2:]:
                if state == 1:
                    if readingWord:
                        if char != "'":
                            currentWord += char
                        else:
                            readingWord = False
                            wordList.append(currentWord)
                            currentWord = ""
                    else:
                        if char == "'":
                            readingWord = True
                if state == 0:
                    if char != " ":
                        compare += char
                    else:
                        state = 1
            print(wordList)
            print(compare)
            fuzzyRatios = []
            for word in wordList:
                fuzzyRatios.append(fuzz.ratio(word, compare))
            socket.send_string(str(fuzzyRatios))
