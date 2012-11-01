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
    
class CustomSettingError(ArchiveException):
    def __init__(self, value,setting,session):
        self.value = value 
    def __str__(self):
        return repr(self.value)
    

class UpdateXMLVersionException(Exception):
    pass  