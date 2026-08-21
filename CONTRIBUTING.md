Thanks for using Pandana!

This is an open source project that's part of the Urban Data Science Toolkit. Development and maintenance is a collaboration between UrbanSim Inc, U.C. Berkeley's Urban Analytics Lab, and other contributors.

You can contact Sam Maurer, the lead maintainer, at `maurer@urbansim.com`.


## If you have a problem:

- Take a look at the [open issues](https://github.com/UDST/pandana/issues) and [closed issues](https://github.com/UDST/pandana/issues?q=is%3Aissue+is%3Aclosed) to see if there's already a related discussion

- Open a new issue describing the problem -- if possible, include any error messages, a full reproducible example of the code that generated the error, the operating system and version of python you're using, and versions of any libraries that may be relevant


## Feature proposals:

- Take a look at the [open issues](https://github.com/UDST/pandana/issues) and [closed issues](https://github.com/UDST/pandana/issues?q=is%3Aissue+is%3Aclosed) to see if there's already a related discussion

- Post your proposal as a new issue, so we can discuss it (some proposals may not be a good fit for the project)


## Contributing code:

- Create a new branch of `UDST/pandana`, or fork the repository to your own account

- Make your changes, following the existing styles for code and inline documentation

- Add [tests](https://github.com/UDST/pandana/tree/main/tests) if possible!

- Open a pull request to the `UDST/pandana` main branch, including a writeup of your changes -- take a look at some of the closed PR's for examples. (Before v0.8, development happened on a `dev` branch; as of the v0.8 release, `main` is the integration branch and `dev` is retired.)

- Current maintainers will review the code, suggest changes, and hopefully merge it!


## Updating the documentation: 

- See instructions in `docs/README.md`


## Preparing a release:

- Make a new branch for release prep

- Update the version number and changelog
  - `CHANGELOG.md`
  - `setup.py`
  - `pandana/__init__.py`
  - `docs/source/index.rst`
  - `docs/source/conf.py`
  
- Make sure all the tests are passing, and check if updates are needed to `README.md` or to the documentation

- Open a pull request to the main branch to finalize it

- After merging, tag the release on GitHub and follow the distribution procedures below

- For anything more than a trivial release, do a dry run first with a release candidate: set the version to e.g. `0.8rc1`, tag it `v0.8rc1`, mark the GitHub release as a pre-release, and publish it to PyPI the same way as a final release. Pip ignores pre-releases unless asked for them (`pip install --pre pandana==0.8rc1`), and the Conda Forge bots ignore them too, so this is a safe way to test the whole process and let others try the binaries. There's no need to delete the release candidate from PyPI afterward; if necessary, it can be "yanked" from the project's management page. Then repeat with the final version number.


## Distributing a release on PyPI (for pip installation):

- Register an account at https://pypi.org with two-factor authentication enabled, ask one of the current maintainers to add you to the project, and `pip install twine`

- Create an API token at https://pypi.org/manage/account/token/ scoped to the Pandana project. PyPI uploads no longer accept a username and password.

- The binary installers ("wheels") and the source distribution are built by the `Build wheels` GitHub Actions workflow, because each wheel needs to be compiled in its own target environment. The workflow runs automatically when a PR is opened, to confirm nothing is broken, and again when a release is published on GitHub. Each wheel is installed and tested as part of the build.

- Publish the release on GitHub (tag plus release notes), wait for the `Build wheels` workflow run for the tag to finish, then download its artifacts from the Actions status page: one `wheels-*` archive per platform plus `sdist`. Unzip them into an empty `dist` directory.

- Check and upload the files:

      twine check dist/*
      twine upload dist/*

  When prompted, enter `__token__` as the username and the API token as the password.

- Check https://pypi.org/project/pandana/ for the new version, and try `pip install pandana` in a fresh environment. The `Installation` GitHub Actions workflow can also be run manually to test installation across platforms and Python versions.

- The plan is to eventually publish to PyPI directly from GitHub Actions using Trusted Publishing, once the repository and organization settings support it. The manual upload steps above will then become the fallback.


## Distributing a release on Conda Forge (for conda installation):

- The [conda-forge/pandana-feedstock](https://github.com/conda-forge/pandana-feedstock) repository controls the Conda Forge release, including which GitHub users have maintainer status for the repo

- Conda Forge bots usually detect new releases on PyPI and set in motion the appropriate feedstock updates, which a current maintainer will need to approve and merge

- Maintainers can add on additional changes before merging the PR, for example to update the requirements or edit the list of maintainers

- You can also fork the feedstock and open a PR manually. It seems like this must be done from a personal account (not a group account like UDST) so that the bots can be granted permission for automated cleanup

- Check https://anaconda.org/conda-forge/pandana for the new version (may take a few minutes for it to appear)
