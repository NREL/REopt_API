server ENV.fetch("STAGE1_URL"), :user => "deploy", :roles => ["web", "app", "db"]

set :app_env, "staging"
set :django_settings_module, "reopt_api.staging_settings"
set :base_domain, ENV.fetch("STAGE_BASEDOMAIN_URL")
set :base_domain_aliases, [ENV.fetch("STAGE_URL"), ENV.fetch("STAGE1_URL"), ENV.fetch("STAGE2_URL")]
