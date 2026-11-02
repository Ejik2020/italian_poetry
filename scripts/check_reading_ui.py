"""Browser acceptance checks. Run against a locally rendered Quarto book."""
import argparse
import os
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--base-url', default='http://127.0.0.1:8766/')
parser.add_argument('--screenshots', type=Path)
args = parser.parse_args()
base = args.base_url.rstrip('/') + '/'
with sync_playwright() as p:
    options = {'headless': True}
    if os.environ.get('CHROME_PATH'):
        options['executable_path'] = os.environ['CHROME_PATH']
    browser = p.chromium.launch(**options)
    context = browser.new_context(viewport={'width': 1600, 'height': 1080})
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(base)
    assert page.locator('.edition-masthead').is_visible()
    assert page.locator('.edition-wordmark').inner_text() == 'Итальянская поэзия'
    assert not page.locator('#quarto-sidebar').is_visible()
    assert not page.locator('.readingbar').is_visible()
    assert page.locator('img[src*="Gravity-7.jpg"]').evaluate('(e)=>e.complete && e.naturalWidth>0')
    page.get_by_role('link', name='Книга', exact=True).click()
    page.wait_for_url('**/book.html')
    assert page.locator('main a[href*="tiptopstreet.com"]').count() == 2
    assert not page.locator('.readingbar').is_visible()
    matrix = 0
    for width in [1600, 1100, 820, 430, 375, 320]:
        page.set_viewport_size({'width': width, 'height': 1080 if width > 760 else 844})
        for poet in ['Капрони', 'Каталано', 'Ламарк', 'Монтале']:
            page.goto(base + quote(poet) + '.html')
            page.wait_for_selector('.poet-page')
            await_fonts = page.evaluate('()=>document.fonts.ready.then(()=>true)')
            if matrix == 0:
                assert page.locator('.font-control output').inner_text() == '17'
            invariants = page.locator('.chapter-head').evaluate('''e=>({
                heading:getComputedStyle(e.querySelector('h1')).fontSize,
                bio:getComputedStyle(e.querySelector('.bio')).fontSize,
                bioFamily:getComputedStyle(e.querySelector('.bio')).fontFamily})''')
            assert 'Source Serif 4' in invariants['bioFamily']
            assert invariants['bio'] == '18px'
            assert page.locator('.bio').evaluate('(e)=>e.getBoundingClientRect().width') <= 680
            assert page.locator('.font-control').evaluate('(e)=>e.parentElement.classList.contains("readingbar")')
            assert page.locator('.reading-modes svg[aria-hidden="true"]').count() == 3
            assert page.locator('.chapter-head #title-block-header').evaluate('(e)=>getComputedStyle(e,"::before").width') == '56px'
            assert page.locator('.nav-page-previous .chapter-arrow').inner_text() == '←'
            assert page.locator('.nav-page-next .chapter-arrow').inner_text() == '→'
            assert page.locator('.chapter-head h1').evaluate('(e)=>parseFloat(getComputedStyle(e).marginBottom)') >= 27
            if width > 760:
                assert page.locator('#quarto-sidebar').is_visible()
            else:
                assert not page.locator('#quarto-sidebar').is_visible()
            for size in [16, 17, 20, 26, 30]:
                page.evaluate('''target=>{
                    let current=Number(document.querySelector('.font-control output').textContent);
                    while(current!==target){document.querySelector(current<target?'.font-up':'.font-down').click();current+=current<target?1:-1;}
                }''', size)
                for mode in ['parallel', 'translation', 'stacked']:
                    page.locator(f'.reading-modes [data-mode="{mode}"]').click()
                    state = page.evaluate('''()=>{
                        const reading=document.querySelector('.reading');
                        const first=document.querySelector('.poem');
                        const ru=first.querySelector('.russian'),it=first.querySelector('.italian');
                        const rb=ru.getBoundingClientRect(),ib=it.getBoundingClientRect();
                        const head=document.querySelector('.chapter-head');
                        return {
                            size:parseFloat(getComputedStyle(first.querySelector('.stanza')).fontSize),
                            title:parseFloat(getComputedStyle(first.querySelector('h3')).fontSize),
                            heading:getComputedStyle(head.querySelector('h1')).fontSize,
                            bio:getComputedStyle(head.querySelector('.bio')).fontSize,
                            mode:reading.dataset.mode,reflow:reading.dataset.reflow==='true',
                            original:getComputedStyle(it).display!=='none',
                            ruTop:rb.top,ruBottom:rb.bottom,itTop:ib.top,
                            overflow:document.documentElement.scrollWidth>innerWidth,
                            empty:[...document.querySelectorAll('.poem')].some(x=>!x.textContent.trim()),
                            overlap:[...document.querySelectorAll('.poem')].some((x,i,a)=>i && x.getBoundingClientRect().top<a[i-1].getBoundingClientRect().bottom-1)
                        };
                    }''')
                    assert state['size'] == size, state
                    assert state['title'] == size * 1.25, state
                    assert state['heading'] == invariants['heading'], state
                    assert state['bio'] == invariants['bio'], state
                    assert state['mode'] == mode and not state['overflow'], (width, poet, state)
                    assert not state['empty'] and not state['overlap'], (poet, state)
                    if mode == 'translation':
                        assert not state['original']
                    elif state['reflow'] or mode == 'stacked' or width <= 760:
                        assert state['itTop'] >= state['ruBottom'] - 1, state
                    else:
                        assert abs(state['itTop'] - state['ruTop']) < 1, state
                    matrix += 1
            page.locator('.reading-modes [data-mode="parallel"]').click()
            page.evaluate("()=>{while(Number(document.querySelector('.font-control output').textContent)>20)document.querySelector('.font-down').click()}")
            if args.screenshots:
                args.screenshots.mkdir(exist_ok=True, parents=True)
                page.screenshot(path=str(args.screenshots / f'{poet}-{width}.png'))
    # Desktop sidebar collapse/reopen and sticky chrome.
    page.set_viewport_size({'width': 1600, 'height': 1080})
    page.goto(base + quote('Капрони') + '.html')
    page.locator('.sidebar-heading').click()
    assert not page.locator('#quarto-sidebar').is_visible()
    assert page.locator('.font-control').is_visible()
    page.locator('.font-up').click()
    assert page.locator('.font-control output').inner_text() == '21'
    page.locator('.font-down').click()
    page.locator('.sidebar-switch').click()
    assert page.locator('#quarto-sidebar').is_visible()
    assert page.locator('#quarto-sidebar a.sidebar-item-text').count() == 32
    page.evaluate('window.scrollTo(0,1600)')
    page.wait_for_timeout(120)
    assert abs(page.locator('.readingbar').bounding_box()['y'] - 66) < 1
    assert page.locator('.chapter-head').bounding_box()['y'] < 0
    assert page.locator('.poem-index, #poem-panel').count() == 0
    assert page.locator('.font-control').is_visible()
    assert page.locator('.font-control').bounding_box()['y'] >= 66
    assert page.locator('.font-control').bounding_box()['y'] < 122
    page.get_by_role('button', name='Перевод', exact=True).focus()
    page.keyboard.press('Enter')
    assert page.locator('.reading').get_attribute('data-mode') == 'translation'
    assert page.get_by_role('button', name='Перевод', exact=True).evaluate('(e)=>getComputedStyle(e).outlineStyle') != 'none'
    snapshot=page.locator('.reading-modes').aria_snapshot()
    assert all(name in snapshot for name in ['Рядом', 'Перевод', 'Друг за другом'])
    assert page.locator('.font-control output').get_attribute('aria-live') == 'polite'
    page.locator('.nav-page-next a').click()
    page.wait_for_url('**/*html')
    assert 'Мениканти' in page.title()
    page.locator('.nav-page-previous a').click()
    page.wait_for_url('**/*html')
    assert 'Капрони' in page.title()
    # Persistence across pages and refresh.
    page.locator('.reading-modes [data-mode="translation"]').click()
    page.locator('.font-up').click()
    page.goto(base + quote('Ламарк') + '.html')
    assert page.locator('.reading').get_attribute('data-mode') == 'translation'
    assert page.locator('.font-control output').inner_text() == '21'
    page.reload()
    assert page.locator('.font-control output').inner_text() == '21'
    assert page.locator('.reading').get_attribute('data-mode') == 'translation'
    assert page.locator('.readingbar').get_attribute('lang') == 'ru'
    # Mobile drawer, keyboard close, and in-chapter navigation.
    page.set_viewport_size({'width': 390, 'height': 844})
    page.goto(base + quote('Капрони') + '.html')
    assert not page.locator('#quarto-sidebar').is_visible()
    page.locator('.sidebar-switch').click()
    assert page.locator('#quarto-sidebar').is_visible()
    page.keyboard.press('Escape')
    assert not page.locator('#quarto-sidebar').is_visible()
    page.locator('.sidebar-switch').click()
    page.locator('#quarto-sidebar a').filter(has_text='Гвидо Каталано').click()
    page.wait_for_url('**/*html')
    assert 'Каталано' in page.title()
    # All chapters remain accessible, including translation-only Pusterla.
    for source in Path('.').glob('*.qmd'):
        response=page.goto(base + quote(source.stem) + '.html')
        assert response.status == 200, source
        assert page.locator('main').inner_text().strip(), source
        if source.stem not in ['index','book']:
            assert page.locator('.nav-page-previous a').is_visible(), source
            assert page.locator('.nav-page-next a').is_visible(), source
            assert page.locator('.chapter-arrow').count() == 2, source
        else:
            assert page.locator('.chapter-head').count() == 0, source
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), source
    assert not errors, errors
    print(f'Passed {matrix} poet/width/size/mode combinations, navigation, persistence, drawer, and all 34 pages.')
    browser.close()
