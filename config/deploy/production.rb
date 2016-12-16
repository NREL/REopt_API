server "reopt-prod-api1.nrel.gov", :user => "deploy", :roles => ["web", "app", "db"]

set :app_env, "production"
set :base_domain, "reopt-prod-api1.nrel.gov"
