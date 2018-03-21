server "iac-c110p.nrel.gov", :user => "deploy", :roles => ["web", "app", "db"]

set :app_env, "internal_c110p"
set :django_settings_module, "reopt_api.internal_c110p_settings"
set :base_domain, "iac-c110p.nrel.gov"
