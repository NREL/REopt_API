reopt_api
=========

Django API for REopt tool

Under development, will provide api to REopt model for performing solar plus storage optimization
Note, the project has been developed in Windows but should be easy to administrate in Linux/OSX if preferred
Instructions will assume a Windows based install where you have administrator privleges or access to the C:/ via command prompt


If setting up from scratch:
1. You will need Python 2.7 installed.  You can get it here: https://www.python.org/download/releases/2.7/
   Python will generally install in C:\Python27\, which will get added to your PATH environmental variable.
   If python has successfully been installed and added to your path, you should be able to open a command prompt and type: python
   If you see: 'python' is not recognized as an internal or external command, you need to add C:\Python27\ to your PATH

2. Python packages are installed using pip.  This is a package which should be included with Python, within C:\Python27\Scripts\
   Add C:\Python27\Scripts\ to your PATH

3. The Django project will be installed within a virtual environment. Install the package with pip
   pip install virtualenvwrapper

4. Navigate to where you want to place the virtual environment.  Create:

   virtualenv env

5. Activate the virtual environment, which you should do whenever you work on this project:

   env\Scripts\activate.bat

6. Install requirements

   pip install django==1.8
   pip install django-tastypie==0.13.3
   pip install numpy==1.11.0

7. Check out the git repository into the virtual environment. 
   Note the 'git' command must be done from a git bash prompt rather than windows command prompt.  
   Alternatively, you can download and extract the files.  
   This should result in a structure env/src/reopt_api

   mkdir src
   cd src
   git clone https://github.nrel.gov/ndiorio/reopt_api

8. Run server

   cd reopt_api
   python manage.py runserver

9. Navigate to 127.0.0.1:8000/reopt, should see landing page
   To use API, navigate to: 127.0.0.1:8000/api/v1/reopt/?format=json
   This will activate a call to the Xpress backend.  Additional parameters will be required to fully query the API.  For example:
   127.0.0.1:8000/api/v1/reopt/?format=json&latitude=40&longitude=-115&load_size=10000


If running from iac-129986:
1. Navigate to C:\Nick\Projects\api\env\
2. Scripts\activate.bat
3. cd src\reopt_api
4. python manage.py runserver
