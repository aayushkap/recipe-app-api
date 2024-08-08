FROM python:3.9-alpine3.13
LABEL maintainer="Aayush Kapoor"

# Python output is sent straight to the terminal without delay
ENV PYTHONUNBUFFERED=1

# Copy the requirements file to the /tmp directory of the image
COPY ./requirements.txt /tmp/requirements.txt

# Copy the dev requirements file to the /tmp directory of the image
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Copy to App directory
COPY ./app /app

# Default directory where CMD will run
WORKDIR /app

# Expose the port 8000
EXPOSE 8000

# Set the environment variable DEV to false. This is a placeholder and is updated by the docker-compose file
ARG DEV=false

# All in one RUN command to reduce the number of layers
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base musl-dev postgresql-dev libpq zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol


# Add the /py/bin directory to the PATH. All executables run in the Virtual Environment
ENV PATH="/py/bin:$PATH"

# Run the application as the django-user
USER django-user
