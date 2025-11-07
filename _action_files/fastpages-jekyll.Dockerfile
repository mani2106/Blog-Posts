# Defines https://hub.docker.com/repository/docker/fastai/fastpages-jekyll
FROM ruby:3.3-alpine

# Install system dependencies (including Node.js for KaTeX)
RUN apk add --no-cache \
    build-base \
    openssl-dev \
    nodejs \
    npm \
    git

# Set working directory
WORKDIR /srv/jekyll

# Copy project files
COPY . .

# Set permissions only for our project files
RUN chmod -R u+rw .

# Install exact bundler version and gems
RUN gem install bundler -v 2.7.2
RUN bundle install
RUN bundle exec jekyll build
