server "reopt-stage-api1.nrel.gov", :user => "deploy", :roles => ["web", "app", "db"]

set :app_env, "staging"
set :base_domain, "reopt-stage-api1.nrel.gov"
