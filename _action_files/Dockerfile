FROM ruby:3.3-alpine

# Install system dependencies
RUN apk add --no-cache \
    build-base \
    openssl-dev \
    nodejs \
    npm \
    git \
    bash \
    dos2unix \
    python3 \
    py3-pip \
    openssh-client

# Install Jekyll and bundler
RUN gem install bundler -v 2.7.2
RUN gem install jekyll

# Install Python dependencies for notebook conversion
RUN pip3 install --break-system-packages \
    watchdog[watchmedo] \
    nbconvert \
    nbformat \
    fastcore \
    nbdev

WORKDIR /fastpages
COPY . .
RUN chmod u+x action_entrypoint.sh
RUN chmod u+x word2post.sh
RUN dos2unix /fastpages/*.sh

CMD [ "/fastpages/action_entrypoint.sh" ]
