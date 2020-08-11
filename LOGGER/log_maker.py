import logging
def logger(logtext):
    log = "makelog.txt"
    logging.basicConfig(filename=log, level=logging.DEBUG,
                        format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    logging.info(logtext)

if __name__=="__main__":
    logger('text')