@Library("tada-jenkins-library") _

pipeline {
  agent any

  environment {
    PATH = "${JENKINS_HOME}/.rbenv/bin:${JENKINS_HOME}/.rbenv/shims:/usr/pgsql-9.4/bin:/usr/local/bin:/sbin:/usr/sbin:/bin:/usr/bin"
    LD_LIBRARY_PATH = "/usr/pgsql-9.4/lib"
    DB_HOSTNAME = "localhost"
    DB_PORT = "5494"
    DB_USERNAME = "postgres"
    DB_PASSWORD = "postgres"
  }

  stages{
    stage("Test") {
      steps {
        sh """
	virtualenv env
	source env/bin/activate
	ls $JENKINS_HOME/jobs/reopt_api/
	/*
	cp $JENKINS_HOME/keys.py .
	pip install -r requirements.txt
	python manage.py test --noinput
	*/
	"""
      }
    }
  }
}
