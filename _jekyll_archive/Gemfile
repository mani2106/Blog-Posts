source "https://rubygems.org"

ruby "~> 3.3.0"

# Hello! This is where you manage which Jekyll version is used to run.
# When you want to use a different version, change it below, save the
# file and run `bundle install`. Run Jekyll with `bundle exec`, like so:
#
#     bundle exec jekyll serve
#
# This will help ensure the proper Jekyll version is running.
# Happy Jekylling!
gem "jekyll", "~> 4.3"
# This is the default theme for new Jekyll sites. You may change this to anything you like.
gem "minima"
# To upgrade, run `bundle update github-pages`.
# gem "github-pages", group: :jekyll_plugins
# If you have any plugins, put them here!
group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.17"
  gem 'jekyll-octicons', "~> 19.8"
  gem 'jekyll-remote-theme', "~> 0.4"
  gem "jekyll-twitter-plugin", "~> 2.1"
  gem 'jekyll-relative-links', "~> 0.7"
  gem 'jekyll-seo-tag', "~> 2.8"
  gem 'jekyll-toc', "~> 0.19"
  gem 'jekyll-gist', "~> 1.5"
  gem 'jekyll-paginate', "~> 1.1"
  gem 'jekyll-sitemap', "~> 1.4"
end

gem "kramdown-math-katex", "~> 1.0"
gem "jemoji", "~> 0.13"

# Windows and JRuby does not include zoneinfo files, so bundle the tzinfo-data gem
# and associated library.
install_if -> { RUBY_PLATFORM =~ %r!mingw|mswin|java! } do
  gem "tzinfo", "~> 2.0"
  gem "tzinfo-data", "~> 1.2024"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.2", :install_if => Gem.win_platform?

gem "nokogiri", "~> 1.18"
gem "rexml", "~> 3.4"
gem "activesupport", "~> 7.2"
gem "faraday", "~> 2.12"

