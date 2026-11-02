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

One-time repository settings:

1. **Settings → Pages → Build and deployment → Source → GitHub Actions**.
2. **Settings → Environments → github-pages → Deployment branches and tags**:
   keep **Selected branches and tags** and add a **Branch** rule named `main`.
   Confirm `main` appears in the allowed list. The historical `gh-pages` rule
   can remain; it does not cause the new workflow to publish from that branch.

The published site is <https://www.alexfeigin.com/>. The original repository
URL, <https://ejik2020.github.io/italian_poetry/>, redirects to the custom domain.
`book.site-url` in `_quarto.yml` records the published address.

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

## Custom domain

DNS is managed at IONOS. GitHub Pages settings use `www.alexfeigin.com` as the
custom domain, with HTTPS enforced. The `www` CNAME points to
`ejik2020.github.io` (no repository path). The bare domain retains GitHub Pages
A records: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, and
`185.199.111.153`; GitHub redirects it to `www`.

Keep the `_github-pages-challenge-Ejik2020` TXT record used for account-level
domain verification, and preserve all MX and other email records. With Actions
publication, GitHub's custom-domain setting controls the binding; a repository
`CNAME` file is not required. Check both names, the introduction, purchase page,
and a Cyrillic chapter after domain changes. If a previously failing root URL
still returns a cached 404 while `/index.html` works, republish and recheck it.
