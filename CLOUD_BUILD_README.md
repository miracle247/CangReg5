# Building the .exe in the Cloud with GitHub Actions

This lets a Windows server in the cloud build your `.exe` for you — no
Windows machine needed on your end.

## One-time setup

1. **Create a GitHub account** (free) if you don't have one:
   https://github.com/join

2. **Create a new repository**
   - Go to https://github.com/new
   - Name it something like `canreg5-tokenizer`
   - Set it to **Private** if you don't want the script public
   - Click "Create repository"

3. **Add the files to the repo**
   In your new (empty) repo, click "uploading an existing file" and upload:
   - `canreg5_pii_tokenizer.py`
   - `build.yml` — but rename it to `.github/workflows/build.yml`
     (GitHub's upload page lets you type a path with folders when you
     name the file — type exactly: `.github/workflows/build.yml`)

   Commit the changes.

## Running the build

1. Go to the **"Actions"** tab of your repository.
2. You should see a workflow called **"Build Windows EXE"**.
3. Click it, then click **"Run workflow"** → **"Run workflow"** (green button).
4. Wait ~1-2 minutes for it to finish (green checkmark = success).
5. Click on the completed run, scroll down to **"Artifacts"**, and download
   **"CanReg5_PII_Tokenizer"** — this is a zip containing your `.exe`.

That's it — the `.exe` was built on a Windows cloud runner and is ready to
use on any Windows machine, no Python required.

## Notes
- The workflow also runs automatically any time you push a change to
  `canreg5_pii_tokenizer.py`.
- Build artifacts are kept for 90 days by default on GitHub.
- If you ever update the script, just upload the new version to the repo
  and re-run the workflow (or let it run automatically on push).
