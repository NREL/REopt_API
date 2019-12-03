server "reopt-stage-api1.nrel.gov", :user => "deploy", :roles => ["web", "app", "db"]

set :app_env, "staging"
set :django_settings_module, "reopt_api.staging_settings"
set :base_domain, "reopt-stage-api.its.nrel.gov"
set :base_domain_aliases, ["reopt-stage-api.nrel.gov", "reopt-stage-api1.nrel.gov", "reopt-stage-api2.nrel.gov"]

# TODO: Remove this if we get more flexible branched deployments setup (with
# our normal DNS subdomain support).
set :branch, ENV.fetch("DEV_BRANCH").gsub("origin/", "")
