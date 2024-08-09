# This is the base image for the proxy service
FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="Aayush Kapoor"

# Take the default.conf.tpl file and copy it to the /etc/nginx directory of the image
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl

# Copy the uwsgi_params file to the /scripts directory of the image
COPY ./uwsgi_params /etc/scripts/uwsgi_params

# Copy the run.sh file to the / directory of the image
COPY ./run.sh /run.sh


# Set the environment variables
ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

USER root

#1. Create a directory /vol/static to store the static files
#2. Change the permissions of the /vol/static directory to 755 (read permission for everyone and write permission for the owner)
#3. Create an empty default.conf file in the /etc/nginx/conf.d directory
#4. Change the owner of the default.conf file to nginx user so that the nginx user can write to it
#5. Change the permissions of the run.sh file to make it executable

RUN mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh

# Default volume for static files
VOLUME /vol/static

USER nginx

CMD ["/run.sh"]