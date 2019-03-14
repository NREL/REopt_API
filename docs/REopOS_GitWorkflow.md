## REopt open-source: Git Workflow

This is the guide for the git version control work-flow, which is being used for REopt API and will be continued with REopt OpenSource development work.

### 1: Cloning the REopt OpenSource Repository to your local machine
- Open a terminal, navigate to the folder in which you would like to clone the repo,
- Use the following command to clone:

	`git clone https://github.com/NREL/reopt_api <your desired folder name> `

**Note**: for existing reopt_api repo users: the existing api repo folder on your machine may already be named as "reopt_api" so it may be a good idea to give it a different name or place it in a different location.

### 2: Overall work-flow
- The following  image depicts the workflow model REopt API teams adheres to. There are three servers:

	1. development

	2. staging

	3. production

- There are two main branches
	1. develop (deployed to development and staging servers)
	2. master (deployed to production server)


- All the development activites are executed on _develop_ branch and when the the new features pass all the back-end tests on development server, UI user tests on staging server, then the _develop_ branch is merged with the _master_ branch.
- _master_ branch is then deployed to the production server.
- read more about this git flow model [here](https://nvie.com/posts/a-successful-git-branching-model/)


![git workflow model](git_workflow_model.png)







### 3: Individual developer working on a feature: workflow

- workflow for individual feature development tasks
	1. First, checkout develop branch and pull the latest changes from the _remote_ to local. Execute the following commands

		`git checkout develop`

		`git pull`
	
	2. Then, create and checkout a new branch locally

		`git checkout -b <branch>`
		
	3. In the new branch, write the new code. Check the status using

		`git status`
	
	4. When done, add the changes to the staging area using:

		`git add <file_name1> <file_name2> <file_name3>`
		
	5. When ready to commit, execute the following:

		`git commit -m <write a brief comment on your commit>`
		
	6. Push the newly created branch (name: my_new_branch1)  to remote origin using:

		`git push --set-upstream origin <branch>`
		
	7. Pull Request (PR): Once your feature branch is pushed to the remote repo. Go to the repo and create a PR for your feature branch

		7.1 Assign a reviewer to the PR and write a brief descripiton of the feature your have added

### 4: More than one developer collaborating on the same feature: workflow

- workflow for collaborating on feature development tasks.

- If >1 developers are simulteneously working on the same feature/section of the code, then we would want to make sure that:
	- they are working off of same _feature branch_ (one developer creates the new _feature branch_ locally, pushes is to the remote and the other developer can then pull that branch)
	- they periodically commit the changes they are making - HOWEVER before commiting/pushing new content, they must **first pull the changes to their local branch, resolve the conflicts (if any),  and then push the new updates**.


- If the intent is to pull the changes from _develop branch_ to the _feature branch_, then the following set of commands can be used:

  ​   `git checkout develop`

  ​	`git pull`

  ​	`git checkout feature branch`

  ​	`git merge develop`

- Or when on _feature branch_ (instead of being on _develop branch_), execute the following command:

  ​	`git fetch && git rebase origin/develop`
