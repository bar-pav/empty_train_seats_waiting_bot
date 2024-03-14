FROM python:3.10

ADD ./bot /opt/app/bot
#ADD ./conf /opt/app/conf
COPY requirements.txt /opt/app
WORKDIR /opt/app

# fetch app specific deps

RUN pip install -r requirements.txt

# specify the port number the container should expose
EXPOSE 5505

# run the application
CMD ["python", "./bot/my_bot.py"]