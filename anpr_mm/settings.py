from configparser import SafeConfigParser
import log
import os.path
cfg = "./anpr_mm.cfg"
safe = True
if (not os.path.exists(cfg)):
    log.this("settingparser: config file not found!")
    safe = False

class Activity:
    def __init__(self):
        self.parser = SafeConfigParser()

    def read(self):
        if safe:
            self.parser.read(cfg)
            self.debug = True if (self.parser.get('global','debug') in ['True']) else False
            self.test = True if (self.parser.get('global','test') in ['True']) else False
            self.localrun = True if (self.parser.get('global','localrun') in ['True']) else False
            self.gui = True if (self.parser.get('mode', 'gui') in ['True']) else False
        else:
            log.this("settingparser: read - skipping.")

    def edit(self):
        u = input('Debug : `{}` [c]hange : '.format(self.debug))
        if ('c' in u): self.parser.set('global','debug',str(not self.debug))
        u = input('Test : `{}` [c]hange : '.format(self.test))
        if ('c' in u): self.parser.set('global','debug',str(not self.test))
        u = input('Localrun : `{}` [c]hange : '.format(self.localrun))
        if ('c' in u): self.parser.set('global','debug',str(not self.localrun))
        if ('a' in input('[a]pply? : ')):
            self.apply()
        else:
            log.this('cancled.')

    def apply(self):
        with open(cfg, 'w') as f:
            self.parser.write(f)
        log.this('settings applied.')

if __name__ == "__main__":
    log.this("Runninng standalone.")
    activity = Activity()
    activity.read()
    log.this("Debug: `{}`".format(activity.debug))
    log.this("Test: `{}` Detection or Not".format(activity.test))
    log.this("Localrun: `{}` Local Camera or TCP Camera".format(activity.localrun))
    u = input('Edit? T/F : ')
    if (u == "T"):
        activity.edit()
    elif(u == "F"):
        pass
    else:
        log.this("either T or F !!")