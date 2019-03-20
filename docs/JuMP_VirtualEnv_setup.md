## REopt open-source JuMP set-up 

### Step 0: 
- `git clone https://github.com/nrel/reopt_api.git`  
- `cd reopt_api`  
- `git checkout jump_dev`  

### Step 1: Miniconda Installation
- Download the Python 2.7 version (64-bit(x86)) installer from

     `https://docs.conda.io/en/latest/miniconda.html`

- In bash terminal, type the command:

     `bash Miniconda-latest-Linux-x86_64.sh`

- Follow the prompts on the installer screens
- To make the changes take effect, close and then re-open your Terminal window.


### Step 2: Creating virtual environment for Julia in  **Python**

- In a new bash terminal, run the following command to create a new virtual environment named *reo_jump*:  

    `conda create --name reo_jump python=2.7.15`
  
 - Activate the newly created python virtual environment using the command:  

    `conda activate reo_jump`

- Install the required packages for REopt_OpenSource project using the following command:  
    `pip install -r /local/workspace/reopt_api/requirements.txt`

- Install python's julia package for calling julia functions in python  

    `conda install -c conda-forge julia`  
    `python2 -m pip install julia`

- Adding the python virtualenv (_reo_jump_)  to the ipython notebook, run the following set of commands:  
    `pip install ipykernel`  
    `ipython kernel install --user --name=reo_jump`
 
#### Step 2.1 Installing Julia programming language
- Open a new terminal
- Navigate to installation location
- Linux users: Either download from <a href="https://julialang.org/downloads" target="_blank">here</a> or:  

     `wget https://julialang-s3.julialang.org/bin/linux/x64/1.0/julia-1.0.3-linux-x86_64.tar.gz`

    `tar xvzf julia-1.0.3-linux-x86_64.tar.gz`
- Mac users: Go to <a href="https://julialang.org/downloads" target="_blank">here</a> 
    - download .dmg 
    - manually run
    - click and drag icon to Applications
    
- Add `julia-1.0.3/bin/julia` to the `PATH`: `export PATH=~/julia-1.0.3/bin:$PATH`
   
- Julia configuration setup   
     `cd $HOME/.julia/`
     `mkdir config`

- Create a file named startup.jl in the newly created folder (you will need a text editior like gedit to create a file)
- Add the following to your `$HOME/.julia/config/startup.jl`, obtaining the path to python and juptyer by: `which python`

    `ENV["PYTHON"] = "/home/reopt/anaconda3/envs/reo_jump/bin/python"`  
    `ENV["JUPYTER"] = "/home/reopt/anaconda3/envs/reo_jump/bin/jupyter"`

- In Julia >= 0.7, above two paths to `libpython` have to match exactly in order for PyJulia to work. Open the terminal window and type `julia` to launch the REPL.  
- For configuring PyCall.jl to use project specific Python interpreter (which is `/home/reopt/anaconda3/envs/reo_jump/bin/python`), run the following commands in the Julia REPL opened in previous step:  

    `ENV["PYTHON"] = "/home/reopt/anaconda3/envs/reo_jump/bin/python"`  
    `using Pkg`  
    `Pkg.add("PyCall")`  
    `Pkg.build("PyCall")`    

### Step 3: IJulia and JuMP Installation

- Open a terminal and launch julia with the command: `julia`
- Install IJulia with the following commands:  
     `using Pkg`  
     `Pkg.add("IJulia")`  
     `Pkg.add("JuMP")`  
- Further help on IJulia notebook:  [here](https://github.com/JuliaLang/IJulia.jl)

### Step 4 Installing Solvers
- Execute the following set of commands:  
     `Pkg.add("Cbc")`  
     `Pkg.add("GLPK")`  
     `Pkg.add("MathOptInterface")`   

#### Step 4.1 Additional dependencies to install (outside of Julia environment)

- for linux users:
    `sudo apt-get update`  
    `sudo apt-get install gfortran`
 
- for mac users:
    `conda install -c anaconda gfortran_osx-64`



### Step 5: Installing **Julia Plugin** for PyCharm
- Open pycharm
- Go to `File -> Settings -> Plugins -> Browse Repositories`
- Search `Julia`
- install the Julia plugin and restart Pycharm

  #### Step 5.1: Setting up julia project environment inside reopt_api folder
- Open a new terminal
- Navigate to `reopt_api\reo_jump\env`, type: `julia`
- You will see *_(v1.1)>_* in the repl:
- ![snapshot of Julia REPL](julia_REPL.png)  
- type the following commands:

     *_(v1.1)_*>  `activate .`  
     
- You will see *_(v1.1)>_* changing to *_(env)>_* in the repl, then type:

     *_(env)_*>  `status`  
     *_(env)_*>  `add Cbc`  
     *_(env)_*>  `add GLPK`  
     *_(env)_*>  `add MathOptInterface`  
     *_(env)_*>   `add Interface`  


  #### Step 5.2: Setting up project interpreter for running Julia file inside PyCharm
- go to `File->Settings->Languages & Frameworks->Julia`
- ![snapshot of Julia Interpreter](Pycharm_Julia_Interpreter_setting.png)  
- Enter the paths in the  _Julia executable_ and _Julia base path_ as shown the above snapshot
- Hit _Apply_ and _OK_
- Click on the drop-down toward the right (up) of the PyCharm main screen (shown in the following  image):  
- ![getting to _Edit Configuration_ window](edit_config_1.png)  
- Click on _Edit Configurations and hit on + button.
- Pick _Julia_ in the options which show up when you click + button
- fill out the details as given in the following snapshot:  
- ![Pycharm Interpreter for Julia](edit_config_2.png)  
- __ed_example.jl__ file is an example julia script located inside reo_jump folder
- __julia-optimization__ was created in previous steps
- Hit _Apply_ and _OK_  

  #### Step 5.3: Setting up python project interpreter in PyCharm
  - go to `File->Settings->Project->Project Interpreter`
  - Add existing project interpreter, point to `/path/to/miniconda/bin/python`
  - Hit _Apply_ and _OK_

