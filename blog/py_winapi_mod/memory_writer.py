from memory_reader import kernel32

import ctypes
from ctypes import wintypes


# Writes the given bytes to the specified memory address in the target process.
def write_data_to_memory(
    process_handle: wintypes.HANDLE, address: int, value: bytes
) -> None:
    size = len(value)
    data = ctypes.create_string_buffer(size)
    data.value = value
    kernel32.WriteProcessMemory(
        process_handle,
        ctypes.c_void_p(address),
        data,
        size,
        None,
    )
