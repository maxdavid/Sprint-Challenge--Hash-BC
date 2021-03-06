import hashlib

from timeit import default_timer as timer

if __name__ == "__main__":
    try:
        f = open("table.py", "w+")
        f.write("hash_table = {\n")
        dict_table = {}
        count = 0x0
        proof = 0

        start = timer()

        while count <= 0xFFFFFF:
            proof_hash = hashlib.sha256(str(proof).encode()).hexdigest()
            hash_int = int(proof_hash[:6],16)

            if hash_int not in dict_table:
                dict_table[hash_int] = proof
                f.write(f"{hash_int}: {proof},\n")
                print(
                    f"Proof for {proof_hash[:6]} found. Only {0xffffff - count} left to go!"
                )
                count += 1
            proof += 1

        f.write("}\n")
        f.close()

        print(f"Table completed in {'{:01.2f}'.format(timer() - start)} seconds.")

    except KeyboardInterrupt:
        f.write("}\n")
        f.close()

