"""Validate rendered search metadata without third-party dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import xml.etree.ElementTree as ET

BASE = 'https://www.alexfeigin.com/'


class Metadata(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.language = None
        self.title = ''
        self.metas = {}
        self.canonicals = []
        self.schemas = []
        self.in_title = False
        self.in_json = False
        self.json_text = ''
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.language = attrs.get('lang')
        elif tag == 'title':
            self.in_title = True
        elif tag == 'meta':
            key = attrs.get('name', attrs.get('property', ''))
            self.metas.setdefault(key, []).append(attrs.get('content', ''))
        elif tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))
        elif tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.in_json = True
            self.json_text = ''

    def handle_data(self, text):
        if self.in_title:
            self.title += text
        if self.in_json:
            self.json_text += text

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        elif tag == 'script' and self.in_json:
            self.schemas.append(json.loads(self.json_text))
            self.in_json = False


def main():
    root = Path('_book')
    sources = re.findall(r'^    - (.+\.qmd)\s*$', Path('_quarto.yml').read_text(), re.M)
    titles = set()
    for source in sources:
        name = str(Path(source).with_suffix('.html'))
        html = (root / name).read_text()
        page = Metadata(html)
        assert page.language == 'ru', name
        assert 'class="description"' not in html, (name, 'visible SEO description')
        assert 'translator-summary' not in html, (name, 'visible SEO introduction')
        author_name = 'Александр Фейгин' if source == 'book.qmd' else 'Александра Фейгина'
        assert author_name in page.title, (name, page.title)
        assert page.title not in titles, (name, 'duplicate title')
        titles.add(page.title)
        descriptions = page.metas.get('description', [])
        assert len(descriptions) == 1, name
        assert 'Italian poetry' in descriptions[0] and 'Feigin' in descriptions[0], name
        assert len(page.canonicals) == 1, name
        canonical = page.canonicals[0]
        expected = BASE if source == 'index.qmd' else BASE + name
        assert unquote(canonical) == expected, (name, canonical)
        assert len(page.metas.get('og:title', [])) == 1, name
        assert page.metas.get('og:locale') == ['ru_RU'], name
        image = 'images/clipboard-2631945230.png' if source == 'book.qmd' else 'images/Gravity-7.jpg'
        assert page.metas.get('og:image') == [BASE + image], name
        assert (root / image).is_file(), name
        assert page.metas.get('twitter:card'), name
        assert not any('noindex' in value.lower() for value in page.metas.get('robots', [])), name
        graphs = [node for schema in page.schemas for node in schema.get('@graph', [])]
        person = next(node for node in graphs if node['@type'] == 'Person')
        assert person['name'] == 'Александр Фейгин', name
        assert set(person['alternateName']) == {'Alex Feigin', 'Alexander Feigin'}, name
        book = next(node for node in graphs if node['@type'] == 'Book')
        assert book['translator']['@id'] == person['@id'], name
        assert any(node['@type'] == 'WebSite' and node['url'] == BASE for node in graphs), name
    sitemap = ET.parse(root / 'sitemap.xml')
    locations = [node.text for node in sitemap.findall('.//{*}loc')]
    paths = set()
    for url in locations:
        assert url.startswith(BASE), url
        assert not urlsplit(url).query and not urlsplit(url).fragment, url
        paths.add(unquote(urlsplit(url).path).lstrip('/') or 'index.html')
    assert paths == {str(Path(s).with_suffix('.html')) for s in sources}, paths
    assert f'Sitemap: {BASE}sitemap.xml' in (root / 'robots.txt').read_text()
    assert not re.search(r'^Disallow:\s*/\s*$', (root / 'robots.txt').read_text(), re.M)
    print(f'Validated SEO metadata and structured data on {len(sources)} pages, sitemap and robots.txt.')


if __name__ == '__main__':
    main()
