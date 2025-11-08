import binascii
import struct

upload_speed = 20
data = "hello world"


def chunker(data: bytes, chunksize: int):
    mv = memoryview(data)
    chunk_index = 1
    for i in range(0, len(mv), chunksize):
        yield bytes(mv[i : i + chunksize]), chunk_index
        chunk_index += 1


def send_with_tag(
    data, msgtype: str, dataclass: str, filename: str = "", filepath: str = ""
):
    def packer_sender(magic: str, msgType: int, totalSize: int, chunkIndex: int, totalChunks: int, checkSum:, dataClass: int, payloadIndex: int, payloadIndexContent, payload): 
        struct.pack(fmt="!4sBQII", magic, msgType, totalSize, chunkIndex, totalChunks, checkSum, dataClass, payloadIndex, payloadIndexContent, payload)
    msg_types = ["cmd", "img", "fil", "hds", "ptc"]
    data_classes = [
        "srnV",
        "cmdI",
        "cmdO",
        "logK",
        "deWH",
        "fDow",
        "fDoI",
        "fDoL",
        "fUpL",
        "fUpS",
        "fUpL",
        "misC",
    ]
    msg_type_no = None
    data_class_no = None
    for inx, item in enumerate(msg_types):
        if msgtype.lower() == item.lower():
            msg_type_no = inx
            break
        else:
            continue

    for inx, item in enumerate(data_classes):
        if dataclass.lower() == item.lower():
            data_class_no = inx
            break
        else:
            continue
    if msg_type_no == None or data_class_no == None:
        return
    if not data or msgtype != "" or dataclass != "":
        return

    magic = b"END0"

    if isinstance(data, str):
        data_bytes = data.encode("utf-8")
    else:
        data_bytes = data

    total_size = len(data_bytes)
    chunk_size = int(upload_speed * 0.75)
    needs_chunking = total_size > chunk_size
    if needs_chunking:
        payload_funced = chunker(data_bytes, chunk_size)
        for chunk, index in payload_funced:
            print(chunk, index)
    else:
        chunk = 1
        index = 1
        print(data_bytes)


send_with_tag(data, "imp", "oisc")
# THIS IS INCOMPLETE LADS...IM SWITCHING TO SOCKETIO FUCK YOU IM DONE TORTURING MYSELF