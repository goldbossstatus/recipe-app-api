# from dockerhub tag name
FROM python:3.7-alpine
# usefull to know who is maintaining the dockerimage
MAINTAINER goldbossstatus

#set pyton environment variable (python will not buffer outputs)
ENV PYTHONUNBUFFERED 1

# copy from
COPY ./requirements.txt /requirements.txt
# this takes the reuirements.txt file that we just created and installs it w/pip
RUN pip install -r /requirements.txt

#creates empty folder called /app
RUN mkdir /app
# switches to this /app dir as the default location to start from when opening
WORKDIR /app
# copies from local machine (app folder) to the app folder we created on our image
# this allows us to create the code here (local machine) and copy it into our
# docker image.
COPY ./app /app

# create user for running applications ONLY
RUN adduser -D user
# if we dont add this user than the dockerIMAGE will run the application from
# root account (NOT RECCOMENDED). IF SOMEBODY COMPROMISES THE APPLICATION THAT MEANS
# THEY CAN HAVE ROOT ACCESS TO THE WHOLE IMAGE, WHEREAS IF WE HAVE A USER JUST
# FOR OUR APPLICATION, IT LIMITS THE SCOPE AND HAVOC THAT AN ATTACKER CAN DEAL
USER user
