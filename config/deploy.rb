# config valid only for current version of Capistrano
lock "3.7.1"

set :application, "reopt_api"
set :repo_url, "git@github.nrel.gov:ndiorio/reopt_api.git"

# Set the base deployment directory.
set :deploy_to_base, "/srv/data/apps"

# Set the user the web app runs as.
set :foreman_user, "www-data-local"
set :file_permissions_users, ["www-data-local"]

# Don't replace github.nrel.gov references for internal servers.
set :bundle_swap_nrel_git_references, false

# Symlink other directories across deploys.
set :linked_dirs, fetch(:linked_dirs, []).push("static/files", "tmp")

# Allow the web user to write files for Xpress
set :file_permissions_paths, fetch(:file_permissions_paths, []).push("static/files", "Xpress")

namespace :app do
  task :pip_install do
    on roles(:app) do
      within release_path do
        execute "virtualenv", "env"
        execute "./env/bin/pip", "install", "-r", "requirements.txt"
      end
    end
  end

  task :keys do
    on roles(:app) do
      execute "ln", "-snf", "/etc/reopt-api-secrets/keys.py", "#{release_path}/keys.py"
    end
  end

  task :migrate do
    on roles(:db) do
      within release_path do
        with "PATH" => "#{release_path}/env/bin:$PATH", "VIRTUAL_ENV" => "#{release_path}/env", "DJANGO_SETTINGS_MODULE" => fetch(:django_settings_module) do
          execute "./env/bin/python", "manage.py", "migrate"
        end
      end
    end
  end

  before "deploy:updated", "app:pip_install"
  before "deploy:updated", "app:keys"
  after "deploy:updated", "app:migrate"
end
