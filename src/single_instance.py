import win32event
import win32api
import winerror
import sys

class SingleInstance:
    def __init__(self):
        self.mutexname = "ClipboardManagerMutex_{D0E858DF-985E-4907-B7FB-8D732C3FC3B9}"
        self.mutex = win32event.CreateMutex(None, False, self.mutexname)
        self.lasterror = win32api.GetLastError()

    def already_running(self):
        return (self.lasterror == winerror.ERROR_ALREADY_EXISTS)
