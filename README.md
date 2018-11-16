REopt Lite API
=========

#### Windows Users: see [these](https://github.nrel.gov/REopt/reopt_api/wiki/Setting-up-VirtualBox-development-environment-on-Windows) instructions for running the API locally.  The instructions below apply to Mac users.
NOTE: As of Celery version 4 Windows OS is no longer supported.

These instructions are for REopt API developers and internal NREL users that wish to use the API locally (rather than via the public API server). Note that the REopt API depends on other NREL API's, and thus even when using the API locally one must be logged into the NREL VPN.  However, for special use-cases, the external dependencies can be by-passed (eg. when using a known solar resource and load profile in place of PVWatts and DOE Reference Building, respectively).  For these special use-cases the API can be modified to work offline.

It is highly recommended that you use a virtual environment for installing the API dependencies (and thus running the API). Virtual environments allow you to have a custom set of code modules for any given project and assuage many of the permission headaches that may arise when installing software on an NREL owned computer. In brief, when a virtual environment is 'activated', a call to any module installed in the environment will be used in place of a system module. For example, newer computers are likely to have the latest version of Python installed (3.X), but the API uses Python 2.7. Thus, if one attempts to run the API with the system Python 3.X - it won't work! By installing Python 2.7 in the virtual environment all of the dependency problems are bypassed.

Lastly, to our best efforts we attempt to follow the development workflow described [here](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow), which is based on using feature branches and pull requests in the development process.


## Step 1: Create Project Directory and Download Git Repo
We will refer to the root directory for installing everything as **MY-API-FOLDER**, which can be anywhere you want.

Open a command prompt (or terminal) and:
```
git clone https://github.nrel.gov/REopt/reopt_api.git MY-API-FOLDER
cd MY-API-FOLDER
```

You may see something like:
```
ruby-2.3.5 is not installed.
To install do: 'rvm install ruby-2.3.5'
```
This can be ignored (it is only needed for the web servers).

You can check which branch you are on with `git status`. It should be the master branch.

Next, you need to copy a couple files to your \$HOME directory (which has the alias of ~).
Assuming that you do not already have a `bash_profile` set up (otherwise you will want to copy and paste the contents of the REopt API `.bash_profile` into your bash_profile)
from MY-API-FOLDER:
```
cp .bash_profile ~/.bash_profile
cp .hscfg ~/.hscfg
```
You then need to point the environment variables in the .bash_profile to the correct directories:
```
#------------------------------------------------------------------------------
#  Define the following based on your file structure
#------------------------------------------------------------------------------
#  xpress path
XPRESSDIR="/usr/local/opt/xpress"

#  path to reopt_api/reo/src for SAM SDK C libraries
SRC_DIR="~/projects/reopt/webtool/reopt_api/reo/src"
```

The `XPRESSDIR` is probably correct; but you will need to change the `SRC_DIR`.  Note that for these changes to take effect you need to either `source` them or open a new terminal session.

Lastly, **get *keys.py* from another API developer** (these are access keys that we do not version control).



