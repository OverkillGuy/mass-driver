Feature: Discovery of repositories within Organisation
  As an organisation maintainer
  I need to discover all repos for which a patch may apply
  So that I migrate all users of an obsoleted pattern

Scenario: Log4shell discovery
  Given a patchnote to apply, updating "log4j" to new version
  When I request discovery of packages
  Then all the organisation's repos using old "log4j" are listed
  But no repo list was written ahead of time
