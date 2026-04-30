# Changelog

## [Unreleased]

### Dependencies
- deps: yarn patch (serverless 4.29.0→4.29.3 direct; @hapi/content 6.0.0→6.0.1, koa 2.16.2→2.16.3, lodash 4.17.21→4.17.23 transitive); minor (@smithy/config-resolver 4.2.2→4.4.0, brace-expansion 2.0.2→2.0.3, minimatch 9.0.5→9.0.7 transitive; axios/follow-redirects updated via serverless bump); major: fast-xml-parser 3.21.1→4.1.2, glob 7.2.3→10.5.0, uuid 9.0.1→14.0.0 (all transitive)
- deps: patch skipped (safety-schemas 0.0.16→0.0.18 blocked by 1-week age cutoff); graphql-server pinned (user declined); pip vuln GHSA-58qw-9mgm-455v (no fix available)

## [0.10.0] - 2025-10-16

### Changed
 - migrate to serverless 4
 - set serverless to python 3.12
 - migrate pyproject.toml to PEP508
 - ensureCI/CD workflows use minimum install footprints
 - add package.json to bump2version 

### Added
 - docs will publish in release workflow
 - tox audit step 

### Remove
 - unused nzshm-model schema (superceded by nshm-model-graphql-api)

## [0.9.3] - 2025-09-25
### Added
 - `safety` vulnerablity scanner (use requires reg/login)

### Changed
 - python 3.10 support only
 - update advisories (from dependabot/safety) `cryptography` and `urllib3`

## [0.9.2] - 2025-09-24
### Changed
 - poetry package update
 - docs for use of audit tools

## [0.9.1] - 2025-09-23
### Changed
 - python security updates
 - node serverless package updates
 - move to `graphql-server` project for GraphQLView

## [0.9.0] - 2025-09-23
### Added
 - `about` resolver
 - `version` resolver

### Removed
 - hazard features migrated to nshm-hazard-graphql-api

### Changed
 - move to yarn2 for node package management
 - updated to shared workflows

## [0.8.1] - 2023-08-15
### Changed
 - use toshi-hazard-store>=0.7.3 for faster hazard queries
 - python versions, now support only 3.9, 3.10

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
