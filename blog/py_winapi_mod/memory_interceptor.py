import memory_reader
from memory_reader import kernel32
import memory_writer
from const import *

from typing import Dict, Any
import ctypes
from ctypes import wintypes
import time


# Modify the register to control whether the thread raises a single-step exception
def _set_single_step(thread_id: int, enable: bool = True) -> None:
    context = WOW64_CONTEXT()
    thread_handle = kernel32.OpenThread(THREAD_ALL_ACCESS, False, thread_id)
    context.ContextFlags = WOW64_CONTEXT_CONTROL
    kernel32.Wow64GetThreadContext(thread_handle, ctypes.byref(context))
    if enable:
        context.EFlags |= 0x100
    else:
        context.EFlags &= ~0x100
    kernel32.Wow64SetThreadContext(thread_handle, ctypes.byref(context))
    kernel32.CloseHandle(thread_handle)


# Configure whether an access violation exception is raised
def _set_protection(
    process_handle: wintypes.HANDLE,
    patterns: Dict[str, Dict[str, Any]],
    enable: bool = True,
) -> None:
    if enable:
        PROTECTION_CONST = PAGE_NOACCESS
    else:
        PROTECTION_CONST = PAGE_EXECUTE_READWRITE

    for pattern in patterns.values():
        old_protection = wintypes.DWORD()
        kernel32.VirtualProtectEx(
            process_handle,
            pattern["s_base_address"],
            pattern["s_size"],
            PROTECTION_CONST,
            ctypes.byref(old_protection),
        )


# Intercept access to memory and toggle its state
def intercept_memory_access(
    pid: int, patterns: Dict[str, Dict[str, Any]], timeout: int
) -> None:
    kernel32.DebugActiveProcess(pid)

    process_handle = memory_reader.open_process_handle(pid)

    f_time = None
    _set_protection(process_handle, patterns, enable=True)
    ss_thread_ids = []

    debug_event = DEBUG_EVENT()
    try:
        while True:
            if f_time and time.time() - f_time > timeout:
                print("Timeout")
                break
            if kernel32.WaitForDebugEventEx(ctypes.byref(debug_event), 1000):
                if debug_event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT:
                    if (
                        debug_event.u.Exception.ExceptionRecord.ExceptionCode
                        == STATUS_WX86_SINGLE_STEP
                    ):
                        _set_protection(process_handle, patterns, enable=True)
                        ss_thread_ids.remove(debug_event.dwThreadId)
                    if (
                        debug_event.u.Exception.ExceptionRecord.ExceptionCode
                        == STATUS_ACCESS_VIOLATION
                    ):
                        access_address = debug_event.u.Exception.ExceptionRecord.ExceptionInformation[
                            1
                        ]
                        _set_single_step(debug_event.dwThreadId, enable=True)
                        ss_thread_ids.append(debug_event.dwThreadId)
                        _set_protection(process_handle, patterns, enable=False)

                        for pattern in patterns.values():
                            if (
                                access_address >= pattern["s_base_address"]
                                and access_address
                                < pattern["s_base_address"] + pattern["s_size"]
                            ):
                                memory_writer.write_data_to_memory(
                                    process_handle,
                                    pattern["w_base_address"],
                                    pattern["w_data"],
                                )
                                if not f_time:
                                    print("First hit")
                                    f_time = time.time()

                kernel32.ContinueDebugEvent(
                    debug_event.dwProcessId, debug_event.dwThreadId, DBG_CONTINUE
                )
            else:
                print("No debug event occurred")
                continue
    finally:
        print("Cleaning up")
        _set_protection(process_handle, patterns, enable=False)

        for thread_id in ss_thread_ids:
            _set_single_step(thread_id, enable=False)

        memory_writer.write_data_to_memory(
            process_handle,
            patterns["before"]["w_base_address"],
            patterns["before"]["w_data"],
        )

        kernel32.DebugActiveProcessStop(pid)
        kernel32.CloseHandle(process_handle)
