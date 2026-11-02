# V4 literary redesign review

The owner approved the redesign with the reading refinements below. Publication
uses the existing `main` branch and GitHub Pages workflow.

## Protected baseline

Annotated tag `v1.0-pre-redesign` was created and pushed **before implementation**.
It points to `ec8e8a6027492ee4e5357806df68834c45e60375`, the successfully deployed
production commit. Tag object: `92b3fce721a2938a4c09fb323cb3977936651b59`.
Do not modify, delete, or move this tag.

## Presentation implementation

- Quarto book, existing chapter URLs, GitHub Pages workflow, and custom domain
  remain in use. The attached prototype supplies presentation, not content.
- `filters/literary.lua` groups the existing Russian text and following
  `.italian` block as a poem, preserving their order and independent lengths.
  Original `.qmd` files and images are unchanged. Translation-only poems remain
  translation-only; untitled poems retain their original markers or first lines.
- The Lua filter fails rendering if any source text token or explicit line break
  changes during its transformation. Paragraphs remain separate stanza blocks;
  original break nodes remain in HTML. Visual line spans provide hanging wraps.
- Quarto's hidden metadata is retained outside the poem index. Viviani's supplied
  collection note remains a note between poems, with its full wording intact.
- `styles.css` applies the v4 paper, typography, spacing, and Quarto integration.
  The main image is the original local `images/Gravity-7.jpg`, without cropping.
- `edition.js` controls persistent reading mode, font size and sidebar navigation. Russian and Italian both use Literata; biographies use Source
  Serif 4 at 18–20 px / 1.68. Serif fallbacks remain available without Google Fonts.
- The 16–30 px verse control changes titles at exactly 1.25×, independently of
  the poet heading, biography, navigation, and browser zoom.
- Parallel mode reflows when the available reading width is less than 39 times
  the verse size. The saved `parallel` preference is preserved during reflow.
  Every subsequent poem starts below the taller language version.
- Desktop has a visible poet list by default with a single `☰ Поэты` control.
  Mobile uses a closed drawer and a compact reading-mode toolbar.
  Home and the real purchase page have no poet sidebar or reading toolbar.
- Latin display names are taken from the source biographies. Five names absent
  there have separate display metadata in `edition.js`; no biography is edited.

## Validation

- Full Quarto render: 34 pages; local URLs, fragments, CSS assets, and images pass.
- All 34 `.qmd` files and both image assets match the baseline tag byte for byte.
- All 177 supplied Italian originals remain in their matching poem units;
  Pusterla's four translation-only poems remain without invented originals.
- Complete rendered text and explicit break counts match the original published
  HTML on all 34 pages, excluding newly added navigation/control labels.
- Browser matrix: Caproni, Catalano, Lamarque, Montale; widths 1600, 1100, 820,
  390, and 320; verse sizes 16, 20, 26, 30; all three modes: 240 combinations.
- Verified exact title/verse ratio, unchanged heading/biography size, responsive
  reflow, no horizontal overflow or poem overlap, desktop collapse/reopen,
  mobile drawer and Escape behavior, sticky chrome, 32-poet navigation,
  purchase navigation and persistence across pages/reloads.
- All 34 pages remain accessible at phone width with no JavaScript exceptions.
- Specifically located all nine named acceptance poems, including long lines
  in Catalano, Lamarque, and Montale and short/uneven pairs in Caproni.

## Editorial review only

Catalano's **«Три смерти» / `Tre morti`** is asymmetric in the existing source:
the Russian side contains three death narratives; the supplied Italian side
contains the first narrative only. Both are reproduced exactly. No missing
Italian text has been reconstructed, added, or removed.

## Approved refinements

- Home wordmark: «Итальянская поэзия».
- Smaller poet/Home headings, with additional clearance before the Latin name.
- Default verse size: 17 px; explicit saved size preferences still persist.
- Compact segmented reading modes, visually separate from main navigation.
- The «Стихи» dropdown is removed. Size controls use a small bottom reading dock.
- Tighter spacing in the desktop poet list.
- Text, punctuation, stanza boundaries, line breaks, links, and images remain unchanged.

## Release

After local validation, publish from `main`, verify the GitHub Actions deployment
and both domain names, and create the annotated `v2.0.0` release tag for that
published commit. The protected pre-redesign tag remains unchanged.
