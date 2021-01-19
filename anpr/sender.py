"""
File - : __file__
This should be run on Client Side : Raspberry PI or like Low Power PC

Example:
    app = Sender()
    app.run()
"""

import time, imzmqx, traceback
from socket import gethostname
import cv2
import pylaxz
from configs.settings import Settings


class Sender:
    def __init__(self):
        self.size = {'w':512, 'h':416}
        s = Settings()
        self.debug, self.nodetect, self.hostcamera, self.gui = s.appconfigs
        self.server = Settings.get_server().parser.get("server", "host")

    def run(self):
        self.init_camera()
        self.connect_server()
        self.send_frame()

    def connect_server(self):
        if self.debug:
            pylaxz.printf("Server is tcp/" + str(self.server))
        connect_to = "tcp://{}:5555".format(self.server)
        self.image_sender = imzmqx.ImageSender(connect_to=connect_to)
        if self.debug:
            pylaxz.printf("Waiting to upload...", _int=True)

    def send_frame(self):
        try:
            while True:
                _, image = self.camera.read()
                resized_rgb = image if self.test else cv2.resize( cv2.cvtColor(image, cv2.COLOR_BGR2RGB), (self.size['w'], self.size['h']), interpolation=cv2.INTER_LINEAR)

                repl = self.image_sender.send_image(gethostname(), resized_rgb)
                self.count += 1
                if self.debug:
                    pylaxz.printf("`frame is sent, ` count : {0}, reply :{1}".format(self.count, repl))
                if repl == b"STOP":
                    self.userAbord = True
                    break
        except (KeyboardInterrupt, SystemExit):
            pylaxz.printf("Keyboard is Interrupted", _int=1)
            pass  # Ctrl-C was pressed to end program
        except Exception as e:
            pylaxz.printf("error with no Exception handler:", _int=1)
            print("Traceback error:", e)
            traceback.print_exc()
        finally:
            pylaxz.printf("--STOP SIGNAL--", _int=True) if self.userAbord else pylaxz.pritnf("Exiting", _int=True)
            self.camera.release()
            if self.debug:
                pylaxz.printf("Released Camera Object.", _int=1)
            self.image_sender.close()
            if self.debug:
                pylaxz.printf("Closed Connection", _int=1)

    def init_camera(self):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(3, self.size['w'])
        self.camera.set(4, self.size['h'])
        pylaxz.printf("Camera is startup up, please wait.", _int=True)
        time.sleep(3.0)

if __name__ == "__main__":
    app = Sender()
    app.run() if not app.hostcamera else exit()
