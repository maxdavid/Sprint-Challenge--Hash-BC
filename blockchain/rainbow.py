import hashlib
from tinydb import TinyDB, Query

from timeit import default_timer as timer

if __name__ == "__main__":
    try:
        # f = open("table.py", "w+")
        # f.write("hash_table = {\n")
        db = TinyDB('table.json')
        dict_table = {}
        count = 0x0
        proof = 0

        start = timer()
        query = Query()

        while count <= 0xFFFFFF:
            proof_hash = hashlib.sha256(str(proof).encode()).hexdigest()
            hash_int = int(proof_hash[:6],16)

            # if hash_int not in dict_table:
            if (len(db.search(query.hash == hash_int)) == 0):
                # dict_table[hash_int] = proof
                # f.write(f"{hash_int}: {proof},\n")
                db.insert({'hash': hash_int, 'proof': proof})
                print(
                    f"Proof for {proof_hash[:6]} found. Only {0xffffff - count} left to go!"
                )
                count += 1
            proof += 1

        # f.write("}\n")
        # f.close()

        print(f"Table completed in {'{:01.2f}'.format(timer() - start)} seconds.")

    except KeyboardInterrupt:
        pass
        # f.write("}\n")
        # f.close()
