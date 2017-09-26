server "reopt-prod-api1.nrel.gov", :user => "deploy", :roles => ["web", "app", "db"]
server "reopt-prod-api2.nrel.gov", :user => "deploy", :roles => ["web", "app"]

set :app_env, "production"
set :django_settings_module, "reopt_api.production_settings"
set :base_domain, "reopt-prod-api.nrel.gov"
set :base_domain_aliases, ["reopt-prod-api1.nrel.gov", "reopt-prod-api2.nrel.gov"]
