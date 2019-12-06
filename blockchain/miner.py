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
╦  ┌─┐┌┬┐┌┐ ┌┬┐┌─┐  ╔═╗┌─┐ ┬ ┌┐┌
║  ├─┤│││├┴┐ ││├─┤  ║  │ │ │ │││
╩═╝┴ ┴┴ ┴└─┘─┴┘┴ ┴  ╚═╝└─┘ ┴ ┘└┘
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

    print(f"\n{color.BOLD}Searching for next proof{color.END}")
    last_hash = hashlib.sha256(str(last_proof).encode()).hexdigest()
    proof = random.randint(420, 6969696969696969696969)

    # spinning_cursor = threading.Thread(target=Spinny, args=())
    # spinning_cursor.start()
    block_poller = threading.Thread(target=PollNewBlock, args=(last_proof, 3))
    block_poller.start()

    while not valid_proof(last_hash, proof):
        if new_block:
            # spinning_cursor.join()
            # block_poller.join()
            return
        proof += 1

    print(
        "Proof found: "
        + str(proof)
        + " in "
        + "{:01.2f}".format(timer() - start)
        + " seconds"
    )
    # spinning_cursor.join()
    # block_poller.join()
    return proof


def PollNewBlock(last_proof, interval):
    global new_block

    def get_last_proof():
        r = requests.get(url=node + "/last_proof")
        try:
            data = r.json()
            return data.get("proof")
        except json.decoder.JSONDecodeError:
            print(
                f"{color.RED}Unexpected response from server when polling for changes.{color.END}"
            )

    while True:
        time.sleep(interval)
        new_proof = get_last_proof()

        if last_proof != new_proof:
            new_block = True
            break


def Spinny():
    def spinning_cursor():
        while True:
            for cursor in "|/-\\":
                yield cursor

    spinner = spinning_cursor()
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


def get_total_coins(_id, node):
    r = requests.get(url=node + "/full_chain")
    try:
        chain = r.json()["chain"]
    except json.decoder.JSONDecodeError:
        print(f"{color.RED}{color.BOLD}Unexpected response from server.{color.END}")
        return
    except Exception:
        raise requests.exceptions.RequestException(
            "Unexpected error fetching blockchain."
        )

    coins = 0
    for block in chain:
        if (
            "recipient" in block["transactions"]
            and block["transactions"]["recipient"] == _id
        ):
            coins += 1

    return coins


if __name__ == "__main__":
    print(f"\u001b[38;5;190m{titlecard}\033[0m")
    # What node are we interacting with?
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "https://lambda-coin.herokuapp.com/api"

    # Load or create ID
    f = open("my_id.txt", "r")
    _id = f.read()
    print("ID is", _id)
    f.close()

    if _id == "NONAME\n":
        print("ERROR: You must change your name in `my_id.txt`!")
        exit()

    coins_mined = 0
    total_coins = get_total_coins(_id, node)
    print(
        f"You currently have {color.GREEN}{total_coins}{color.END} coins in the chain."
    )

    # Run forever until interrupted
    while True:
        try:
            new_block = False

            # Get the last proof from the server
            print("Getting last proof...")
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
                print(f"{color.YELLOW}New block found, refreshing...{color.END}")
                continue

            # Found, let's send to server
            post_data = {"proof": new_proof, "id": _id}
            r = requests.post(url=node + "/mine", json=post_data)

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
                print(f"\n{color.GREEN}{color.BOLD}SUCCESS!{color.END}")
                print(f"{color.GREEN}Lambda coins mined: {coins_mined}{color.END}")
            else:
                print(f"{color.RED}{data.get('message')}{color.END}")
        except KeyboardInterrupt:
            print(f"{color.BOLD}\nKeyboard Interrupt received.{color.END}")
            print("Quitting...")
            break
        except requests.exceptions.RequestException:
            print(f"{color.RED}Error connecting to server. Retrying...{color.END}")
            continue
        except Exception:
            continue

    print(f"\nLambda coins mined: {color.GREEN}{coins_mined}{color.END}")
    print(
        f"Total lambda coins in the chain: {color.GREEN}{coins_mined + total_coins}{color.END}"
    )

