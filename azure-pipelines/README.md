# CI pipelines

Two pipelines, split so a frontend change does not run backend checks and vice versa.

| File | Runs when | Checks |
|---|---|---|
| `backend-ci.yml` | anything under `backend/` changes | install, ruff lint, app imports, document shapes are valid |
| `frontend-ci.yml` | anything under `frontend/` changes | `npm ci`, ESLint, `tsc --noEmit`, `next build` |

Both run in about a minute and neither needs a database.

## Creating the pipelines

Not done yet. For each file:

1. **Pipelines > New pipeline**
2. **Azure Repos Git** > **Project G**
3. **Existing Azure Pipelines YAML file**
4. Pick the file, then **Save** (not *Save and run*)
5. Rename it to something readable, e.g. `backend-ci` / `frontend-ci`

## Making them run on pull requests

This is the part that is easy to miss. **Azure Repos does not support the `pr:`
trigger in YAML** - it is a GitHub/Bitbucket feature and is silently ignored here.
Both files set `pr: none` so it is obvious that this is deliberate.

To get PR runs you add a branch policy instead:

**Repos > Branches > `main` > ... > Branch policies > Build Validation > +**

- Build pipeline: `backend-ci`
- Path filter: `/backend/*`
- Trigger: Automatic
- Policy requirement: Required

Repeat with `frontend-ci` and `/frontend/*`. The path filter matters - without it
every frontend PR waits on the backend build and vice versa.

## What the backend checks actually catch

The two custom checks are not busywork, they are both bugs we have already hit:

- **App imports** runs with no Cosmos reachable. The client is built on first use
  rather than at import, so this catches "a fresh clone does not start" without
  needing a database. That has broken `main` twice before.
- **`scripts/check_documents.py`** builds one of every document shape and checks the
  field names. A shape can import perfectly and still write the wrong keys, and every
  part of the app has to agree on them.

## Things deliberately left out

- **Tests.** `tests/` runs locally with `pytest` and needs no database. Worth adding as a step.
- **`ruff format --check`.** Enabling it today would reformat 11 files in one go.
  Worth doing as its own PR so the diff is reviewable, rather than hiding it in here.
- **Anything against a real Cosmos.** The emulator takes minutes to start and is not
  worth it per build. The shape check covers what would otherwise be caught late.
- **Caching.** Both jobs are fast enough that pip/npm caching is not worth the extra
  moving parts yet.
- **Deployment.** These only build and validate. Nothing deploys anywhere.

## Local equivalents

Everything CI runs, you can run yourself:

```bash
# backend
cd backend
pip install -r requirements.txt -r requirements-dev.txt
ruff check .
python -c "from app.main import app"
python scripts/check_documents.py

# frontend
cd frontend
npm ci
npm run lint
npx tsc --noEmit
npm run build
```

Note CI pins **Python 3.12** and **Node 20**. If you are on a different version
locally you can hit problems that CI does not, and the other way round.
