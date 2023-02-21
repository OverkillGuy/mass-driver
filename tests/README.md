# Mass-driver integration tests

Note that due to the packaging structure, tests in this folder aren't captured
into the package that's built for users, hence cannot be run by downstream users
to validate that mass-driver does the job.

This is why the tests you'll see here are very high level and for now, quite
empty, as the project is using plugins, and showing how plugins should get
tested is of major importance, hence moving a lot of the relevant tests under
`src/mass_driver/tests/` instead.
