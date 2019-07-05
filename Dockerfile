# from dockerhub tag name
FROM python:3.7-alpine
# usefull to know who is maintaining the dockerimage
MAINTAINER goldbossstatus

#set pyton environment variable (python will not buffer outputs)
ENV PYTHONUNBUFFERED 1

# copy from
COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cache postgresql-client jpeg-dev

RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

# this takes the reuirements.txt file that we just created and installs it w/pip
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps
#creates empty folder called /app
RUN mkdir /app
# switches to this /app dir as the default location to start from when opening
WORKDIR /app
# copies from local machine (app folder) to the app folder we created on our image
# this allows us to create the code here (local machine) and copy it into our
# docker image.
COPY ./app /app

# we know where all of the volumne mappings need to be in our contatiner if we need to share this data with otther containers in our service
RUN mkdir -p /vol/web/media
# store recipe images
RUN mkdir -p /vol/web/static
# create user for running applications ONLY
RUN adduser -D user
# now we need to change the ownership of these files to the user we added.
# THIS NEEDS TO BE DONE BEFORE WE SWITCH TO THE USER user
# this sets the ownership of the all of the directories within the volumne directory to our custom user
RUN chown -R user:user /vol/
# Add permissions
# this means that the user/owner can do everything with the dir and the rest can read and execute from the directory
RUN chmod -R 755 /vol/web
# if we dont add this user than the dockerIMAGE will run the application from
# root account (NOT RECCOMENDED). IF SOMEBODY COMPROMISES THE APPLICATION THAT MEANS
# THEY CAN HAVE ROOT ACCESS TO THE WHOLE IMAGE, WHEREAS IF WE HAVE A USER JUST
# FOR OUR APPLICATION, IT LIMITS THE SCOPE AND HAVOC THAT AN ATTACKER CAN DEAL
USER user
