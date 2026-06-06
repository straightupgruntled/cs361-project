import zmq

context = zmq.Context()

socket = context.socket(zmq.REP)
socket.bind("tcp://*:7052")

print("Undo/Redo Microservice running on tcp://localhost:7052")

# History timeline
history = []

# Current position in history
current_index = -1


def record_action(request_data):
    global current_index

    action = request_data["action"]
    state = request_data["state"]

    # Remove redo history if user records
    # a new action after undoing.
    del history[current_index + 1 :]

    history.append({"action": action, "state": state})

    current_index = len(history) - 1

    return {
        "status": "success",
        "message": "Action recorded.",
        "current_index": current_index,
    }


def undo_action():
    global current_index

    if current_index <= 0:
        return {"status": "error", "message": "Nothing to undo."}

    current_index -= 1

    print(current_index)

    entry = history[current_index]

    return {
        "status": "success",
        "command": "undo",
        "action": entry["action"],
        "state": entry["state"],
    }


def redo_action():
    global current_index

    if current_index >= len(history) - 1:
        return {"status": "error", "message": "Nothing to redo."}

    current_index += 1

    entry = history[current_index]

    return {
        "status": "success",
        "command": "redo",
        "action": entry["action"],
        "state": entry["state"],
    }


def process_request(request_data):
    command = request_data["command"]

    if command == "record":
        return record_action(request_data)
    elif command == "undo":
        return undo_action()
    elif command == "redo":
        return redo_action()
    else:
        return {"status": "error", "message": "Invalid command."}


# MAIN MICROSERVICE LOOP #
while True:
    try:
        request_data = socket.recv_json()

        print(f"Undo/Redo Request Received!")

        response = process_request(request_data)

        socket.send_json(response)

    except Exception as error:

        socket.send_json({"status": "error", "message": str(error)})
