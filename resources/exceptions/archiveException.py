from exceptions import Exception

class ArchiveException(Exception):
    pass

class ArchiveThreadException(ArchiveException):
    pass
        
class CustomInfoError(ArchiveException):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class CustomError(ArchiveException):
    def __init__(self, value):
        self.value = value 
    def __str__(self):
        return repr(self.value) 		

class CustomWarningError(ArchiveException):
    def __init__(self, value):
        self.value = value 
    def __str__(self):
        return repr(self.value)
