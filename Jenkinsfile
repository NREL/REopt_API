@Library("tada-jenkins-library") _

pipeline {
  agent any

  environment {
    PATH = "${JENKINS_HOME}/.rbenv/bin:${JENKINS_HOME}/.rbenv/shims:/usr/pgsql-9.6/bin:/usr/local/bin:/sbin:/usr/sbin:/bin:/usr/bin"
    BUILD_TYPE ="jenkins"
    LD_LIBRARY_PATH = "/usr/pgsql-9.6/lib"
    DB_HOSTNAME = "localhost"
    DB_PORT = "5496"
    DB_USERNAME = "postgres"
    DB_PASSWORD = "postgres"  
    XPRESS = "/opt/xpressmp/bin"
  }

  stages{
    stage("Test") {
      steps {
        sh """
	virtualenv env
	source env/bin/activate
	source /opt/xpressmp/bin/xpvars.sh
	cat /opt/xpressmp/bin/xpauth.xpr

	cp keys.py.test keys.py
	pip install -r requirements.txt
	mosel
	"""
      }
    }
  }
}
