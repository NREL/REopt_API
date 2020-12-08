# Load DSL and set up stages
require "capistrano/setup"

# Include default deployment tasks
require "capistrano/deploy"

# Load the SCM plugin
require "capistrano/scm/git"
install_plugin Capistrano::SCM::Git

# Includes additional plugins
require "capistrano/rbenv"
require "capistrano/bundler"
require "capistrano/file-permissions"
require "captastic/subdomains"
require "captastic/foreman"
require "captastic/nginx"
require "capistrano/tada-defaults"

# Load custom tasks from `lib/capistrano/tasks` if you have any defined
Dir.glob("lib/capistrano/tasks/*.rake").each { |r| import r }