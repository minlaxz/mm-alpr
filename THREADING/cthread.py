import threading
import time
import logging


def f():
    t = threading.currentThread()
    logging.debug('sleeping %s', 3)
    time.sleep(3)
    logging.debug('ending')
    return

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)
    for i in range(3):
        t = threading.Thread(target=f)
        t.setDaemon(False)
        t.start()

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        #logging.debug('joining %s', t.getName())
        #t.join()
