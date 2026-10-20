#!/usr/bin/env python3
"""Turn a freshly built demo page into the website copy at demos/<name>/index.html.

    python3 demos/apply_site_theme.py <built.html> <comparison|ndd|rounding>

It adds the site navbar, footer, favicon, fonts and demos/demo-theme.css, the
"Created by Zikai Xiong" byline, and the website-only fixes made to each copy.
Every step is idempotent, so running it on the current copy changes nothing.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent

TITLES = {
    'comparison': 'Color Picking by Comparison Feedback',
    'photo': 'Photo Editing by Comparison Feedback',
    'fairwasp': 'How Little Must Data Change to Be Fair?',
    'ndd': 'Normal Direction Descent (NDD)',
    'rounding': 'Does Symmetry Help Rounding?',
    'pdhg-lp-hardness': 'Why Is This LP Hard?',
    'pdhg-random-lps': 'How Hard Is a Random LP?',
}

DESCRIPTIONS = {
    'fairwasp': 'Interactive demo by Zikai Xiong: make loan data fair while moving it as little as possible, and compare FairWASP with reweighing.',
    'photo': 'Interactive demo by Zikai Xiong: edit a photo by answering only which of two versions is better, and watch an optimization algorithm learn from comparisons alone.',
    'comparison': 'Interactive demo by Zikai Xiong: find a color by answering only which of two colors is closer, and watch an optimization algorithm learn from comparisons alone.',
    'ndd': 'Interactive animation by Zikai Xiong: how comparisons alone give a normal direction, and the two descent methods NDD and adaNDD built on it.',
    'rounding': 'Interactive demo by Zikai Xiong: how the symmetry of a convex shape limits how well an ellipse can round it.',
    'pdhg-lp-hardness': 'Interactive demo by Zikai Xiong: why a tiny LP can be hard for restarted PDHG, and how a near tie in the LP or its dual makes it slow.',
    'pdhg-random-lps': 'Interactive demo by Zikai Xiong: restarted PDHG solves hundreds of random linear programs in your browser.',
}

PAPERS = {
    'comparison': ('Scheinberg &amp; Xiong', ['2604.26867']),
    'photo': ('Scheinberg &amp; Xiong', ['2604.26867']),
    'fairwasp': ('Xiong, Dalmasso, Mishler, Potluru, Balch &amp; Veloso', ['2311.00109']),
    'ndd': ('Scheinberg &amp; Xiong', ['2604.26867']),
    'rounding': ('Xiong &amp; Freund', ['2608.30876']),
    'pdhg-lp-hardness': ('Xiong', ['2410.04043']),
    'pdhg-random-lps': ('Xiong', ['2501.00728', '2410.04043']),
}

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='8' fill='%238B1D2C'/%3E"
           "%3Ccircle cx='19' cy='20' r='9' fill='%23fff'/%3E%3Ccircle cx='45' cy='20' r='9' fill='%23fff'/%3E%3Ccircle cx='32' cy='36' r='20' fill='%23fff'/%3E"
           "%3Ccircle cx='25' cy='33' r='2.5' fill='%238B1D2C'/%3E%3Ccircle cx='39' cy='33' r='2.5' fill='%238B1D2C'/%3E"
           "%3Cellipse cx='32' cy='42' rx='4.5' ry='3.5' fill='%238B1D2C'/%3E%3C/svg%3E")

HEAD = f'''<meta name="author" content="Zikai Xiong">
<link rel="icon" type="image/svg+xml" href="{FAVICON}">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap">
<link rel="stylesheet" href="../demo-theme.css">
'''

NAV = '''<header class="site-header">
  <nav class="navbar" aria-label="Site navigation">
    <a class="navbar-brand" href="../../index.html">Zikai&nbsp;Xiong</a>
    <button class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false" aria-controls="nav-menu">&#9776;</button>
    <ul class="nav-links" id="nav-menu">
      <li><a href="../../index.html">about</a></li>
      <li><a href="../../research.html">research</a></li>
      <li><a href="../" class="active">demos</a></li>
      <li><a href="../../news.html">news</a></li>
      <li><a href="../../cv/" target="_blank" rel="noopener">cv</a></li>
      <li><a href="../../awards.html">awards</a></li>
      <li><a href="../../teaching.html">teaching</a></li>
      <li><a href="../../talks.html">talks</a></li>
      <li><a href="../../blogs.html">blog</a></li>
      <li><a href="../../gallery.html">photos</a></li>
    </ul>
  </nav>
</header>
'''

FOOT = '<div class="site-foot">&copy; 2026 Zikai Xiong &middot; <a href="../">All interactive demos</a></div>\n'
NAVJS = '<script src="../../assets/js/nav.js"></script>\n'


COMPARISON_UI = '''<script id="site-ui">
// Website-only UI layer for the comparison demo: the comparison is the one obvious action.
(function () {
  var $ = function (id) { return document.getElementById(id); };
  // click a swatch to answer
  [['swA', 'ansA'], ['swB', 'ansB']].forEach(function (p) {
    var sw = $(p[0]), btn = $(p[1]);
    if (!sw || !btn) return;
    sw.classList.add('pickable');
    sw.addEventListener('click', function () { if (!btn.disabled) btn.click(); });
  });
  // one-line instruction under the question, following the task
  var prompt = $('prompt'), hint = document.createElement('p');
  hint.className = 'booth-hint';
  prompt.insertAdjacentElement('afterend', hint);
  function syncHint() {
    var t = prompt.textContent;
    hint.textContent = /^Done/.test(t) ? ''
      : /like more/.test(t) ? 'Click the shade you like more. No preference? Click Same.'
      : 'Click the color that is closer to the target. Cannot tell? Click Same.';
    hint.hidden = !hint.textContent;
  }
  new MutationObserver(syncHint).observe(prompt, { childList: true, characterData: true, subtree: true });
  syncHint();
  // Undo next to the comparison count
  var foot = document.querySelector('.booth-foot'), undo = $('undoBtn'), count = $('boothCount');
  if (foot && undo && count) count.insertAdjacentElement('afterend', undo);
  // everything else in the toolbar goes under "More options"
  var bar = document.querySelector('.toolbar'), more = document.createElement('details');
  more.className = 'more-ctl';
  more.innerHTML = '<summary class="btn">More options</summary><div class="more-row"></div>';
  var row = more.querySelector('.more-row');
  [bar.querySelector('.seg[aria-label="Dimension"]'), $('restartBtn'), $('newTargetBtn'), $('autoBtn'), $('revealBtn')]
    .forEach(function (el) { if (el) row.appendChild(el); });
  bar.appendChild(more);
  document.addEventListener('click', function (e) { if (more.open && !more.contains(e.target)) more.open = false; });
})();
</script>
'''


def byline(name):
    authors, ids = PAPERS[name]
    links = ' and '.join(f'<a href="https://arxiv.org/abs/{a}" target="_blank" rel="noopener">arXiv:{a}</a>' for a in ids)
    return f'Created by Zikai Xiong · Based on {authors}, {links}'


def replace_once(s, old, new):
    assert s.count(old) == 1, f'expected exactly one match for: {old[:80]!r}'
    return s.replace(old, new)


def apply(s, name):
    # <html>: theme classes, light by default like the website
    m = re.search(r'<html[^>]*>', s)
    tag = m.group(0)
    if 'demo-site' not in tag:
        extra = ' demo-pdhg' if name.startswith('pdhg') else ''
        new = tag[:-1] + f' class="demo-site demo-{name}{extra}"'
        if 'data-theme' not in new:
            new += ' data-theme="light"'
        s = s.replace(tag, new + '>', 1)

    if 'href="../demo-theme.css"' not in s:
        s = replace_once(s, '<meta charset="utf-8">\n', '<meta charset="utf-8">\n' + HEAD)
    # description and link-preview tags (shown when the link is shared)
    if 'property="og:image"' not in s:
        desc = DESCRIPTIONS[name]
        meta = '' if '<meta name="description"' in s else f'<meta name="description" content="{desc}">\n'
        meta += (f'<meta property="og:type" content="website">\n'
                 f'<meta property="og:title" content="{TITLES[name]} | Zikai Xiong">\n'
                 f'<meta property="og:description" content="{desc}">\n'
                 f'<meta property="og:url" content="https://zikaixiong.github.io/demos/{name}/">\n'
                 f'<meta property="og:image" content="https://zikaixiong.github.io/demos/{name}/preview.jpg">\n'
                 f'<meta name="twitter:card" content="summary_large_image">\n')
        s = replace_once(s, '<link rel="stylesheet" href="../demo-theme.css">\n', '<link rel="stylesheet" href="../demo-theme.css">\n' + meta)

    # navbar and footer: replace the current ones so that updates reach every demo
    s = re.sub(r'<header class="site-header">.*?</header>\n', '', s, count=1, flags=re.S)
    s = re.sub(r'<div class="site-foot">.*?</div>\n', '', s, count=1, flags=re.S)
    if 'class="site-header"' not in s:
        if '<body' in s:
            m = re.search(r'<body[^>]*>\n', s)
            s = s[:m.end()] + NAV + s[m.end():]
        else:
            s = replace_once(s, '<div class="wrap">', NAV + '<div class="wrap">')

    if name != 'ndd' and 'class="site-foot"' not in s:
        if name == 'comparison':
            # end of .wrap: the page's own footer note, then the closing div
            k = s.index('</footer>\n</div>\n') + len('</footer>\n</div>\n')
            s = s[:k] + FOOT + s[k:]
        else:
            s = replace_once(s, NAVJS + '</body>', FOOT + NAVJS + '</body>') if NAVJS + '</body>' in s else replace_once(s, '</body>', FOOT + '</body>')

    if 'assets/js/nav.js' not in s:
        if '</body>' in s:
            s = replace_once(s, '</body>', NAVJS + '</body>')
        else:
            s = replace_once(s, '</html>', NAVJS + '</html>')

    # byline under the title
    if name in ('comparison', 'rounding', 'photo', 'fairwasp'):
        s = re.sub(r'<p class="cite">.*?</p>', '<p class="cite">' + byline(name) + '</p>', s, count=1, flags=re.S)

    if name.startswith('pdhg') and 'class="cite"' not in s:
        m = re.search(r'<h1>.*?</h1>\n', s)
        ind = re.match(r' *', s[s.rfind('\n', 0, m.start()) + 1:]).group(0)
        s = s[:m.end()] + f'{ind}<p class="cite">{byline(name)}</p>\n' + s[m.end():]

    if name == 'comparison':
        # title that names the task and the kind of feedback
        s = s.replace('<title>Optimizing by Comparison</title>', '<title>Color Picking by Comparison Feedback</title>')
        s = s.replace('<h1>Optimizing by Comparison</h1>', '<h1>Color Picking by Comparison Feedback</h1>')
        s = s.replace('Which side is closer to the target?', 'Which color is closer to the target?')
        # clickable swatches, a one-line instruction, Undo by the answers, the rest under "More options"
        if 'id="site-ui"' not in s:
            s = replace_once(s, NAVJS, NAVJS + COMPARISON_UI)

        # default comparison budget 40 (was 20), with 60 and 100 as options
        s = s.replace('<option value="20" selected>20, then reveal</option><option value="40">40, then reveal</option><option value="0">No limit</option>',
                      '<option value="20">20, then reveal</option><option value="40" selected>40, then reveal</option><option value="60">60, then reveal</option><option value="100">100, then reveal</option><option value="0">No limit</option>')
        s = s.replace("set:{task:'match',d:2,T:1,h0:0.4,budget:20,", "set:{task:'match',d:2,T:1,h0:0.4,budget:40,")
        s = s.replace('auto:false, reveal:false, budget:20, atBudget', 'auto:false, reveal:false, budget:40, atBudget')
        s = s.replace('id="moreBtn" hidden>20 more comparisons', 'id="moreBtn" hidden>40 more comparisons')
        s = s.replace('textContent=`${S.set.budget||20} more comparisons`', 'textContent=`${S.set.budget||40} more comparisons`')

    if name == 'ndd':
        # the step-by-step animation (2026-10-18): title, and the byline in the panel
        s = re.sub(r'<title>Normal direction descent, step by step</title>', '<title>Normal Direction Descent (NDD)</title>', s, count=1, flags=re.I)
        s = s.replace('<div class="ttl">Normal direction descent, step by step</div>', '<div class="ttl">Normal Direction Descent (NDD)</div>')
        cite = '<div class="sub cite">' + byline(name) + '</div>'
        s = re.sub(r'<div class="sub">Comparison-based optimization · Scheinberg &amp; Xiong, <a [^>]*>arXiv:2604\.26867</a></div>', cite, s, count=1)
        s = re.sub(r'<div class="sub cite">.*?</div>', cite, s, count=1)
        if '.sub.cite a' not in s:
            s = replace_once(s, '</style>', '.sub.cite a { color: var(--accent); }\n</style>')
    return s


if __name__ == '__main__':
    src, name = pathlib.Path(sys.argv[1]), sys.argv[2]
    assert name in PAPERS, name
    out = HERE / name / 'index.html'
    out.write_text(apply(src.read_text(encoding='utf-8'), name), encoding='utf-8')
    print('wrote', out)
