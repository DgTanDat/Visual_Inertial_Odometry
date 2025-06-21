import requests
from interface.global_interface import *

# Firebase database URL (replace with your own URL)
DATABASE_URL = "https://imucar-default-rtdb.asia-southeast1.firebasedatabase.app/"

# Node to access (e.g., "users.json")
NODE = "instruction.json"

# Optional: Auth token or API key if required
AUTH = "'AIzaSyAJ9NWzrhKBnos2XqpvJes507JcA_sgMog'"

# Construct the URL
url = f"{DATABASE_URL}/{NODE}?auth={AUTH}"  # Add `?auth=` only if auth is required

def get_inst():
    global STOP, GOSTRAIGHT, TURNLEFT, TURNRIGHT, NONE, nextStateQueue
    defaultInst = "0000300003000030000300001"

    # Send GET request
    response = requests.get(url)

    # Handle the response
    if response.status_code == 200:
        instructions = response.json()
        print("data: ", instructions)
    else:
        print("Failed to retrieve data. HTTP Status Code:", response.status_code)
        print("Error message:", response.text)
        instructions = defaultInst

    for instruction in instructions:
        if instruction == '0':
            nextStateQueue.put(GOSTRAIGHT)
            print("put g")
        if instruction == '1':
            nextStateQueue.put(STOP)
            print("put t")
        if instruction == '2':
            nextStateQueue.put(TURNLEFT)
            print("put l")
        if instruction == '3':
            nextStateQueue.put(TURNRIGHT)
            print("put r")
