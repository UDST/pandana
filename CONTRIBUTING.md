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

- Add [tests](https://github.com/UDST/pandana/tree/master/pandana/tests) if possible!

- Open a pull request to the `UDST/pandana` dev branch, including a writeup of your changes -- take a look at some of the closed PR's for examples

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

- Open a pull request to the master branch to finalize it

- After merging, tag the release on GitHub and follow the distribution procedures below


## Distributing a release on PyPI (for pip installation):

- Register an account at https://pypi.org, ask one of the current maintainers to add you to the project, and `pip install twine`

- Check out the copy of the code you'd like to release

- Run `python setup.py sdist`

- This should create a `dist` directory containing a gzip package file -- delete any old ones before the next step

- Run `twine upload dist/*` -- this will prompt you for your pypi.org credentials

- Check https://pypi.org/project/pandana/ for the new version

The binary package installers or "wheels" are built using a GitHub Actions workflow, because each one needs to be compiled in its own target environment. This should run automatically when a PR is opened, to confirm nothing is broken, and again when a release is tagged in GitHub. You can download the resulting wheel files from the Action status page and then upload them to PyPI using the same command as above.

How to create wheels for ARM Macs: As of 7/2023, GitHub Actions doesn't provide this environment yet. You'll need an ARM Mac to create the wheels. One at a time, set up a Conda environment with Python 3.8, 3.9, etc. Include cython, numpy, clang, llvm-openmp, and pytables. These need to be ARM-native Conda environments -- check that you're getting `osx-arm64` versions of libraries. Run `python setup.py bdist_wheel` to generate a wheel file. Once one is built for each Python version, upload them to PyPI using the command above.


## Distributing a release on Conda Forge (for conda installation):

- The [conda-forge/pandana-feedstock](https://github.com/conda-forge/pandana-feedstock) repository controls the Conda Forge release, including which GitHub users have maintainer status for the repo

- Conda Forge bots usually detect new releases on PyPI and set in motion the appropriate feedstock updates, which a current maintainer will need to approve and merge

- Maintainers can add on additional changes before merging the PR, for example to update the requirements or edit the list of maintainers

- You can also fork the feedstock and open a PR manually. It seems like this must be done from a personal account (not a group account like UDST) so that the bots can be granted permission for automated cleanup

- Check https://anaconda.org/conda-forge/pandana for the new version (may take a few minutes for it to appear)
