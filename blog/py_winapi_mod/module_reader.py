from typing import Optional, List, Dict, Any
import ctypes
from ctypes import wintypes


psapi = ctypes.WinDLL("psapi")


# Detailed documentation can be found at: https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-moduleinfo
class MODULEINFO(ctypes.Structure):
    _fields_ = [
        ("lpBaseOfDll", wintypes.LPVOID),
        ("SizeOfImage", wintypes.DWORD),
        ("EntryPoint", wintypes.LPVOID),
    ]


# Enumerates all modules in the specified process and returns a list of module information.
def get_process_module_list(
    process_handle: wintypes.HANDLE,
) -> Optional[List[Dict[str, Any]]]:
    LIST_MODULES_ALL = 0x03
    num_modules = 1024
    while True:
        module_handles = (wintypes.HMODULE * num_modules)()
        needed = wintypes.DWORD()
        # Detailed documentation can be found at: https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-enumprocessmodulesex
        if not psapi.EnumProcessModulesEx(
            process_handle,
            ctypes.byref(module_handles),
            ctypes.sizeof(module_handles),
            ctypes.byref(needed),
            LIST_MODULES_ALL,
        ):
            return None

        num_modules = needed.value // ctypes.sizeof(wintypes.HMODULE)
        if len(module_handles) >= num_modules:
            break

    modules = []
    for i in range(num_modules):
        path_buffer = ctypes.create_unicode_buffer(512)
        mi = MODULEINFO()
        module = {}
        try:
            # Detailed documentation can be found at: https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getmodulefilenameexw
            if psapi.GetModuleFileNameExW(
                process_handle,
                module_handles[i],
                path_buffer,
                ctypes.sizeof(path_buffer),
            ):
                module["path"] = path_buffer.value
            if psapi.GetModuleInformation(
                process_handle, module_handles[i], ctypes.byref(mi), ctypes.sizeof(mi)
            ):
                module["base_address"] = mi.lpBaseOfDll
                module["size"] = mi.SizeOfImage
                module["entry_point"] = mi.EntryPoint
        except:
            continue
        finally:
            if len(module) > 0:
                modules.append(module)
    return modules


if __name__ == "__main__":
    # Example: Retrieve and display module details and associated memory regions for a process based on its window title.
    import memory_reader

    def _print_dict(d: Dict) -> None:
        print({k: hex(v) if type(v) == int else v for k, v in d.items()})

    pid = memory_reader.get_process_id_by_window_title("foo")
    process_handle = memory_reader.open_process_handle(pid)
    modules = get_process_module_list(process_handle)
    regions = memory_reader.get_memory_regions(process_handle)

    for module in modules:
        print("===== Module Info =====")
        _print_dict(module)
        print("----- Associated Memory Info -----")
        for region in regions:
            if (
                region["base_address"] >= module["base_address"]
                and region["base_address"] < module["base_address"] + module["size"]
            ):
                _print_dict(region)
