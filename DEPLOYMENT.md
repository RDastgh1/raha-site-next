# Netlify Deployment

This site is a Hugo site with optional Quarto-generated content. The current production deploy should build Hugo from the `raha-site-next` directory and publish the generated `public` directory.

## Netlify Build Settings

- **Base directory:** `raha-site-next`
- **Build command:** `hugo --minify`
- **Publish directory:** `public`
- **Hugo version:** `0.162.1`

Set the Hugo version in Netlify environment variables:

```text
HUGO_VERSION=0.162.1
HUGO_ENV=production
HUGO_ENABLEGITINFO=false
```

No Node.js, npm, or package install step is required for the current Hugo build.

## Quarto Requirements

Quarto source files live in `quarto/` and render to `content/quarto-generated` according to `quarto/_quarto.yml`.

Current local Quarto version:

```text
Quarto 1.9.37
```

Recommended deployment default:

1. Render Quarto locally only when Quarto content changes.
2. Commit the generated Markdown/content outputs.
3. Let Netlify run only `hugo --minify`.

Optional Netlify build command if Quarto rendering must happen during deploy:

```bash
cd quarto && quarto render && cd .. && hugo --minify
```

If using the optional Quarto build command, Netlify must have Quarto available. Netlify does not include Quarto by default, so use a Quarto install plugin or a custom build image/script before relying on server-side Quarto rendering.

## Environment Variables

Required:

```text
HUGO_VERSION=0.162.1
HUGO_ENV=production
```

Recommended:

```text
HUGO_ENABLEGITINFO=false
```

Optional, only if future analytics or external services are added:

```text
PLAUSIBLE_DOMAIN=
GOOGLE_ANALYTICS_ID=
```

Do not add secrets unless a feature explicitly requires them.

## Exact Launch Steps

1. Push the site repository to GitHub.
2. In Netlify, choose **Add new site** -> **Import an existing project**.
3. Connect the GitHub repository.
4. Set the base directory to:

   ```text
   raha-site-next
   ```

5. Set the build command to:

   ```text
   hugo --minify
   ```

6. Set the publish directory to:

   ```text
   public
   ```

7. Add environment variables:

   ```text
   HUGO_VERSION=0.162.1
   HUGO_ENV=production
   HUGO_ENABLEGITINFO=false
   ```

8. Trigger the first deploy.
9. Open the Netlify deploy preview and verify:
   - Homepage loads.
   - `/software/` loads.
   - `/publication/` loads.
   - PDF buttons open bundled PDFs.
   - `/talks/rmedicine-2024-scidatareportr/` loads and links to the Quarto talk.
   - No console-blocking mixed-content errors appear.
10. Once verified, assign the production domain in Netlify **Domain management**.

## Local Preflight

Run before pushing:

```bash
hugo --minify
```

If Quarto content changed:

```bash
cd quarto
quarto render
cd ..
hugo --minify
```

## Rollback Plan

Netlify keeps immutable deploys.

1. Go to **Netlify** -> target site -> **Deploys**.
2. Find the last known-good deploy.
3. Open the deploy menu and select **Publish deploy**.
4. Confirm the site returns to the previous working version.
5. Revert or fix the problematic commit in Git.
6. Push the fix and allow Netlify to create a new deploy.

For urgent rollback, use Netlify's **Publish deploy** first, then fix Git history afterward. Do not delete failed deploys until the root cause is understood.
