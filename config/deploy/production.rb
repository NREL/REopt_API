server ENV.fetch("PROD1_URL"), :user => "deploy", :roles => ["web", "app", "db"]
server ENV.fetch("PROD2_URL"), :user => "deploy", :roles => ["web", "app"]

set :app_env, "production"
set :django_settings_module, "reopt_api.production_settings"
set :base_domain, ENV.fetch("PROD_URL")
set :base_domain_aliases, [ENV.fetch("PROD1_URL"), ENV.fetch("PROD2_URL")]
