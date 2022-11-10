Feature: Bulk PR creation
  As an organisation maintainer
  I need to create a PR on many repos at once
  So that I update-fix log4shell quickly

Scenario: Dependabot-like dependency updates
  Given a list of repos to maintain
  When bumping "libxml" from "1.2.0" to "1.3.0"
  Then each repo using "1.2.0" has a PR updating "libxml" to "1.3.0"
  But no PR exist on repos already at "1.3.0"

Scenario: Downstream adoption of template update
  Given a project template
  And a list of old-template-using repos
  When the template gets updated
  And a template update migration is created
  Then repos using old template get a PR updating usage
