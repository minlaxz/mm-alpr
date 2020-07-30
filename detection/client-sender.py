# This should be run on raspberry_pi OR image_sender_host
import socket, time, os, argparse, imagezmq

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
	help="ip address of the server to which the client will connect")
ap.add_argument("-d", "--debug", required=False, default=False,
    help="debug info.")
args = vars(ap.parse_args())

w, h = 512, 416
if args['debug']: print('stream width:{0} height:{1}'.format(w,h))
x64 = None
if 'arm' in os.uname()[-1]:
    if args['debug']: print('ARM Host.')
    from imutils.video import VideoStream
    x64 = False 
else:
    if args['debug']: print('x64 Host')
    import cv2
    x64 = True

# initialize the ImageSender object with the socket address of the server
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
	args["server_ip"]))
if args['debug']: print('image sender object is initialized.')

if x64:
    vs = cv2.VideoCapture(0)
    if args['debug']: print('set camera_index:0 -- x64')
    vs.set(3, h)
    vs.set(4, w)
    if args['debug']: print('set camera dimention.')
else:
    if args['debug']: print('set camera_index: piCamera -- arm')
    vs = VideoStream(usePiCamera=True, resolution=(w, h)).start()
    if args['debug']: print('set camera dimention.')
if args['debug']: print('Camera is warming up.')
time.sleep(2.0) # time to warm up the camera
print('Camera is started.')
while True:
    if x64:
        _ , frame = vs.read()
    else:
        frame = vs.read() 
    sender.send_image(socket.gethostname(), frame)
