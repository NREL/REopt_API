# Contributing to REopt Lite
Thank you for contributing! 

Below are guidelines for making contributions to REopt Lite.


### I don't want to read this whole thing I just have a question!!!
Please do not create an "issue" if you have a question. We have a discussion board **here** (TODO add URL to discourse). You might find answers to general questions on [our web site](https://reopt.nrel.gov/), and the discourse discussion board is pretty comprehensive as well. If you don't find your question on the discussion board, please open a new question there. 

## How Can I Contribute?

#### Reporting Bugs
Creating an issue in the github.com repository is the preferred method for reporting bugs. 


#### Suggesting Enhancements
First, please check the [REopt Lite Development Plan](https://reopt.nrel.gov/development-plans.html) in case your idea is already in the works.

Please refer to the instructions given in the issue template provided in the [issues](https://github.com/NREL/reopt_api/issues) tab on the repository for suggesting enhancements. 

#### Pull Requests

##### I have created a bug fix

- First fork the repository and create a new branch on your fork
- Once the bug is fixed, run the full test suite (instructions for running the test suite are available [here](https://github.com/NREL/reopt_api/wiki/Testing-the-REopt-API))
- If it passes, send a PR to the original repository. If you haven't signed the [Code License Agreement](https://github.com/NREL/REopt_Lite_API/blob/master/cla.md) already, the CLA Assistant will comment on your PR and request you to sign the CLA. You can simply comment "I have read the CLA Document and I hereby sign the CLA" to sign the [CLA](https://github.com/NREL/REopt_Lite_API/blob/master/cla.md). 
- If tests aren't passing, then first look the specific test[s] that is/are failing. Then think through - "do I expect the test to fail after introducing the bug-fix I am proposing?"
    - If yes, then please provide a clear description of the identified bug, how you fixed it, and explanation for why the fix is making an existing test fail
    - If no, then revisit the changes you introduced to identify where the problem is

##### I have added a feature that other users will benefit from

- First fork the repository and create a new branch on your fork
- Then develop the feature on that branch, detailed tutorial for REopt-api feature development is [here](https://github.com/NREL/reopt_api/wiki/Developing-the-API)
- Note that we highly recommend test-driven development (the tutorial cover that in detail)
- After the feature is complete, run the full test suite
- If it passes, send a PR to the original repository. If you haven't signed the [Code License Agreement](https://github.com/NREL/REopt_Lite_API/blob/master/cla.md) already, the CLA Assistant will comment on your PR and request you to sign the CLA. You can simply comment "I have read the CLA Document and I hereby sign the CLA" to sign the [CLA](https://github.com/NREL/REopt_Lite_API/blob/master/cla.md). 
- If tests aren't passing, then first look the specific test which is failing. Then think through - Do I expect this test to fail after having added the new feature? 
    - If yes, then please provide a clear explanation for why the existing test[s] should fail after the introduction of the new feature
    - If no, then revisit the new feature you have developed to troubleshoot the problem with the failing test[s]


## Styleguides

#### Python code
- PEP8

## Recommended IDE
- PyCharm

#### Git Commit Messages
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line
