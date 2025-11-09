import logging

class driverExampleClass:
    
    def __init__(self):
        logging.info("Constructor de driverExampleClass")
        
    def driverMethod(self):
        """
        Logs an informational message indicating that the driverMethod has been called.

        This method is intended for tracing or debugging purposes to confirm invocation.
        """
        logging.info("Estoy llamando a driverMethod")