import zmq
from tkinter import filedialog

# Simple ratio


def convertToPossibleFileTypes(list):
    fileTypes = []
    for item in list:
        if item == "all":
            fileTypes.append(("all files", "*.*"))
        else:
            filetype = "*." + item
            newtype = (item + " files", filetype)
            fileTypes.append(newtype)
    return fileTypes


context = zmq.Context()

socket = context.socket(zmq.REP)
socket.bind("tcp://*:7051")

print("FileImporter Microservice running on tcp://localhost:7051")


while True:
    message = socket.recv_string()
    if len(message) > 0:
        if message[0] == "R":
            print(message)
            currentList = []
            currentWord = ""
            for char in message[2:]:
                if char != " ":
                    currentWord += char
                else:
                    currentList.append(currentWord)
                    currentWord = ""
            currentList.append(currentWord)
            file_path = filedialog.askopenfilename(
                title="Select a file", filetypes=convertToPossibleFileTypes(currentList)
            )
            if not file_path:
                socket.send_string("unknown file path")
            else:
                socket.send_string(file_path)
