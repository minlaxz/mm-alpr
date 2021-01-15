from configparser import SafeConfigParser
import pylaxz, os

cfg = "./configs/config.ini"
section = "global"

if not os.path.exists(cfg):
    pylaxz.printf("config file not found!", _int=True, _err=True)
    raise FileNotFoundError


class Settings:
    def __init__(self):
        pylaxz.printf("settings are initialized.", _int=1)
        self.parser = SafeConfigParser()
        self.parser.read(cfg)

    @property
    def appconfigs(self):
        self._debug = True if (self.parser.get(section, "debug") == "1") else False
        self._nodetect = True if (self.parser.get(section, "test") == "1") else False
        self._hostcamera = True if (self.parser.get(section, "localrun") == "1") else False
        self._gui = True if (self.parser.get(section, "gui") == "1") else False
        return (self._debug, self._nodetect, self._hostcamera, self._gui)

    @property
    def get_network(self):
        cfg = self.parser.get("network", "cfg")
        data = self.parser.get("network", "data")
        weight = self.parser.get("network", "weight")
        thresh = self.parser.get("network", "thresh")
        batch_size = self.parser.get("network","batch_size")
        return ({"cfg":cfg, "data":data, "weight":weight, "thresh":thresh, "batch_size":batch_size})


    @appconfigs.setter
    def appconfigs(self, *arg):
        self.parser.set(
            section,
            "debug",
            str(not self._debug) if arg[0][0] == "y" else str(self._debug),
        )
        self.parser.set(
            section,
            "test",
            str(not self._nodetect) if arg[0][1] == "y" else str(self._nodetect),
        )
        self.parser.set(
            section,
            "localrun",
            str(not self._hostcamera) if arg[0][2] == "y" else str(self._hostcamera),
        )
        self.parser.set(
            section, "gui", str(not self._gui) if arg[0][3] == "y" else str(self._gui)
        )

    @staticmethod
    def show(obj):
        pylaxz.printf(
            "Debug {0} \nNo Detect {1} \nUse Host Camera {2} \nGUI {3}".format(
                obj[0], obj[1], obj[2], obj[3]
            ),
            _int=True,
        )
    
    @classmethod
    def get_server(cls)->object:
        return cls()

    def apply(self):
        with open(cfg, "w") as f:
            self.parser.write(f)
        pylaxz.printf("settings applied.", _int=True)


if __name__ == "__main__":
    s = Settings()
    s.show(s.get_network)
    s.show(s.appconfigs)

    if input("Edit [y/N] : ") == "y":
        pylaxz.printf("Example yyyy or yynn. (only small and be exactly 4)", _int=True)
        choices = input("Debug, Nodetect, Hostcamera, GUI : ")
        if not len(choices) == 4:
            raise ValueError
        else:
            settings.appconfigs = [i for i in choices]
    else:
        pylaxz.printf("Cancled.", _int=True)
        exit()

    settings.show(settings.appconfigs)
    if input("[a]pply ? : ") == "a":
        settings.apply()
    else:
        pass
