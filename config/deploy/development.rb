server "reopt-dev-api1.nrel.gov", :user => "deploy", :roles => ["web", "app", "db"]

set :app_env, "development"
set :django_settings_module, "reopt_api.dev_settings"
set :base_domain, "reopt-dev-api1.nrel.gov"

# TODO: Remove this if we get more flexible branched deployments setup (with
# our normal DNS subdomain support).
set :branch, ENV.fetch("DEV_BRANCH").gsub("origin/", "")
