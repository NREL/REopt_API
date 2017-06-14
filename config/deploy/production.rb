server "reopt-prod-api1.nrel.gov", :user => "deploy", :roles => ["web", "app", "db"]

set :app_env, "production"
set :django_settings_module, "reopt_api.production_settings"
set :base_domain, "reopt-prod-api1.nrel.gov"
