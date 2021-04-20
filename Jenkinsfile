@Library("tada-jenkins-library") _

pipeline {
  agent none
  options {
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: "365"))
  }

  environment {
    IMAGE_REPO_DOMAIN = credentials("reopt-api-image-repo-domain")
    DEVELOPMENT_BASE_DOMAIN = credentials("reopt-api-development-base-domain")
    DEVELOPMENT_TEMP_BASE_DOMAIN = credentials("reopt-api-development-temp-base-domain")
    STAGING_BASE_DOMAIN = credentials("reopt-api-staging-base-domain")
    STAGING_TEMP_BASE_DOMAIN = credentials("reopt-api-staging-temp-base-domain")
    PRODUCTION_DOMAIN = credentials("reopt-api-production-domain")
    XPRESS_LICENSE_HOST = credentials("reopt-api-xpress-license-host")
    NREL_ROOT_CERT_URL_ROOT = credentials("reopt-api-nrel-root-cert-url-root")
  }

  parameters {
    booleanParam(
      name: "DEVELOPMENT_DEPLOY",
      defaultValue: false,
      description: "Development Deploy: Deploy to development.",
    )

    booleanParam(
      name: "STAGING_DEPLOY",
      defaultValue: false,
      description: "Staging Deploy: Deploy to staging for a non-master branch (master will always be deployed).",
    )
  }

  stages {
    stage("app-agent") {
      agent {
        dockerfile {
          filename "Dockerfile"
          additionalBuildArgs "--pull --build-arg XPRESS_LICENSE_HOST='${XPRESS_LICENSE_HOST}' --build-arg NREL_ROOT_CERT_URL_ROOT='${NREL_ROOT_CERT_URL_ROOT}'"
        }
      }

      stages {
        stage("tests") {
          steps {
            sh "echo 'Container built and running.'"
          }
        }
      }
    }

    stage("deploy-agent") {
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
        DOCKER_BASE_IMAGE_DIGEST = tadaDockerBaseImageDigest(dockerfile: "Dockerfile")
        XPRESS_LICENSE_HOST = credentials("reopt-api-xpress-license-host")
        NREL_ROOT_CERT_URL_ROOT = credentials("reopt-api-nrel-root-cert-url-root")
      }

      stages {
        stage("deploy") {
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

            stage("deploy-development") {
              when { expression { params.DEVELOPMENT_DEPLOY } }

              environment {
                DEPLOY_ENV = "development"
                DEPLOY_SHARED_RESOURCES_NAMESPACE_POD_LIMIT = "6"
                DEPLOY_APP_NAMESPACE_POD_LIMIT = "20"
              }

              steps {
                withKubeConfig([credentialsId: "kubeconfig-nrel-reopt-test"]) {
                  tadaWithWerfNamespaces(rancherProject: "reopt-api-dev", primaryBranch: "master", dbBaseName: "reopt_api_development", baseDomain: "${DEVELOPMENT_BASE_DOMAIN}") {
                    withCredentials([string(credentialsId: "reopt-api-werf-secret-key", variable: "WERF_SECRET_KEY")]) {
                      sh """
                        werf deploy \
                          --values=./.helm/values.deploy.yaml \
                          --values=./.helm/values.${DEPLOY_ENV}.yaml \
                          --secret-values=./.helm/secret-values.${DEPLOY_ENV}.yaml \
                          --set='branchName=${BRANCH_NAME}' \
                          --set='ingressHost=${DEPLOY_BRANCH_DOMAIN}' \
                          --set='tempIngressHost=${tadaDeployBranchDomain(baseDomain: env.DEVELOPMENT_TEMP_BASE_DOMAIN, primaryBranch: "master")}' \
                          --set='dbName=${DEPLOY_BRANCH_DB_NAME}'
                      """
                    }
                  }
                }
              }
            }

            stage("deploy-staging") {
              when { expression { params.STAGING_DEPLOY || env.BRANCH_NAME == "master" } }

              environment {
                DEPLOY_ENV = "staging"
                DEPLOY_SHARED_RESOURCES_NAMESPACE_POD_LIMIT = "6"
                DEPLOY_APP_NAMESPACE_POD_LIMIT = "20"
              }

              steps {
                withKubeConfig([credentialsId: "kubeconfig-nrel-reopt-prod"]) {
                  tadaWithWerfNamespaces(rancherProject: "reopt-api-stage", primaryBranch: "master", dbBaseName: "reopt_api_staging", baseDomain: "${STAGING_BASE_DOMAIN}") {
                    withCredentials([string(credentialsId: "reopt-api-werf-secret-key", variable: "WERF_SECRET_KEY")]) {
                      sh """
                        werf deploy \
                          --values=./.helm/values.deploy.yaml \
                          --values=./.helm/values.${DEPLOY_ENV}.yaml \
                          --secret-values=./.helm/secret-values.${DEPLOY_ENV}.yaml \
                          --set='branchName=${BRANCH_NAME}' \
                          --set='ingressHost=${DEPLOY_BRANCH_DOMAIN}' \
                          --set='tempIngressHost=${tadaDeployBranchDomain(baseDomain: env.STAGING_TEMP_BASE_DOMAIN, primaryBranch: "master")}' \
                          --set='dbName=${DEPLOY_BRANCH_DB_NAME}'
                      """
                    }
                  }
                }
              }
            }

            stage("deploy-production") {
              when { branch "master" }

              environment {
                DEPLOY_ENV = "production"
                DEPLOY_SHARED_RESOURCES_NAMESPACE_POD_LIMIT = "6"
                DEPLOY_APP_NAMESPACE_POD_LIMIT = "70"
              }

              steps {
                withKubeConfig([credentialsId: "kubeconfig-nrel-reopt-prod"]) {
                  tadaWithWerfNamespaces(rancherProject: "reopt-api-prod", primaryBranch: "master") {
                    withCredentials([string(credentialsId: "reopt-api-werf-secret-key", variable: "WERF_SECRET_KEY")]) {
                      sh """
                        werf deploy \
                          --values=./.helm/values.deploy.yaml \
                          --values=./.helm/values.${DEPLOY_ENV}.yaml \
                          --secret-values=./.helm/secret-values.${DEPLOY_ENV}.yaml \
                          --set='ingressHost=${PRODUCTION_DOMAIN}'
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
