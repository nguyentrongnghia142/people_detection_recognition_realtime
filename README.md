# People detection and recognition real time
# Buid docker images
* sudo docker build -t detect .
# Run Docker
* sudo docker run -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --privileged --device=/dev/video0:/dev/video0 -it detect
or 
* sudo docker run -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --privileged --device=/dev/video0:/dev/video0 -it detect bash
