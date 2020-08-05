import threading
import time
import logging

def thread_one(name):
    logging.info('starting thread. {}'.format(name))
    time.sleep(5)
    logging.info('finishing thread. {}'.format(name))

def thread_two(name):
    logging.info('starting thread. {}'.format(name))
    time.sleep(10)
    logging.info('finishing thread. {}'.format(name))


if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                            datefmt="%H:%M:%S")
    logging.info('Main thread started')
    t1 = threading.Thread(target=thread_one, args=('one',))
    t2 = threading.Thread(target=thread_two, args=('two',))

    t1.start()
    t2.start()

    logging.info('Main thread done.')