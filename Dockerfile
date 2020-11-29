FROM ubuntu:20.04
FROM python:3.6
RUN apt-get update
RUN apt-get install -y libgl1-mesa-glx
ADD dataset /Doc/dataset/
COPY * /Doc/
COPY requirements.txt /Doc
WORKDIR /Doc
RUN pip3 install -r requirements.txt
RUN pip3 install opencv-python==4.1.2.30
RUN export QT_X11_NO_MITSHM=1

CMD QT_X11_NO_MITSHM=1 python3 /Doc/Opencv-Vgg.py
