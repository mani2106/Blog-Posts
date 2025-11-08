# Defines https://hub.docker.com/repository/docker/fastai/fastpages-jekyll
FROM ruby:3.3-alpine

# Install dependencies
RUN apk add --no-cache \
    build-base \
    gcc \
    cmake \
    git \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    nodejs \
    npm

WORKDIR /srv/jekyll

# Install bundler first (cached layer)
RUN gem install bundler -v 2.4.22

# Copy only dependency files first for better caching
COPY Gemfile Gemfile.lock ./
RUN bundle install

# Copy the rest of the application
COPY . .
RUN chmod -R 777 /srv/jekyll

# Build Jekyll site
RUN jekyll build
