REopt Lite API
=========
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

Lastly, get *keys.py* from another API developer (these are access keys that we do not version control).

## Step 2: Python 2.7

Mac only: If you have not already, you need to install [Xcode](https://developer.apple.com/xcode/), which can be found in the app store or installed via terminal with `xcode-select --install`

For **both PC and Mac**, in a mac terminal or windows command prompt you can check if/what version of python you have installed with
`python --version`
If the response is:
`Python 2.7.x`
you can skip to Step 2

#### PC
You can get Python 2.7 [here](https://www.python.org/download/releases/2.7/).
Python will generally install in C:\Python27\, which will get added to your `PATH` environmental variable.

If python has successfully been installed and added to your path, you should be able to open a command prompt and type: `python`.
If you see:

`'python' is not recognized as an internal or external command`

Then:

`set PATH=%PATH%;C:\Python27\`

Python packages are installed using `pip`.  This is a package which should be included with Python, within C:\Python27\Scripts\

`set PATH=%PATH%;C:\Python27\Scripts\`

#### Mac
Mac computers come with python installed in two locations: `/System/Library/Frameworks/Python.framework` and `/usr/bin/python`. These should not be modified since Apple and third party apps may depend on them.  If you wish to install another version of python [Homebrew](http://docs.python-guide.org/en/latest/starting/install/osx/) is a popular option.



## Step 3: Virtual Environment
Fortunately, there's an [app](https://virtualenv.pypa.io/en/stable/userguide/) for that.

#### Both PC and Mac
1. `pip install virtualenv`
2. `cd` to **MY-API-FOLDER** (if you are not there already) and

   `virtualenv env`

   NOTE: Virtual environments do not apply to only the directory in which they are installed. You can install the virtual environment into any directory with any name. However, we already have the "env" directory in the .gitignore file so that the virtual environment is not version controlled if it is installed in MY-API-FOLDER.

3. Activate the virtual environment, which you should do whenever you are using the API:
   - PC: `env\Scripts\activate`
   - Mac: `source env/bin/activate`

   NOTE: If you open a new terminal or command prompt the environment will need to be activated for that session. Also, you can activate the environment from any directory by providing the full path to the `activate` script.

4. DO NOT DO THIS NOW, but for future reference, to deactivate the virtual environment simply `deactivate` from any directory.


## Step 4: Install Requirements

### For Windows
Celery 4 is not supported on windows. So you will have to:
```
git checkout windows
```
BEFORE installing the requirements. The requirements.txt file is different from all other branches on the windows branch.
Specifically, the celery version for windows is 3.1.25, and the `django-celery` package must be installed (not need on other OS's).
Note that because of the need of Celery v3 on windows, the settings files (within the windows branch) are slightly different.

### For both Mac & Windows

`pip install -r requirements.txt`



## Step 5: Run Servers Locally
All of the `commands` are done in MY-API-FOLDER.

If you wish to take advantage of the celery task manager, three separate servers must be started (in three separate command windows or terminals):

1. The REopt API: `python manage.py runserver`
2. A redis server: `redis-server`  (which acts as a message broker for the tasks)
    - if you don't have redis go [here](https://redis.io/topics/quickstart) for mac/linux or [here](https://github.com/MicrosoftArchive/redis/releases) for Windows
    -  **Windows**: you have to `redis-cli shutdown` before starting `redis-server`, and scripts may only be run from the Redis directory.
        - Also, make sure your user account has full write access to the Redis directory (necessary for back-ups that Redis performs regularly)
3. A celery server: `celery -A reopt_api worker --loglevel=info`

For each step above, the last line that you should see after executing are:
1. `Starting development server at http://127.0.0.1:8000/`
2. ...`Ready to accept connections`
3. ...`celery@<YOUR-MACHINE> ready.`

An alternative API usage method, which excludes running redis and celery servers, is described in the **Advanced** section below


## Step 6: Using the API
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


# Advanced

## Backend Database
The REopt API uses a PostgreSQL datbase to save invalid posts, scenarios, and exceptions.  Separate databases are configured for the three different web servers in MY-API-FOLDER/reopt_api/[dev_settings.py, production_settings.py, staging_settings.py]. When using the API locally, it still relies on a remote database.

When the API server is started with `python manage.py runserver` the dev_settings.py is used. Within dev_setings.py, you will see that a different, local database is used for testing (when using `python manage.py test`). Thus, **in order to run tests, a local postgres database must be set up**.

### Running tests with `python manage.py test`

In order to run all test functions, one must have a [postgres](https://www.postgresql.org/download/) server installed and running locally.  To do this requires several packages, for example in Ubuntu:

```
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgresql-client-common postgresql-client
```

Once you've downloaded and installed postgres, you will want to setup a local database. By default, when postgres is installed, it automatically creates a database user that matches your username, and has a default role called 'postgres'.  To create a local database called "reopt", with a username "reopt", and password "reopt":

```
sudo -i -u postgres
psql postgres
CREATE USER reopt WITH PASSWORD 'reopt';
ALTER USER reopt CREATEDB;
CREATE DATABASE reopt;
GRANT ALL PRIVILEGES ON DATABASE reopt TO reopt;
```

When tests are run, a new database will be created, with `test_` prepended to the `NAME` defined in dev_settings.py.

Working with postgres can be tricky.  Here are a few good resources:
[link1](https://www.codementor.io/engineerapart/getting-started-with-postgresql-on-mac-osx-are8jcopb)
[link2](https://www.a2hosting.com/kb/developer-corner/postgresql/managing-postgresql-databases-and-users-from-the-command-line)

### Removing remote database dependency
Sometimes it can be advantageous to store results locally. The database that the API uses is configured in MY-API-FOLDER/reopt_api/dev_settings.py. The easiest way to configure your own local database is to:
1. `CREATE USER reopt WITH PASSWORD 'reopt';` (if you haven't already for testing)
2. `CREATE DATABASE reopt;`
3. Remove the second `DATABASES` definition from dev_settings.py, as well as the if/else statements
4. De-dent the `DATABASES` definition that was below `if 'test' in sys.argv:`, so that it looks like:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'reopt',
        'USER': 'reopt',
        'PASSWORD': 'reopt',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```
5. `python manage.py migrate`

NOTE: You can use any values for the `DATABASES` settings that you want as long as you set up the same values in your Postgres server.  For example, you could create a database with the name of `MY-PROJECT` and use your own log-in information.

## Removing redis/celery dependency
When running tests, the celery tasks are run in "eager" mode, which means that they are run synchronously and thus the reopt endpoint will not responde with the run_uuid until the model has solved.  This setting is achieved with:
```
if 'test' in sys.argv:
    CELERY_TASK_ALWAYS_EAGER = True
```
within dev_settings.py.

To run scenarios without having to start the redis and celery servers, simply remove the `if` statement and de-dent `CELERY_TASK_ALWAYS_EAGER = True`, such that all scenarios are run in "eager" mode.


## Monitoring and Management

Celery offers a web-based task monitor (under development). To start the "flower" (pronounced like water flow) server:
`celery -A reopt_api flower --port=5555`
which will allow you to view tasks in your brower at [http://localhost:5555](http://localhost:5555).


## Alternative Method for running API server locally (Mac/Linux only?)
The actual API servers (develop, staging, and production) use Chef to set up each node (including daemonizing Redis).
The Gunicorn instance (which is a [Python WSGI HTTP server for Unix](http://gunicorn.org/)), the Celery workers, and the Flower task monitor
are all started via the `Procfile` by [Foreman](http://ddollar.github.io/foreman/).

[Honcho](https://honcho.readthedocs.io/en/latest/index.html) is a Python port of the Ruby based Foreman and can be easily installed with
`pip install honcho`
Honcho uses a `.env` file in the project root directory to define environment variables, which should define the following:
```
DEPLOY_CURRENT_PATH="/Users/nlaws/projects/reopt/webtool/reopt_api"
APP_ENV="local"
APP_QUEUE_NAME="localhost"
TEST="true"
```
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

Once you have honcho installed, your .env variables defined, and a `redis-server` running, you can:
```
honcho start
```
which will start the API and Flower servers, as well as the Celery workers.
