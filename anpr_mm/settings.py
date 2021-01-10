from configparser import SafeConfigParser
import pylaxz
import os

cfg = "./settings/config.ini"

if not os.path.exists(cfg):
    pylaxz.printf("config file not found!", _int=True, _err=True)


class Settings:
    def __init__(self):
        self.parser = SafeConfigParser()
        self.parser.read(cfg)
        self.debug = True if (self.parser.get("global", "debug") in ["True"]) else False
        self.test = True if (self.parser.get("global", "test") in ["True"]) else False
        self.localrun = (
            True if (self.parser.get("global", "localrun") in ["True"]) else False
        )
        self.gui = True if (self.parser.get("mode", "gui") in ["True"]) else False

    @property
    def configs(self):
        return self

    @configs.setter
    def configs(self, arg):
        self.test = arg

    @classmethod
    def callclass(cls):
        pass

    def edit(self):
        u = input("Debug : `{}` [c]hange : ".format(self.debug))
        if "c" in u:
            self.parser.set("global", "debug", str(not self.debug))
        u = input("Test : `{}` [c]hange : ".format(self.test))
        if "c" in u:
            self.parser.set("global", "debug", str(not self.test))
        u = input("Localrun : `{}` [c]hange : ".format(self.localrun))
        if "c" in u:
            self.parser.set("global", "debug", str(not self.localrun))
        if "a" in input("[a]pply? : "):
            self.apply()
        else:
            pylaxz.printf("cancled.", _int=True)

    def apply(self):
        with open(cfg, "w") as f:
            self.parser.write(f)
        pylaxz.printf("settings applied.", _int=True)


if __name__ == "__main__":
    s = Settings()
    pylaxz.printf(s.configs.test, _int=True)

    s.configs = True
    pylaxz.printf(s.configs.test, _int=True)



    # pylaxz.printf("Debug: {}".format(activity.debug), _int=True)
    # pylaxz.printf("Test: {} Detection or Not".format(activity.test), _int=True)
    # pylaxz.printf(
    #     "Localrun: {} Local Camera or TCP Camera".format(activity.localrun), _int=True
    # )
