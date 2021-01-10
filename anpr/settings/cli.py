from configparser import SafeConfigParser
import logging
from threading import Thread
from os import path

class StartParser:
    def __init__(self, parser):
        self.config_logger()
        self.parser = parser
        self.config_path = './anpr_mm.cfg'

        try:
            if (path.exists(self.config_path)):
                self.parser.read(self.config_path)
            else: raise FileNotFoundError(logging.debug('404 config File not Found.'))
            self.read_settings()

        except (KeyboardInterrupt):
            self.destory(False)
        
        except (FileNotFoundError):
            self.destory()

        except Exception as e:
            logging.debug(e)
            self.destory()
    

    def read_settings(self):
        logging.debug('Debug    >>> {}'.format(self.parser.get('no-gui', 'debug')))
        logging.debug('Test     >>> {}'.format(self.parser.get('no-gui', 'test')))
        logging.debug('Localrun >>> {}'.format(self.parser.get('no-gui', 'localrun')))
        c = input('[e]dit / [a]pply / ctrl c: ')
        if (c == 'e'): self.get_settings()
        elif ( c == 'a'): self.apply_settings()
        else: self.destory(False)  # """no choice or wrong choice. discard."""
    
    def get_settings(self):
        debug = self.parser.get('no-gui','debug')
        test = self.parser.get('no-gui','test')
        localrun = self.parser.get('no-gui','localrun')
        debug = True if (debug in ['True']) else False
        test = True if (test in ['True']) else False
        localrun = True if (localrun in ['True']) else False

        ch = input('Debug : {} [c]hange : '.format(debug))
        if ('c' in ch): self.parser.set('no-gui','debug',str(not debug))

        ch1 = input('Test : {} [c]hange : '.format(test))
        if ('c' in ch1): self.parser.set('no-gui','test',str(not test))

        ch2 = input('Self Camera : {} [c]hange : '.format(localrun))
        if ('c' in ch2): self.parser.set('no-gui','localrun',str(not localrun))

        self.read_settings()

    def destory(self,*flag):
        if flag:
            logging.debug("\n")
            logging.debug('exiting, all changes will not be saved.')
        else: logging.debug('exiting.')
        exit()

    def apply_settings(self):
        with open(self.config_path ,'w') as f:
            self.parser.write(f)
        logging.debug('applied.')

    def config_logger(self):
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.DEBUG, datefmt="%H:%M:%S")
        logging.debug('Ready logger!')


if __name__ == "__main__":
    StartParser(SafeConfigParser())