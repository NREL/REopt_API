server ENV.fetch("C110P_URL"), :user => "deploy", :roles => ["web", "app", "db"]

set :app_env, "internal_c110p"
set :django_settings_module, "reopt_api.internal_c110p_settings"
set :base_domain, ENV.fetch("C110P_URL")