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
    DB_TEST_NAME = "reopt_lite_${BRANCH_NAME.replaceAll(/[^\w]+/, '_')}"  
  }

  options {
    disableConcurrentBuilds()
  }

  stages{
    stage("Test") {
      steps {
        sh """
	virtualenv env --python=/bin/python3
	source env/bin/activate
	source /opt/xpressmp/bin/xpvars.sh
	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$WORKSPACE/reo/src/:/opt/xpressmp/lib
	export XPRESS=/opt/xpressmp/bin
	cat /opt/xpressmp/bin/xpauth.xpr

	cp keys.py.test keys.py
	pip3 install -r requirements.txt
	python manage.py test -v 2 --failfast --noinput
	"""
      }
    }
  }
}
