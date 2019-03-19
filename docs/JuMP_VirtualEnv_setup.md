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
    
- Julia configuration setup   
     `cd $HOME/.julia/`
     `mkdir config`

- Create a file named startup.jl in the newly created folder (you will need a text editior like gedit to create a file)
- Add the following to your `$HOME/.julia/config/startup.jl`, obtaining the path to python and juptyer by: `which python`

    `ENV["PYTHON"] = "/home/reopt/anaconda3/envs/reo_jump/bin/python"`  
    `ENV["JUPYTER"] = "/home/reopt/anaconda3/envs/reo_jump/bin/jupyter"`

- In Julia >= 0.7, above two paths to `libpython` have to match exactly in order for PyJulia to work.  To configure PyCall.jl to use Python interpreter `/home/reopt/anaconda3/envs/reo_jump/bin/python`, run the following commands in the Julia interpreter (to get to Julia interpreter, open a new terminal and type `julia`) and then type the following commands:  

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

    `sudo apt-get update`  
    `sudo apt-get install gfortran`

### Step 5: Installing **Julia Plugin** for PyCharm

- Open pycharm
- Go to `File -> Settings -> Plugins -> Browse Repositories`
- Search `Julia`
- install the Julia plugin and restart Pycharm

  #### Step 5.1: Setting up julia project environment inside reopt_api folder
- Create a folder `reo_jump` within the root of the `reopt_api` directory  
- Create a new file named 'julia-optimization' in the `reo_jump` folder.  
- Add the following content to the file:  

 `` /path/to/your/julia/folder/julia-1.0.3/bin/julia --project="/local/workspace/reopt_api/reo_jump/env" $@ `` 
 
- Save and close the file  
- Create a new folder named `env` in the `reo_jump` folder
- In the `env` folder, open a new terminal, type: `julia`
- You will see *_(v1.1)>_* in the repl, type the following commands:

     *_(v1.1)_*>  `activate .`  
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

