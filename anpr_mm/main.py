import os, imagezmq, cv2, traceback, sys, time
from PIL import Image, ImageTk
import tkinter as tk
import threading 
"""to handle multi thread processes."""
import detector as dkv

debug =  True

# class Plate:
#     def __init__(self,image_rgb):
#         self.image = image_rgb

#     def perspective(self):
#         print('perspective transformation is handling.')
#         cv2.imshow('client_name', self.image)

class Application:
    def __init__(self, debug=False):

        self.debug = debug
        self.dkv = dkv
        """dakrnet is initialized here"""
        self.dkv.initialize_darknet()

        self.image_hub = imagezmq.ImageHub()

        self.current_image = None

        self.root = tk.Tk()
        self.root.title("MM ANPR")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        self.panel = tk.Label(self.root)
        self.panel.pack(padx=10, pady=10)

        btn = tk.Button(self.root, text="smth Command!", command=self.blackhole)
        btn.pack(fill="both", expand=True, padx=10, pady=10)

        self.text = tk.StringVar()
        self.label = tk.Label(self.root, textvariable=self.text)
        self.label.pack(padx=10, pady=10)
        self.master_loop()

    def master_loop(self):
        # 
        client_name, resized_rgb = self.image_hub.recv_image()
        """ We need to process received image here """
        detections = self.dkv.YOLO(resized_rgb)

        if detections:
            self.text.set("Detected")
            x = threading.Thread(target=self.thread_func, args=(1,), daemon=False)
            if x.is_alive():
                self.debug: print('current thread is on going.')
            else:
                x.start()
                self.debug: print('started another thread.')
            print("Main : main thread done.")
        else:
            self.text.set('Nothing')

        #self.text.set("Detected.") if detections else self.text.set("Nothing.")

        self.current_image = Image.fromarray(resized_rgb)
        self.client_name = client_name
        imgtk = ImageTk.PhotoImage(image=self.current_image) 

        self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
        self.panel.config(image=imgtk)  # show the image

        self.image_hub.send_reply(b"OK")
        self.root.after(30, self.master_loop)  # call the same function after 30 milliseconds

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        _, image = self.image_hub.recv_image()
        self.image_hub.send_reply(b"STOP")
        self.root.destroy()
        self.image_hub.close()
        cv2.destroyAllWindows()  # it is not mandatory in this application

    def thread_func(self, thread_name):
        print("Thread %s: starting", thread_name)
        print('Door is opening.')
        self.text.set("Door is opening.")
        time.sleep(3)
        print("Thread %s: finishing", thread_name)

    def blackhole(self):
        pass


app = Application(debug=debug)
app.root.mainloop()



# try:
#     while True:
#         client_name, resized_rgb = image_hub.recv_image()        

#         """YOLO method needs rgb frame"""
#         detections = dkv.YOLO(resized_rgb=resized_rgb)

#         if detections:
#             detected = dkv.cropDetected(detections=detections, img=resized_rgb)
#             plate = Plate(detected)
#             plate.perspective()
#             #cv2.imshow(client_name, detected)
#         else:
#             pass
#             # print(False)
#             cv2.imshow(client_name, resized_rgb)
#         cv2.waitKey(1)

#         image_hub.send_reply(b"OK")

# except (KeyboardInterrupt, SystemExit):
#     _, resized_rgb = image_hub.recv_image()
#     image_hub.send_reply(b'STOP')
#     #pass  # Ctrl-C was pressed to end program;

# except Exception as ex:
#     print('Python error with no Exception handler:')
#     print('Traceback error:', ex)
#     traceback.print_exc()

# finally:
#     print('finally')
#     cv2.destroyAllWindows()
#     image_hub.close()
#     sys.exit()
