FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CFLAGS=-static

RUN apt-get update -y && \
    apt-get install build-essential cmake pkg-config -y

RUN pip3 install --upgrade pip && \
    git clone -b 'v19.21' --single-branch https://github.com/davisking/dlib.git && \
    cd dlib/ && \
    python3 setup.py install --set BUILD_SHARED_LIBS=OFF

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

EXPOSE 8000

#RUN chmod 777 ./config/start.sh \
#    && ln -s /code/config/start.sh /

WORKDIR /code/config

ENTRYPOINT ["./start.sh"]
# ENTRYPOINT ["python", "manage.py"]
# CMD ["runserver", "0.0.0.0:8000"]