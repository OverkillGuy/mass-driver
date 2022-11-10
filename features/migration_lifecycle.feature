Feature: Lifecycle management of a migration
  As an organisation maintainer
  I need to monitor the adoption of a planned migration from start to finish
  So that I can chase the last few non-compliance events

Scenario: Migration progress dashboard
  Given a patchnote to apply, updating "log4j" to new version
  And the PRs were already sent out
  When I open the migration's view
  Then all the organisation's repos using old "log4j" are listed
  And all the repos which adopted new version are crossed out
