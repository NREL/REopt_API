<h1>reopt_api</h1>
=========

<h3>Django API for REopt tool</h3>

Under development, will provide api to REopt model for performing solar plus storage optimization  
Note, the project has been developed in Windows but should be easy to administrate in Linux/OSX if preferred  
Instructions will assume a Windows based install where you have administrator privleges or access to the C:/ via command prompt  


<h4>If setting up from scratch:</h4>

1. You will need Python 2.7 installed.  You can get it here: `https://www.python.org/download/releases/2.7/`  
   Python will generally install in `C:\Python27\`, which will get added to your `PATH` environmental variable.  
   If python has successfully been installed and added to your path, you should be able to open a command prompt and type: `python`  

   If you see: 
   `'python' is not recognized as an internal or external command`  
   Then:
   `set PATH=%PATH%;C:\Python27\`  

2. Python packages are installed using `pip`.  This is a package which should be included with Python, within `C:\Python27\Scripts\`  

   `set PATH=%PATH%;C:\Python27\Scripts\`  

3. The Django project will be installed within a virtual environment. Install the package with pip
   
   `pip install virtualenvwrapper`

4. Navigate to where you want to place the virtual environment.  Create:

   `virtualenv env`

5. Activate the virtual environment, which you should do whenever you work on this project:

   `env\Scripts\activate.bat`

6. Install requirements
   ```
   pip install requests
   pip install django==1.8
   pip install django-tastypie==0.13.3
   pip install numpy==1.11.0
   pip install pandas==0.18.1  (may need Visual C++ compiler, install from http://aka.ms/vcpython27)
   install pywin32==220 from: https://sourceforge.net/projects/pywin32/files/pywin32/Build%20220/pywin32-220.win-amd64-py2.7.exe/download
   ```
7. Check out the git repository into the virtual environment. 
   Note the 'git' command must be done from a git bash prompt rather than windows command prompt.  
   Alternatively, you can download and extract the files.  
   This should result in a structure `env/src/reopt_api`  
      
   `mkdir src`  
   `cd src`  
   `git clone https://github.nrel.gov/ndiorio/reopt_api`  
   
8. Run server (in local mode, which requires command prompt to remain open)
   
   `cd reopt_api`  
   `python manage.py runserver 0.0.0.0:80`  
   
9. Navigate to `10.40.10.40/reopt`, should see landing page  
   To use API, navigate to: `10.40.10.40/api/v1/reopt/?format=json`  
   This will activate a call to the Xpress backend.  Additional parameters will be required to fully query the API.  For example:  

   `10.40.10.40/api/v1/reopt/?format=json&latitude=40&longitude=-115&load_size=10000`  
   
   Returns:
   ```
   {"meta": {"limit": 20, "next": null, "offset": 0, "previous": null, "total_count": 1}, "objects": [{"analysis_period": null, "batt_cost_kw": null, "batt_cost_kwh": null, "id": 260394, "latitude": 40.0, "lcc": 2.85481, "load_profile": null, "load_size": 1000000.0, "longitude": -115.0, "offtaker_discount_rate": null, "owner_discount_rate": null, "pv_cost": null, "pv_om": null, "resource_uri": "/api/v1/reopt/260394/"}]}
   ```

<h4>If running locally from the REopt default server `iac-129986`:</h4>
* Navigate to `C:\Nick\Projects\api\env\`   
```
  Scripts\activate.bat
  cd src\reopt_api
  python manage.py runserver
```
<h4> To deploy the API using CherryPy and setuptools <h4>
   
The reopt_api is staged on iac-129986 as a standalone service (CherryPyService), which automatically starts when the server boots. This is a different process than using `runserver`, which starts the API on a process associated with the command prompt and uses the local python code repository rather than the deployed python package. The `runserver` method is useful for development and debugging, but is not a solution for serving a finished product. 

The process of deploying the API on the server is somewhat complicated, but results in a distributable python package installed in the standard Python path (`C:\Python27\Lib\site-packages\`), and the package serving as the backend to any API calls.

The process (modified from: https://baxeico.wordpress.com/2013/10/13/django-on-windows/).  Note, all installations and references to Python will refer to the system-wide install as opposed to the virtual environment method described previously.  The service runs system-wide, not through the virtualenv. Also of note is that the files referenced in the following instructions are already present in the git repo.  These instructions are for reference.

1. Install CherryPy
   
   `pip install CherryPy==6.0.1`
2. Verify CherryPy install
   `cd C:\Python27\Lib\site-packages\cherrypy\tutorial`
   `python tut01_helloworld.py`
   - navigate to http://127.0.0.1:8080, should see "Hello World"
3. Install most recent pywin32 package from https://sourceforge.net/projects/pywin32/files/pywin32 using the appropriate architecture and Python version.
4. Make Django project an installable python package
   - Download ez_setup.py from https://pypi.python.org/pypi/setuptools
   - Create a setup.py file using the template from https://baxeico.wordpress.com/2013/10/13/django-on-windows
      - Update the setup parameters to reflect the project
      - Update the script to include the 'Xpress' folder in data_files
      - Add the function gen_dat_files, which enumerates all of the files in 'Xpress' to be included
      - Modify the data install directory to match the source install directory
   - Create the package:
      `python setup.py install`
   - Package will be installed to:
      `C:\Python27\Lib\site-packages\reopt_api-1.0-py2.7.egg`
5. Get Django package to run in CherryPy as Windows service
   - Download the files linked to in the wordpress tutorial.  
   - Modify `cherrypy_django_service.py` to serve host 0.0.0.0 on port 80.
   - Modify the same file to use 'reopt_api.settings' for the settings module
6. Start the service
   `python cherrypy_django_service.py install`
   `python cherrypy_django_service.py start`
7. Make the service automatic
   - Open task manager, navigate to "Services", and then click the "Services..." button in the bottom right.
   - Right click "CherryPy Service" and click "Properties"
   - Under "Startup Type", change it to "Automatic"
8. Test hitting the site
   `10.40.10.40/reopt`
   - Should see "Future home of REopt API"
9. Notes:
   - The installable package runs out of `C:\Python27\Lib\site-packages\win32\` due to the pywin32 process.
   - There are logs for the CherryPy Service and for the API available in:
     `C:\Python27\Lib\site-packages\reopt_api-1.0-py2.7.egg\reopt_api`
   - The DAT paths in the Xpress file have to be relative to where the installable package runs from
