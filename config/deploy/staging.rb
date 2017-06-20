server "reopt-stage-api1.nrel.gov", :user => "deploy", :roles => ["web", "app", "db"]

set :app_env, "staging"
set :django_settings_module, "reopt_api.staging_settings"
set :base_domain, "reopt-stage-api1.nrel.gov"
