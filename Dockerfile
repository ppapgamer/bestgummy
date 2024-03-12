FROM ubuntu
RUN apt-get update -y
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
RUN apt install texlive-latex-extra -y
RUN apt install dvipng -y
RUN apt install python3-pip -y
RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
WORKDIR /app
COPY . . 
CMD ["python3", "bestgummy2.py"]