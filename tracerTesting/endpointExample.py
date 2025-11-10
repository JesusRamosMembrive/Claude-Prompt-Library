import logging
from middlewareExample import middlewareAPI


class endpointExampleClass:

    def __init__(self):
        self.middleware = middlewareAPI()

    def endpointMethod(self):
        """
        Executes the endpoint logic by logging messages before and after calling the apiDriveMethod.

        This method logs an informational message indicating it is about to call the middleware's
        apiDriveMethod, invokes that method, and then logs another message after the call.

        Returns:
            None
        """
        logging.info("Estoy en endpointExample antes de llamar a apiDriveMethod")
        self.middleware.apiDriveMethod()
        logging.info("Estoy en endpointExample después de llamar a apiDriveMethod")
