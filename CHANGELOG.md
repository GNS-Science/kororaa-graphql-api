# Changelog

## [0.8.1] - 2023-08-15
### Changed
 - use toshi-hazard-store>=0.7.3 for faster hazard queries
 - python versions, now support only 3.9, 3.10

## [0.8.0] - 2022-
### Added
 - new schema resource nzshm_model with logic_tree structure

## [0.7.0] - 2023-05-17
### Changed
 - named locations have 0.001 precision

## [0.6.4] - 2023-05-15
### Changed
 - bumpversion to force redeploy
 - update GHA scripts
 - pin nzshm-grid-loc dependency
 - update tox
 - update serverless packages
 - use python3.9 runtime
 - remove nzshm-grid-loc dependency
 - update nzshm-common and toshi-hazard-store dependencies

## [0.6.3] - 2022-10-18
### Changed
 - omit hazard_map tiles where value is None

## [0.6.2] - 2022-10-07
### Changed
 - update toshi-hazard-store=0.5.5 for vs30 fix

## [0.6.1] - 2022-09-30
### Changed
 - updated versions for nzshm-grid-loc, nzshm-common, toshi-hazard-store
### Added
 - added filename field on science_publications
 - script to update json

## [0.6.0] - 2022-09-21

### Changed
 - scheme change making all gridded_hazard queries unary

## [0.5.1] - 2022-09-19
### Changed
 # better performance on hazard_map query

## [0.5.0] - 2022-09-16
### Changed
 * hazard_map geojson is clipped to NZ outline

## [0.4.0] - 2022-09-14
### Added
 * textual_content
 * science_reports

## [0.3.0] - 2022-08-15
### Added
 * gridded_hazard queries
 * geojson field with config args

## [0.2.0] - 2022-08-04
### Added
 * dataframe interim model
 * query_v3 suupport against HazardAggregation table
 * gridded_location query
 * arbitrary location added to hazard_curve resolver

## [0.1.0] - 2022-05-31

* First release on PyPI.
