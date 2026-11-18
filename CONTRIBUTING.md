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

- Open a pull request to the main branch, and merge it once the checks pass

- Publish the release on GitHub: create a tag on the merge commit named with a `v` prefix (e.g. `v0.8.1` for version `0.8.1`), and use the changelog text as the release notes. Publishing the release starts the `Build wheels` workflow described below

- For anything more than a trivial release, do a dry run first with a release candidate: set the version to e.g. `0.8.1rc1`, tag it `v0.8.1rc1`, and mark the GitHub release as a pre-release. Pip ignores pre-releases unless asked for them (`pip install --pre pandana==0.8.1rc1`), and the Conda Forge bots ignore them too, so this is a safe way to test the whole process and let others try the binaries. There's no need to delete the release candidate from PyPI afterward; if necessary, it can be "yanked" from the project's management page. Then repeat with the final version number

- After the release, rebuild and publish the documentation (see `docs/README.md`)


## Distributing a release on PyPI (for pip installation):

- The binary installers ("wheels") and the source distribution are built by the `Build wheels` GitHub Actions workflow (`.github/workflows/build-wheels.yml`), because each wheel needs to be compiled in its own target environment. The workflow runs on every pull request, to confirm nothing is broken, and again when a release is published on GitHub. Each wheel is installed and tested as part of the build

- When a release is published, the workflow goes on to check the files with `twine check --strict`, confirm that the version in every file matches the release tag (and that a pre-release version is marked as a pre-release on GitHub, and a final version is not), and then upload them to PyPI using [Trusted Publishing](https://docs.pypi.org/trusted-publishers/), so no PyPI credentials are stored on GitHub

- The upload step runs in the repository's `pypi` deployment environment, which requires approval from a maintainer: once the builds and checks succeed, the workflow pauses until a reviewer approves the deployment from the workflow run page. Merging to `main` never publishes anything

- Check https://pypi.org/project/pandana/ for the new version, and try `pip install pandana` in a fresh environment. The `Installation` GitHub Actions workflow can also be run manually to test installation across platforms and Python versions

- One-time setup, in case it needs to be repeated: a PyPI owner of the project registers the trusted publisher at https://pypi.org/manage/project/pandana/settings/publishing/ with owner `UDST`, repository `pandana`, workflow `build-wheels.yml`, and environment `pypi`; and a repository admin creates the `pypi` environment at https://github.com/UDST/pandana/settings/environments with required reviewers

- Manual fallback, if the upload step can't be used: register an account at https://pypi.org with two-factor authentication enabled, ask one of the current maintainers to add you to the project, and create an API token scoped to the Pandana project. Download the artifacts of the `Build wheels` workflow run for the release from the Actions status page (one `wheels-*` archive per platform plus `sdist`) and unzip them into an empty `dist` directory. Then `pip install twine` and run `twine check --strict dist/*` and `twine upload dist/*`, entering `__token__` as the username and the token as the password


## Distributing a release on Conda Forge (for conda installation):

- The [conda-forge/pandana-feedstock](https://github.com/conda-forge/pandana-feedstock) repository controls the Conda Forge release, including which GitHub users have maintainer status for the repo

- Conda Forge bots usually detect new releases on PyPI within a few hours and open a pull request to update the feedstock, which a current feedstock maintainer needs to review and merge

- Before merging, check that the requirements in `recipe/meta.yaml` still match `setup.py` and `pyproject.toml`; the bot only updates the version and hash. Additional changes can be pushed to the bot's branch, for example to update the requirements or the list of maintainers

- The bots also open a pull request to rebuild the package for each new version of Python. Merge these once their checks pass rather than closing them: a closed rebuild is treated as done, and the package will be missing for that Python version

- You can also fork the feedstock and open a PR manually. It seems like this must be done from a personal account (not a group account like UDST) so that the bots can be granted permission for automated cleanup

- Check https://anaconda.org/conda-forge/pandana for the new version (may take a few minutes for it to appear)
