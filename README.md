# Collection of toy problems and demonstrations.

# Setup
## uv
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Run `uv venv` from repository root to install dependencies from the lockfile `uv.lock`.
3. `uv run` to run scripts, to run notebooks select this venv (`.venv/bin/python`) as the kernel.
4. `uv add` and `uv remove` to add and remove packages from `project.toml`

## pre-commit
Run `pre-commit` install to add the hooks specified in `.pre-commit-config.yaml`
to `.git/hooks`.
