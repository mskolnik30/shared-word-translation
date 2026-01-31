# The Shared Word Translation (Provisional)

The Shared Word Translation is an ongoing translation project of the Christian Scriptures.

Texts are translated and released incrementally. Books may receive minor revisions as the work continues.

This repository contains the canonical source files for the translation.

## Deploying to Church Commons (WordPress)

GitHub is the single source of truth. WordPress renders a mirrored copy.

**Server mirror location (do not edit these files directly):**
- `wp-content/uploads/tsw-repo/`

**Update workflow**
1. GitHub → Code → Download ZIP (main)
2. Unzip locally
3. Upload the *contents* of the repo folder (books/, README.md, TRANSLATION_PHILOSOPHY.md) into:
   - `wp-content/uploads/tsw-repo/`
   Replace existing files as needed.
4. In WordPress, clear cache.

**Shortcode**
- `[tsw book="philippians" chapter="1"]`
