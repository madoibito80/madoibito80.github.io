import memory_reader
import module_reader

from typing import Tuple, List
from ctypes import wintypes


# Resolves the final address by following a chain of pointers.
def get_address_by_pointer_offsets(
    process_handle: wintypes.HANDLE, pointers: Tuple[str, List]
) -> int:
    ADDRESS_SIZE = 4
    ENDIAN = "little"

    modules = module_reader.get_process_module_list(process_handle)
    mname, offsets = pointers
    module = [x for x in modules if x["path"].endswith(mname)][0]
    address = module["base_address"] + offsets[0]
    for offset in offsets[1:]:
        address = memory_reader.read_memory_region(
            process_handle, address, ADDRESS_SIZE
        )
        address = int.from_bytes(address, ENDIAN)
        address += offset
    return address


if __name__ == "__main__":
    # Example: Read and unpack 3D coordinates from memory.
    import struct

    pid = memory_reader.get_process_id_by_window_title("foo")
    process_handle = memory_reader.open_process_handle(pid)
    pointers = ("bar.dll", [0x2577F0, 0x160, 0x3C, 0x118, 0x130, 0x30, 0x8])
    address = get_address_by_pointer_offsets(process_handle, pointers)
    b = memory_reader.read_memory_region(process_handle, address, 12)
    x = struct.unpack("<f", b[:4])[0]
    y = struct.unpack("<f", b[4:8])[0]
    z = struct.unpack("<f", b[8:])[0]
    print(f"address: {hex(address)}")
    print(f"x: {x:.2f}")
    print(f"y: {y:.2f}")
    print(f"z: {z:.2f}")
