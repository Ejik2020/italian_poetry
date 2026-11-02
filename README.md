# Современная Итальянская Поэзия

Quarto book of Alexander Feigin's translations. The November 2026 migration uses
`Poetry Book.zip` as the content authority: 32 poet chapters, the introduction,
and the purchase page. Poetry text, punctuation, line breaks, supplied Italian
originals, and `styles.css` are preserved from that archive.

## Content and appearance

- Poet chapters are the Cyrillic `.qmd` files in the repository root.
- `index.qmd` is the introduction; `book.qmd` is «Купить книгу».
- `_quarto.yml` controls chapter order, navigation, and the Cosmo HTML theme.
- `styles.css` contains custom styles; `images/` contains the supplied images.
- `_book/` and `.quarto/` are generated and ignored. Do not edit rendered HTML.

To add a poem, edit the relevant `.qmd` file using the existing poem formatting.
Preserve explicit backslashes at line endings (Markdown hard breaks), blank
lines between stanzas, and the existing spacing between poems. Do not reflow
poetry or normalize punctuation. Include Italian originals only when supplied.
For a new poet, create a UTF-8 `.qmd` file with the intended Cyrillic filename,
add it to `book.chapters` in `_quarto.yml`, and check spelling and case exactly.
The apostrophe in `Д'Агостини.qmd` is part of its filename.

## Preview and checks

Install [Quarto](https://quarto.org/docs/get-started/). CI pins **1.10.20**;
use that version to reproduce publication. Python 3 is needed only for validation.

```sh
quarto preview
quarto render
python3 scripts/check_site.py
```

Review the introduction, purchase page and its external purchase link, a short
chapter such as Пьерсанти, and long chapters such as Каталано and Ламарк.
Check desktop and mobile navigation, images, line breaks, and stanza spacing.
The validator checks all rendered local links, fragment IDs, stylesheets,
images, chapter filenames, and CSS assets with exact case/Unicode spelling.
It rejects root-relative local HTML links that break `/italian_poetry/` hosting.

## Automatic GitHub Pages publication

`.github/workflows/publish.yml` renders and validates every push to `main` and
every pull request targeting `main`. Only `main` publishes, using GitHub's Pages
artifact upload and deployment actions. The workflow can also be run manually
from **Actions → Render and publish Quarto book → Run workflow** on `main`.
No Quarto Pub token or personal access token is needed.

One-time repository setting: **Settings → Pages → Build and deployment →
Source → GitHub Actions**. Keep the custom domain unset until the repository
URL has been verified. The site URL is:
<https://ejik2020.github.io/italian_poetry/>.

`gh-pages` is retained as historical output, but the new workflow does not write
to it. Do not also run `quarto publish gh-pages` or deploy from a branch. Old
Quarto Pub metadata and obsolete/generated files were removed from `main`;
Git history preserves them, including the retired Бенедетти chapter.

Routine: supply poems or styling instructions, edit Quarto source, preview and
review the changes, then push the reviewed changes. GitHub rebuilds and publishes.

## Failed builds

Open **Actions** and select the run for the pushed commit. `build` contains the
Quarto render and link-check logs. Check missing files, exact Cyrillic spelling,
filename case, YAML indentation, and local image paths. Reproduce with the
commands above. Only successful builds proceed to `deploy`.

If `deploy` fails, confirm the Pages source is **GitHub Actions**, Actions are
enabled, and the `github-pages` environment permits deployment from `main`.
The deploy job needs `pages: write` and `id-token: write`; these are declared in
the workflow. A pending environment approval must be handled in GitHub.
Use the deployment job's URL and confirm its commit before checking browser
caches. Never force-push as a publication repair.

## Custom domain (deferred)

After verifying the repository URL, connect `www.alexfeigin.com` in Pages
settings and configure its DNS with the domain provider. First inspect the
provider, existing records, email records, and any existing website redirects.
Decide how the bare `alexfeigin.com` should reach `www`, enable HTTPS once the
certificate is ready, and verify both names. No domain file or DNS change is
part of the initial migration.
