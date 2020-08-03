ffmpeg used udp by default but can specify tcp or udp
+ tcp 
`ffmpeg -f v4l2 -i /dev/video0 -f rtsp -rtsp_transport tcp rtsp://localhost:8554/live.sdp`

+ udp
`ffmpeg -f v4l2 -i /dev/video0 -f rtsp -rtsp_transport udp rtsp://localhost:8000/live.sdp`
---

ffmpeg -f v4l2 -i /dev/video0 -f rtsp rtsp://localhost:8554/anpr

ffplay -rtsp_flags listen rtsp://localhost:8888/live.sdp?tcp

---

### **using complete filters**

ffmpeg -f v4l2 -framerate 25 -i /dev/video0 -vf scale=512:418 -vcodec libx264 -pix_fmt yuv420p -tune zerolatency -preset ultrafast -threads 4 -crf 24 -f rtsp -rtsp_transport tcp rtsp://admin:adminpassword@0.0.0.0:8554/live.sdp


### **taking snapshots**
ffmpeg -loglevel panic -rtsp_transport udp -i rtsp://192.168.1.192:554/onvif1 -f image2 -s 640x480 -pix_fmt yuvj420p -r 1/2 -updatefirst 1 image.jpg

ffmpeg -loglevel panic -i /dev/video0 -f image2 -s 640x480 -pix_fmt yuvj420p -r 1/2 -updatefirst 1 image.jpg

ffmpeg -f video4linux2 -i /dev/v4l/by-id/usb-0c45_USB_camera-video-index0 -vframes 2 test%3d.jpeg

fswebcam -r 640x480 --jpeg 85 -D 1 shot.jpg