## Step 2: Python 2.7.15
If you have not already, you need to install [Xcode](https://developer.apple.com/xcode/), which can be found in the app store or installed via terminal with `xcode-select --install`

In a terminal you can check which version of python you have installed with
`python --version`
If the response is:
`Python 2.7.15`
you can skip to Step 2

Sometime in 2018 Mac released an update that caused SSL issues for python 2.7. [Python version 2.7.15](https://www.python.org/downloads/release/python-2715/) fixes these issues. Download and install Python 2.7.15. **You will need to close and reopen your terminal session for the changes to take effect.**

Confirm your version of python with `python --version`.

#### FYI
Mac computers come with python installed in two locations: `/System/Library/Frameworks/Python.framework` and `/usr/bin/python`. These should not be modified since Apple and third party apps may depend on them.  [Homebrew](http://docs.python-guide.org/en/latest/starting/install/osx/) is a popular option for managing Mac software packages, including python versions.


## Step 3: Virtual Environment
Fortunately, there's an [app](https://virtualenv.pypa.io/en/stable/userguide/) for that.

1. `pip install virtualenv`
2. `cd` to **MY-API-FOLDER** (if you are not there already) and find the path to Python 2.7.15 with `which python` (should be something like /usr/local/bin/python)

3. `virtualenv --python==<your/path/to/python2.7.15> env`

   NOTE: Virtual environments can be installed into any directory with any name. However, we already have the "env" directory in the .gitignore file so that the virtual environment is not version controlled if it is installed in MY-API-FOLDER.

4. Activate the virtual environment, which you should do whenever you are using the API:
   - `source env/bin/activate`

   NOTE: If you open a new terminal or command prompt the environment will need to be activated for that session. Also, you can activate the environment from any directory by providing the full path to the `source` command.

#### FYI
DO NOT DO THIS NOW, but for future reference, to deactivate the virtual environment simply `deactivate` from any directory.


## Step 4: Install Requirements
`pip install -r requirements.txt`



## Step 5: Set up database servers
Note that all of the commands below are done in MY-API-FOLDER with the virtual environment activated.

There are four different servers required for the API:
1. Django
2. Celery
3. Redis
4. PostgreSQL

The Django server provides the API itself.
The Celery server manages the celery tasks (functions within the API).
The Redis server is a database for storing and retrieving Celery tasks (aka a message broker).
The PostgreSQL server is a database for all of the data models in the API (stores inputs, outputs, and errors).

In the production environment, we have separate machines for the database components (Redis and PostgreSQL).
However, for development all of the servers are run locally.


### Redis server
To install redis go [here](https://redis.io/topics/quickstart)
Start the server with
```
redis-server
```


### PostgreSQL backend database

The REopt API uses a PostgreSQL datbase to save invalid posts, scenarios, and exceptions.
Separate databases are configured for the three different web servers in MY-API-FOLDER/reopt_api/[dev_settings.py, production_settings.py, staging_settings.py].

When using the API locally a remote database can be used.
However, due to problems that can arise with database migrations (especially when modifying inputs or outputs to the API) it is highly recommended that a local database be used for development.
Also, **a local PostgreSQL database is necessary for running tests.**

To install [PostgreSQL](https://www.postgresql.org/download/):

```
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgresql-client-common postgresql-client
```

Once you've downloaded and installed PostgreSQL, you will want to setup a local database.
By default, when PostgreSQL is installed, it automatically creates a database user that matches your username, and has a default role called 'PostgreSQL'.
To create a local database called "reopt", with a username "reopt", and password "reopt":
```
sudo su - postgres
psql postgres
CREATE USER reopt WITH PASSWORD 'reopt';
ALTER USER reopt CREATEDB;
CREATE DATABASE reopt;
GRANT ALL PRIVILEGES ON DATABASE reopt TO reopt;
```
Working with PostgreSQL can be tricky.  Here are a few good resources:
[link1](https://www.codementor.io/engineerapart/getting-started-with-postgresql-on-mac-osx-are8jcopb)
[link2](https://www.a2hosting.com/kb/developer-corner/postgresql/managing-postgresql-databases-and-users-from-the-command-line)

Once your PostgreSQL server is up and running, in your development environment:
```
python manage.py migrate
```

#### FYI
If you totally bugger up your local PostgreSQL database during development, log into psql and:
```
drop database reopt;
create database reopt;
```
Then in your development environment:
```
python manage.py migrate
```

## Step 6: Setting up Xpress
In order to run the API, you'll need to get a license key for Xpress on your virtual environment. To do this, please follow the instructions here: https://github.nrel.gov/dcutler/fico-xpress. If you don't have access to this page, email Dylan Cutler.

## Step 7: Test the API
Run all test with `python manage.py test`.
When tests are run, a new PostgreSQL database will be created, with `test_` prepended to the `NAME` defined in dev_settings.py.

#### FYI
A good option to know is `--failfast`, as in:
```
python manage.py test --failfast
```
which will stop the test suite as soon as one test fails or errors.

You can also test individual apps:
```
python manage.py test reo.tests
```
Or an individual test function:
```
python manage.py test reo.tests.test_wind
```




## Step 8: Starting API server and Celery workers
First, one must define some local environment variables. Open a new file called `.env` in the root directory of the API and include:
```
DEPLOY_CURRENT_PATH="/full/path/to/MY-API-FOLDER"
APP_ENV="local"
APP_QUEUE_NAME="localhost"
TEST="true"
```

With the two database servers up and running (Redis and PostgreSQL), you're ready to start the Django server and Celery workers:
```
honcho start
```

#### FYI
[Honcho](https://honcho.readthedocs.io/en/latest/index.html) is a Python port of the Ruby based Foreman.

The actual API servers (develop, staging, and production) use Chef to set up each node (including daemonizing Redis).
The Gunicorn instance (which is a [Python WSGI HTTP server for Unix](http://gunicorn.org/)) and the Celery workers
are all started via the `Procfile` by [Foreman](http://ddollar.github.io/foreman/).

The first line of the `Procfile`:
```
web: $DEPLOY_CURRENT_PATH/bin/server
```
requires that `DEPLOY_CURRENT_PATH` point to your root directory for the API (MY-API-FOLDER). It will run the bash file located in
MY-API-FOLDER/bin. You can expect these lines to fail (gracefully):
```
. /opt/xpressmp/bin/xpvars.sh
export XPRESS=/opt/xpressmp/bin
```
which define the Mosel environment variables on the linux servers.

Finally, `exec ./env/bin/gunicorn --config ./config/gunicorn.conf.py reopt_api.wsgi` will start the Gunicorn server.
With `TEST="true"` the server will listen at `127.0.0.1:8000`, which is defined in MY-API-FOLDER/config/gunicorn.conf.py.
The gunicorn.conf.py file also uses `APP_ENV="local"` to select the Django configuration file.


Note that you can also start the API and Celery servers individually with `python manage.py runserver`
and `celery -A reopt_api worker --loglevel=info`.



## Step 9: Using the API
There are many different ways to use the API. At high level:

1. Inputs are POST'ed at `http://127.0.0.1:8000/v1/job/`
2. The response will include your run_uuid, eg:
```
{
    "run_uuid": "3a76612c-e538-484a-a1f3-3793bb4b869d"
}
```
3. Results are obtained from `http://127.0.0.1:8000/v1/job/MY-RUN-UUID/results/

Example methods for POSTing inputs include:
1. `curl`
2. [Postman](https://www.getpostman.com/)
3. https://github.nrel.gov/REopt/API_scripts


# Debugging

### Interactive debugging
Unless you manually set `CELERY_TASK_ALWAYS_EAGER = True` in the django settings file (eg. dev_settings.py) then you can not directly use the Python debugger (i.e. `pdb`).
(When running tests, the celery tasks are run in "eager" mode, which means that they are run synchronously and thus the reopt endpoint will not respond with the run_uuid until the model has solved.)

For interactive debugging with celery tasks, you need to use the remote debugger. Place the following where you want to start the interactive Python debugger:
```
from celery.contrib import rdb; rdb.set_trace()
```
In the celery terminal you will see something like:
```
Remote Debugger:6902: Ready to connect: telnet 127.0.0.1 6902
```
Open a new terminal and copy and paste the `telnet 127.0.0.1 6902` line into the new terminal, which will log you into the interactive Python debugger session.
Once you continue or exit the pdb session, the celery worker will continue.


### Exeptions and traceback information
Unfortunately, having `DEBUG=True` in the django settings leads to a memory leak (seems to be related to Celery task chord.unlock getting stuck in infinite loop).
However, if you want to receive debugging information from the API, you can temporarily set `DEBUG=True`. **DO NOT PUSH ANY COMMITS WITH DEBUG=True!**

Another, safer way to view exception information is to log into your PostgreSQL server and query the `reo_errormodel` table. For example:
```
\c reopt;
select * from reo_errormodel where run_uuid = '<my_run_uuid>';
select * from reo_errormodel order by id desc limit 2;
\q
```
**Note that PostgreSQL uses single quotes around strings, such as the run_uuid field.**


## Monitoring and Management

Celery offers a web-based task monitor (under development). To start the "flower" (pronounced like water flow) server:
`celery -A reopt_api flower --port=5555`
which will allow you to view tasks in your brower at [http://localhost:5555](http://localhost:5555).
