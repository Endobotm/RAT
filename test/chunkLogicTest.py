size = 21689
data = "bro-" + "a" * (size - len("bro-")) + "-end"
size = len(data)
if size > 2000:
    eqt = int(round(size / 2000, 0))
    if size / 2000 > eqt:
        noOfChunks = eqt + 2
    else:
        noOfChunks = eqt + 1
    print(noOfChunks)
    chunk_size = 2000
    for i in range(0, len(data), chunk_size):
        chunk = data[i : i + chunk_size]
        print(
            f"Chunk Number {i//chunk_size + 2}\n{chunk}\n-----------------------------"
        )
