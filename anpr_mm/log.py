import logging

def this(message):
    logging.debug(message)

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.DEBUG, datefmt="%H:%M:%S")
this('Log Ready.')

"""this? maybe I previously play with JS"""