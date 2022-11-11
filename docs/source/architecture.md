---
myst:
  substitutions:
    Repository: "[Repository](concept-repository)"
    Repositories: "[Repositories](concept-repository)"
    Migration: "[Migration](concept-migration)"
    Forge: "[Forge](concept-forge)"
    Driver: "[Patch Driver](concept-patch-driver)"
    Patch: "[Patch](concept-patch)"
---

# Architecture of Mass Driver

An overview of the useful concepts used in this project.

## Repository
(concept-repository)=

A single git repository, on a {{Forge}}

## Forge
(concept-forge)=

A website integrating Git with a UI for change request etc.

Example Forge: Github.


## Patch Driver
(concept-patch-driver)=

A Patch Driver is a class that implements PatchDriver, describing a set way to
create Patches against a {{Repository}}.

## Patch
(concept-patch)=

A Patch is a diff-able change, the outcome of a {{Driver}}, usually in the
context of a single {{Repository }}.

When discussing a set of Patches created by the same {{ Driver }}, we refer
to the collective as a {{Migration}}

## Migration
(concept-migration)=

A {{Migration}} is a {{Patch}} being applied to a group of {{Repositories}}.

Example Migration: The act of bumping a vulnerable library across all of the
org's repos.

In particular, Migrations include the concept of progression over time, where
change requested on each repo get adopted by developers, and it becomes
valuable to review the {{Patch}}'s adoption, until all {{Repositories}} affected
are patched.
