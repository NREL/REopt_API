# Contributing to REopt Lite
Thank you for contributing! 

Below are guidelines for making contributions to REopt Lite.


### I don't want to read this whole thing I just have a question!!!
Please do not create an "issue" if you have a question. We have a discussion board **here**(TODO add URL or change to stackoverflow with "reopt" tag?). You might find answers to general questions on [our web site](https://reopt.nrel.gov/). Finally, if you want to reach out to us ... 
TODO should we include the following: You can also contact us at reopt@nrel.gov

## How Can I Contribute?

#### Reporting Bugs
Creating an issue in the github.com repository is the preferred method for reporting bugs. 
Please see our issue template(TODO create issue template) for more.

#### Suggesting Enhancements

#### Testing
The REopt API has a built-in test suite. 
Much of the code was developed in parallel with tests, using the principles behind [test driven development](https://en.wikipedia.org/wiki/Test-driven_development)
Tests can be run using [Django's `manage.py`](https://docs.djangoproject.com/en/2.2/topics/testing/overview/) in the top directory. 
For example, to run all tests:
```
python manage.py test
```
One can also run a specific test suite, like:
```
python manage.py test reo.tests.test_reopt_url
```
Or even an individual test within a suite:
```
python manage.py test reo.tests.test_reopt_url.EntryResourceTest.test_complex_incentives
```

#### Pull Requests

##### I have created a bug fix

##### I have added a feature that other users will benefit from


## Styleguides

#### Python code
- PEP8 and PyCharm

#### Git Commit Messages
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line
