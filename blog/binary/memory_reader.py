from typing import Optional, List, Dict, Any
import win32gui
import win32process

import ctypes
from ctypes import wintypes

kernel32 = ctypes.WinDLL("kernel32")


# Retrieves the process ID (PID) for a given window title.
def get_process_id_by_window_title(window_title: str) -> Optional[int]:
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid
    else:
        return None


# Contains details about process memory segments.
# Detailed documentation can be found at: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-memory_basic_information
class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("PartitionId", wintypes.WORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


# Retrieves a list of memory regions from a specified process that are currently allocated and in use.
def get_memory_regions(process_handle: int) -> List[Dict[str, Any]]:
    MEM_COMMIT = 0x1000  # Region is currently allocated and in use by the process.

    current_address = 0
    regions = []
    while True:
        mbi = MEMORY_BASIC_INFORMATION()
        try:
            kernel32.VirtualQueryEx(
                process_handle,
                current_address,
                ctypes.byref(mbi),
                ctypes.sizeof(mbi),
            )
        except:
            break
        finally:
            if mbi.State == MEM_COMMIT:
                regions.append(
                    {
                        "base_address": mbi.BaseAddress,
                        "allocation_base": mbi.AllocationBase,
                        "size": mbi.RegionSize,
                        "type": mbi.Type,
                    }
                )
        current_address += mbi.RegionSize
    return regions


# Reads an immutable block of memory from the specified process and returns it as bytes.
def read_memory_region(
    process_handle: wintypes.HANDLE, base_address: int, size: int
) -> Optional[bytes]:
    region_data = (ctypes.c_byte * size)()

    if kernel32.ReadProcessMemory(
        process_handle, base_address, ctypes.byref(region_data), size, None
    ):
        return bytes(region_data)
    else:
        return None


# Opens a process with all access rights using its PID and returns the process handle.
# Details on access rights can be found at: https://learn.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights
def open_process_handle(pid: int) -> wintypes.HANDLE:
    PROCESS_ALL_ACCESS = 0x001FFFFF
    return kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)


# Returns a list of dictionaries each containing 'base_address', 'allocation_base', 'size', 'type', and 'data' keys.
def get_memory_state_by_window_title(window_title: str) -> List[Dict[str, Any]]:
    pid = get_process_id_by_window_title(window_title)
    process_handle = open_process_handle(pid)

    if not process_handle:
        return []

    regions = get_memory_regions(process_handle)
    for i in range(len(regions)):
        data = read_memory_region(
            process_handle, regions[i]["base_address"], regions[i]["size"]
        )
        regions[i]["data"] = data
    kernel32.CloseHandle(process_handle)
    return regions
