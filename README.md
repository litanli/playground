# Collection of toy problems and demonstrations.

# Setup
1. Install [Poetry](https://python-poetry.org/docs/)
2. Install dependencies from lockfile by running `poetry install` from repo root. 
By default the virtualenv will be created in `{cache-dir}/virtualenvs` where 
[cache-dir](https://python-poetry.org/docs/configuration/#cache-dir) is 
OS-specific 
3. To run scripts, activate the virtualenv by running `poetry shell` anywhere 
in the repo. Run ``poetry env info --executable`` to see the executable's path.
4. To run notebooks select this virtualenv's executable path as the kernel.
