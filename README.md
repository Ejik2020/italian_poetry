# Современная Итальянская Поэзия

Quarto book of Alexander Feigin's translations, initially migrated from
`Poetry Book.zip` in November 2026. Author-supplied additions and corrections are
maintained in the Quarto source. The book currently contains 33 poet chapters,
the introduction, and the purchase page. The v4 literary redesign updates the
presentation layer; see [review notes](docs/redesign-review.md).

## Content and appearance

- Poet chapters are the Cyrillic `.qmd` files in the repository root.
- `index.qmd` is the introduction; `book.qmd` is «Купить книгу».
- `_quarto.yml` controls chapter order, navigation, and the Cosmo HTML theme.
- `styles.css` contains the literary design; `images/` contains the supplied images.
- `filters/literary.lua` renders poem pairs, titles, stanzas, and hanging line
  wraps without editing source text. Keep source `.italian` blocks immediately
  after their matching translations; preserve stanza paragraphs and hard breaks.
- `edition.js` and `includes/edition.html` provide reading modes, the independent
  verse/title size control (17 px default), saved font-size/sidebar preferences, and responsive
  navigation. Each poet chapter opens in «Друг за другом» mode on phones (up to 760 px)
  and «Рядом» on larger screens. Readers can switch modes within the chapter. Thin icons and text identify the reading modes; size controls stay
  at the right of the sticky reading toolbar, including when the sidebar is closed.
- `_book/` and `.quarto/` are generated and ignored. Do not edit rendered HTML.

To add a poem, edit the relevant `.qmd` file using the existing poem formatting.
Preserve explicit backslashes at line endings (Markdown hard breaks), blank
lines between stanzas, and the existing spacing between poems. Do not reflow
poetry or normalize punctuation. Include Italian originals only when supplied.
For a multi-part poem such as «Три смерти» in `Каталано.qmd`, keep the
shared titles inside the `.poem-cycle` wrapper, followed by one `.poem-part`
wrapper per matched Russian/Italian section. Each part contains its Russian
subtitle and verses followed by its `.italian` block. These independent rows
align corresponding subtitles even when translations have different lengths.
Use longer colon fences for the outer wrappers, as in the existing example.

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

The optional browser checks need `pip install -r requirements-dev.txt` and
`playwright install chromium`. Serve `_book` with `python3 -m http.server 8766
--directory _book` in a separate terminal, then run:

```sh
python3 scripts/check_reading_ui.py --base-url http://127.0.0.1:8766/
```

To use an existing Chrome installation, set `CHROME_PATH` to its executable.
For the one-time redesign content audit, run
`python3 scripts/check_preservation.py`; this compares against the immutable
`v1.0-pre-redesign` tag and intentionally flags subsequent content edits.

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

## Search visibility

`filters/seo.lua` supplies a unique Russian search title and bilingual description
for each page without changing its visible literary heading. `includes/seo.html`
identifies the translator as Александр Фейгин / Alexander Feigin / Alex Feigin
using Person, WebSite and Book structured data. SEO descriptions are emitted
only in the HTML head, not as visible title-block descriptions. No additional
English introduction or hidden keyword text is included in the page body.

`_quarto.yml` sets Russian as the document language, enables canonical links and
social previews, and supplies the published `book.site-url`. Quarto generates
`sitemap.xml` and a `robots.txt` sitemap reference automatically. The post-render
script `scripts/finalize_sitemap.py` aligns sitemap entries with canonical URLs
and safely encodes Cyrillic filenames and apostrophes. Russian and
Italian verse blocks retain their individual language attributes. There are no
separate English translations of the pages, so do not add English `hreflang`
links pointing to these same Russian pages.

After publication, verify the domain in Google Search Console, submit
`https://www.alexfeigin.com/sitemap.xml`, and inspect/request indexing for the
Home page and representative poet chapters. Domain verification uses the exact
TXT value provided by Google at IONOS; preserve the GitHub verification and
all email DNS records. Do not put private account credentials in the repository.
SEO changes help search engines understand the site; indexing and rankings
are controlled by the search engines and are not guaranteed.

Run `python3 scripts/check_seo.py` after rendering to check the metadata,
structured data, sitemap, and crawl access alongside the normal site checks.
