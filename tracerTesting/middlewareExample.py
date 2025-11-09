import logging
from driverExample import driverExampleClass

class middlewareAPI():
    
    def __init__(self):
        self.driver = driverExampleClass()
        
    def apiDriveMethod(self):
        """
        Calls the driverMethod of the associated driver object, logging messages before and after the call.

        This method is intended to act as middleware, providing logging around the invocation of driverMethod
        for debugging or tracing purposes.
        """
        logging.info("Estoy en middlewareAPI antes de llamar a driverMethod")
        self.driver.driverMethod()
        logging.info("Estoy en middlewareAPI después de llamar a driverMethod")