@Library("tada-jenkins-library") _

pipeline {
  agent none
  options {
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: "365"))
  }
  triggers {
    cron(env.BRANCH_NAME == "main" ? "H H(0-5) * * *" : "")
  }

  environment {
    IMAGE_REPO_DOMAIN = credentials("reopt-api-image-repo-domain")
    STAGING_BASE_DOMAIN = credentials("reopt-api-staging-base-domain")
    STAGING_TEMP_BASE_DOMAIN = credentials("reopt-api-staging-temp-base-domain")
    PRODUCTION_DOMAIN = credentials("reopt-api-production-domain")
    XPRESS_LICENSE_HOST = credentials("reopt-api-xpress-license-host")
  }

  parameters {
    booleanParam(
      name: "SKIP_TESTS",
      defaultValue: false,
      description: "Skip tests before deploying.",
    )
    booleanParam(
      name: "FORCE_STAGING_DEPLOY",
      defaultValue: false,
      description: "Staging Only: Force a staging deployment for a non-main branch, even if no pull request is open.",
    )
    choice(
      name: "STAGING_SYNC_DB",
      choices: [
        "",
        "production_latest_nightly",
        "production",
        "staging",
      ],
      description: "Staging Only: Sync the branched database from this environment's database before deploying. The 'production_latest_nightly' option will use the latest dump stored on the db-data-dump Jenkins job. The other options will produce a fresh dump first.",
    )
    string(
      name: "STAGING_SYNC_DB_OVERRIDE_NAME",
      defaultValue: "",
      description: "Staging Only: Override the database name to sync from in order to sync from other branched databases on staging.",
    )
  }

  stages {
    stage("app-agent") {
      agent {
        dockerfile {
          filename "Dockerfile.dev"
          additionalBuildArgs "--pull --build-arg XPRESS_LICENSE_HOST=${XPRESS_LICENSE_HOST}"
        }
      }

      stages {
        stage("tests") {
          when { expression { !params.SKIP_TESTS } }

          environment {
            CI = "true"
            HOME = "/tmp"
            TMPDIR = "/tmp"
            APP_ENV = "test"
            DB_HOST = "localhost"
            DB_PORT = "5412"
            DB_USERNAME = "postgres"
            DB_PASSWORD = "postgres"
            // Use different databases for each branch so Jenkins multibranch runs
            // don't conflict.
            DB_TEST_NAME = "reopt_api_test_${BRANCH_NAME.replaceAll(/[^\w]+/, '_')}"
          }

          parallel {
            stage("echo") {
              steps {
                sh "echo 'Container built and running.'"
              }
            }
          }
        }
      }
    }

    stage("deploy-agent") {
      when { not { triggeredBy "TimerTrigger" } }

      agent {
        docker {
          image "${IMAGE_REPO_DOMAIN}/tada-public/tada-jenkins-kube-deploy:latest"
          args tadaDockerInDockerArgs()
        }
      }

      environment {
        TMPDIR = tadaDockerInDockerTmp()
        WERF_STAGES_STORAGE = ":local"
        WERF_IMAGES_REPO = "${IMAGE_REPO_DOMAIN}/tada-public"
        WERF_TAG_BY_STAGES_SIGNATURE = "true"
        WERF_ADD_ANNOTATION_CI_COMMIT = "ci.werf.io/commit=$GIT_COMMIT"
        WERF_THREE_WAY_MERGE_MODE = "enabled"
        WERF_LOG_VERBOSE = "true"
        DOCKER_BASE_IMAGE_DIGEST = tadaDockerBaseImageDigest(dockerfile: "Dockerfile.dev")
      }

      stages {
        stage("deploy") {
          when { expression { env.CHANGE_ID || params.FORCE_STAGING_DEPLOY || env.BRANCH_NAME == "main" } }

          stages {
            stage("lint") {
              steps {
                withCredentials([string(credentialsId: "reopt-api-werf-secret-key", variable: "WERF_SECRET_KEY")]) {
                  sh "werf helm lint"
                }
              }
            }

            stage("build") {
              steps {
                sh "werf build"
              }
            }

            stage("publish") {
              steps {
                script {
                  docker.withRegistry("https://${IMAGE_REPO_DOMAIN}", "harbor-tada-public") {
                    sh "werf publish"
                  }
                }
              }
            }

            stage("deploy-staging") {
              when { expression { env.CHANGE_ID || params.FORCE_STAGING_DEPLOY || env.BRANCH_NAME == "main" } }

              environment {
                DEPLOY_ENV = "staging"
                DEPLOY_SHARED_RESOURCES_NAMESPACE_POD_LIMIT = "4"
                DEPLOY_APP_NAMESPACE_POD_LIMIT = "5"
              }

              steps {
                withKubeConfig([credentialsId: "kubeconfig-nrel-test"]) {
                  // TODO: Remove `primaryBranch: "rancher"` from these lines once
                  // this is merged into master (to revert to default behavior of
                  // treating "master" as the primary branch).
                  tadaWithWerfNamespaces(rancherProject: "reopt-api-stage", primaryBranch: "rancher", dbBaseName: "reopt_api_staging", baseDomain: "${STAGING_BASE_DOMAIN}") {
                    withCredentials([string(credentialsId: "reopt-api-werf-secret-key", variable: "WERF_SECRET_KEY")]) {
                      sh """
                        werf deploy \
                          --values=./.helm/values.deploy.yaml \
                          --values=./.helm/values.${DEPLOY_ENV}.yaml \
                          --secret-values=./.helm/secret-values.${DEPLOY_ENV}.yaml \
                          --set='ingressHost=${DEPLOY_BRANCH_DOMAIN}' \
                          --set='tempIngressHost=${tadaDeployBranchDomain(baseDomain: env.STAGING_TEMP_BASE_DOMAIN, primaryBranch: "rancher")}' \
                          --set='dbName=${DEPLOY_BRANCH_DB_NAME}' \
                          --set='deploySharedResources=${DEPLOY_BRANCH_DEPLOY_SHARED_RESOURCES}' \
                          --set='sharedResourcesNamespace=${DEPLOY_SHARED_RESOURCES_NAMESPACE_NAME}'
                      """
                    }
                  }
                }
              }
            }

            stage("deploy-production") {
              when { branch "main" }

              environment {
                DEPLOY_ENV = "production"
                DEPLOY_SHARED_RESOURCES_NAMESPACE_POD_LIMIT = "5"
                DEPLOY_APP_NAMESPACE_POD_LIMIT = "10"
              }

              steps {
                withKubeConfig([credentialsId: "kubeconfig-nrel-prod"]) {
                  tadaWithWerfNamespaces(rancherProject: "reopt-api-prod") {
                    withCredentials([string(credentialsId: "reopt-api-werf-secret-key", variable: "WERF_SECRET_KEY")]) {
                      sh """
                        werf deploy \
                          --values=./.helm/values.deploy.yaml \
                          --values=./.helm/values.${DEPLOY_ENV}.yaml \
                          --secret-values=./.helm/secret-values.${DEPLOY_ENV}.yaml \
                          --set='ingressHost=${PRODUCTION_DOMAIN}' \
                          --set='sharedResourcesNamespace=${DEPLOY_SHARED_RESOURCES_NAMESPACE_NAME}'
                      """
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }

  post {
    always {
      tadaSendNotifications()
    }
  }
}
