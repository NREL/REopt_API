# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.1.0] - 2020-01-21
### Added
- First release of the REopt API
- Setting version number to 0.1.0 (and not 1.0.0) to reflect the fact that this version of the REopt API has not been used in a production environment
  - The primary difference between the production version of the REopt API and the open-source version is that the production version uses a Mosel model (FICO Xpress modeling language) and the open-source version using a Julia JuMP model (to allow compatibility with more solvers)
