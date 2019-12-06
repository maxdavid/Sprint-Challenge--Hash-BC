import hashlib
import requests

import sys
import time
import threading
import json

from uuid import uuid4

from timeit import default_timer as timer

import random

from style import color

titlecard = """
╦  ┌─┐┌┬┐┌┐ ┌┬┐┌─┐╔═╗┌─┐┬┌┐┌
║  ├─┤│││├┴┐ ││├─┤║  │ │││││
╩═╝┴ ┴┴ ┴└─┘─┴┘┴ ┴╚═╝└─┘┴┘└┘
"""

new_block = False


def proof_of_work(last_proof):
    """
    Multi-Ouroboros of Work Algorithm
    - Find a number p' such that the last six digits of hash(p) are equal
    to the first six digits of hash(p')
    - IE:  last_hash: ...AE9123456, new hash 123456888...
    - p is the previous proof, and p' is the new proof
    - Use the same method to generate SHA-256 hashes as the examples in class
    """

    start = timer()

    print(f"{color.BOLD}Searching for next proof{color.END}")
    last_hash = hashlib.sha256(str(last_proof).encode()).hexdigest()
    proof = random.randint(420, 6969696969696969)

    Spinny()
    # PollNewBlock(last_proof, interval=1)

    while not valid_proof(last_hash, proof):
        if not new_block:
            proof += 1

    print("Proof found: " + str(proof) + " in " + str(timer() - start))
    return proof


class PollNewBlock(object):
    def __init__(self, last_proof, interval=5):
        self.interval = interval
        self.last_proof = last_proof

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def get_last_proof(self):
        r = requests.get(url=node + "/last_proof")
        try:
            data = r.json()
            return data.get("proof")
        except json.decoder.JSONDecodeError:
            print(
                f"{color.RED}Unexpected response from server when polling for changes.{color.END}"
            )

    def run(self):
        global new_block
        while True:
            time.sleep(self.interval)
            new_proof = self.get_last_proof()
            print(new_proof)
            print(self.last_proof)
            new_block = True

            if self.last_proof == new_proof:
                new_block = True
                break


class Spinny(object):
    def __init__(self, interval=1):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def spinning_cursor(self):
        while True:
            for cursor in "|/-\\":
                yield cursor

    def run(self):
        spinner = self.spinning_cursor()
        while True:
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write("\b")


def valid_proof(last_hash, proof):
    """
    Validates the Proof:  Multi-ouroborus:  Do the last six characters of
    the hash of the last proof match the first six characters of the hash
    of the new proof?

    IE:  last_hash: ...AE9123456, new hash 123456E88...
    """
    proof_hash = hashlib.sha256(str(proof).encode()).hexdigest()
    return last_hash[-6:] == proof_hash[:6]


if __name__ == "__main__":
    print(f"\u001b[38;5;190m{titlecard}\033[0m")
    # What node are we interacting with?
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "https://lambda-coin.herokuapp.com/api"

    coins_mined = 0

    # Load or create ID
    f = open("my_id.txt", "r")
    _id = f.read()
    print("ID is", _id)
    f.close()

    if _id == "NONAME\n":
        print("ERROR: You must change your name in `my_id.txt`!")
        exit()

    # Run forever until interrupted
    try:
        while True:
            new_block = False

            # Get the last proof from the server
            r = requests.get(url=node + "/last_proof")
            try:
                data = r.json()
            except json.decoder.JSONDecodeError:
                print(
                    f"{color.RED}{color.BOLD}Unexpected response from server.{color.END}"
                )
                print("Unable to proceed mining. Quitting...")
                break

            # Work on getting a new proof
            new_proof = proof_of_work(data.get("proof"))

            if new_block:
                print(f"{color.YELLOW}New proof found, refreshing...{color.END}")
                continue

            # Found, let's send to server
            post_data = {"proof": new_proof, "id": _id}
            # r = requests.post(url=node + "/mine", json=post_data)

            try:
                data = r.json()
            except json.decoder.JSONDecodeError:
                print(
                    f"{color.RED}{color.BOLD}Unexpected response from server.{color.END}"
                )
                print("Unable to proceed mining. Quitting...")
                break

            # Confirmation and success message
            if data.get("message") == "New Block Forged":
                coins_mined += 1
                print(
                    f"\n{color.GREEN}Total lambda coins mined: {coins_mined}{color.END}"
                )
            else:
                print(f"{color.RED}{data.get('message')}{color.END}")
    except KeyboardInterrupt:
        print(f"{color.BOLD}\nKeyboard Interrupt received.{color.END}")
        print("Quitting...")

    print(f"\n{color.GREEN}Total lambda coins mined: {coins_mined}{color.END}")
