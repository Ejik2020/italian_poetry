"""Use rendered canonical URLs in Quarto's sitemap, including Unicode filenames."""
from html import unescape
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit
import xml.etree.ElementTree as ET

from check_seo import BASE, Metadata

root = Path('_book')
sitemap = root / 'sitemap.xml'
namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('', namespace)
tree = ET.parse(sitemap)
seen = set()
for location in tree.findall('.//{*}loc'):
    # Quarto can double-escape the apostrophe in Д'Агостини as &amp;#39;.
    url = unescape(location.text)
    parsed = urlsplit(url)
    assert url.startswith(BASE) and not parsed.query and not parsed.fragment, url
    path = unquote(parsed.path).lstrip('/') or 'index.html'
    page = Metadata((root / path).read_text())
    assert len(page.canonicals) == 1, path
    canonical = urlsplit(page.canonicals[0])
    assert page.canonicals[0].startswith(BASE), path
    uri = urlunsplit((canonical.scheme, canonical.netloc,
                     quote(unquote(canonical.path), safe='/'), '', ''))
    assert uri not in seen, uri
    seen.add(uri)
    location.text = uri
# Keep Quarto's modification times; do not invent dates or rankings.
tree.write(sitemap, encoding='UTF-8', xml_declaration=True)
print(f'Finalized {len(seen)} canonical sitemap URLs.')
