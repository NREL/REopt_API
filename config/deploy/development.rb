server "reopt-dev-api1.nrel.gov", :user => "deploy", :roles => ["web", "app", "db"]

set :app_env, "development"
set :base_domain, "reopt-dev-api1.nrel.gov"
