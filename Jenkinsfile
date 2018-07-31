@Library("reopt-api-jenkins-library") _

pipeline {
  agent any
  triggers {
    cron("H H(0-5) * * *")
  }

  environment {
    PATH = "${JENKINS_HOME}/.rbenv/bin:${JENKINS_HOME}/.rbenv/shims:/usr/pgsql-9.4/bin:/usr/local/bin:/sbin:/usr/sbin:/bin:/usr/bin"
    LD_LIBRARY_PATH = "/usr/pgsql-9.4/lib"
    DB_HOSTNAME = "localhost"
    DB_PORT = "5494"
    DB_USERNAME = "postgres"
    DB_PASSWORD = "postgres"
  }

    stage("Test") {
      steps {
        python manage.py test
      }
    }
  }
 }
}
