"""Builds the OVAIC website in all languages: python3 tools/build.py (run from the repo root)."""
import html
import pathlib
import re

from people import BOARD, FOUNDED, MEMBERS, OCT, P
from texts import T
from open_texts import JOIN, OPEN

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
LANGS = ["en", "de", "fr", "it", "es", "pt", "ru", "uk", "be", "pl", "cs", "sk", "sl", "sr", "hu", "lv", "lt", "et", "sv", "no", "ja", "ko"]
OLD = ["en", "de", "fr", "it", "es", "ja"]  # languages with full translations of the legal documents
MAIL = '<a href="/contact/">ovaic.org/contact</a>'
SITE = "https://ovaic.org"
LABEL = {"en": "English", "de": "Deutsch", "fr": "Français", "it": "Italiano", "es": "Español", "pt": "Português", "ru": "Русский",
         "uk": "Українська", "be": "Беларуская", "pl": "Polski", "cs": "Čeština", "sk": "Slovenčina", "sl": "Slovenščina",
         "sr": "Српски", "hu": "Magyar", "lv": "Latviešu", "lt": "Lietuvių", "et": "Eesti", "sv": "Svenska", "no": "Norsk", "ja": "日本語", "ko": "한국어"}

# Newer languages: home page and application form translated; legal documents shown in English (binding).
import copy
from tr_1 import TR as _t1
from tr_2 import TR as _t2
from tr_3 import TR as _t3
from tr_4 import TR as _t4
for _l, _tr in {**_t1, **_t2, **_t3, **_t4}.items():
    T[_l] = {**copy.deepcopy(T["en"]), **_tr, "c_note": _tr["docnote"]}
    P[_l] = {**copy.deepcopy(P["en"]), "nav": _tr["gov"]}
    FOUNDED[_l], OCT[_l] = _tr["founded"], _tr["oct"]
assert set(T) == set(LANGS), set(LANGS) ^ set(T)


def doc(kind, lang):
    f = TOOLS / f"{kind}_{lang}.md"
    return (f if f.exists() else TOOLS / f"{kind}_en.md").read_text()


def base(lang):
    return "/" if lang == "en" else f"/{lang}/"


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return re.sub(r"(https://[^\s<]+)", r'<a href="\1">\1</a>', s)


def table(rows):
    rows = [r.strip().strip("|").split("|") for r in rows if not re.match(r"^\|[-| ]+\|$", r.strip())]
    head = "".join(f"<th>{inline(c.strip())}</th>" for c in rows[0])
    body = "".join("<tr>" + "".join(f"<td>{inline(c.strip())}</td>" for c in r) + "</tr>" for r in rows[1:])
    return f"<table><tr>{head}</tr>{body}</table>"


def md(text):
    lines, buf, out_lines = text.splitlines(), [], []
    for line in lines + [""]:
        if line.startswith("|"):
            buf.append(line)
            continue
        if buf:
            out_lines.append("\x00" + table(buf))
            buf = []
        out_lines.append(line)
    text = "\n".join(out_lines)
    out, lst, anchor = [], None, ""
    for line in text.splitlines():
        m_id = re.match(r"\{#([a-z]+)\}$", line)
        if m_id:
            anchor = f' id="{m_id.group(1)}"'
            continue
        m_ol, m_ul = re.match(r"\d+\. (.*)", line), re.match(r"- (.*)", line)
        tag = "ol" if m_ol else "ul" if m_ul else None
        if lst and tag != lst:
            out.append(f"</{lst}>")
            lst = None
        if tag:
            if not lst:
                out.append(f"<{tag}>")
                lst = tag
            out.append(f"<li>{inline((m_ol or m_ul).group(1))}</li>")
        elif line.startswith("### "):
            out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2{anchor}>{inline(line[3:])}</h2>")
            anchor = ""
        elif line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("\x00"):
            out.append(line[1:])
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
    if lst:
        out.append(f"</{lst}>")
    return "\n".join(out)


def head(lang, title, path):
    t = T[lang]
    alts = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{SITE}{base(l)}{path}">' for l in LANGS
    )
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(t['desc'])}">
<meta property="og:title" content="Open Verifiable AI Consortium (OVAIC)">
<link rel="canonical" href="{SITE}{base(lang)}{path}">
{alts}
<link rel="alternate" hreflang="x-default" href="{SITE}/{path}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/style.css">
<script src="/theme.js"></script>
</head>"""


def tnote(lang):
    n = T[lang].get("note")
    return f'\n<div class="tnote"><div class="wrap">{n}</div></div>' if n else ""


def header(lang, path):
    t, b = T[lang], base(lang)
    ids = ["why", "principles", "work", "join"]
    nav = "".join(f'<a href="{b}#{i}">{n}</a>' for i, n in zip(ids, t["nav"]))
    nav += f'<a href="{b}charter/">{t["nav"][4]}</a><a href="{b}governance/">{P[lang]["nav"]}</a>'
    langs = ('<details class="lang"><summary aria-label="Language">&#127760; ' + LABEL[lang] + '</summary><div class="lang-menu">'
             + "".join(f'<a href="{base(l)}{path}" hreflang="{l}" lang="{l}" data-lang="{l}"'
                       + (' aria-current="true"' if l == lang else "") + f">{LABEL[l]}</a>" for l in LANGS)
             + "</div></details>")
    return f"""<body>
<header><div class="wrap">
  <a class="brand" href="{b}"><svg class="mark" width="30" height="30" viewBox="0 0 100 100" aria-hidden="true"><path d="M50 94V60" stroke="currentColor" stroke-width="7" stroke-linecap="round"/><path class="l" d="M50 62C37 62 20 54 13 35C33 33 47 45 50 62Z"/><path class="r" d="M50 62C58 40 73 19 95 6C97 37 80 58 50 62Z"/></svg><b>OVAIC</b> · Open Verifiable AI Consortium</a>
  <nav>{nav}{langs}</nav>
</div></header>{tnote(lang)}"""


SCRIPT = """<script>
(function(){
  function get(){try{return localStorage.getItem('ovaic-lang')}catch(e){return null}}
  document.querySelectorAll('.lang-menu a').forEach(function(a){a.addEventListener('click',function(){try{localStorage.setItem('ovaic-lang',a.dataset.lang)}catch(e){}})});
  if(document.documentElement.lang!=='en'||get())return;
  var l=(navigator.language||'').slice(0,2).toLowerCase();
  if(["de","fr","it","es","pt","ru","uk","be","pl","cs","sk","sl","sr","hu","lv","lt","et","sv","no","ja","ko"].indexOf(l)>=0)location.replace('/'+l+location.pathname+location.hash);
})();
</script>"""


def footer(lang):
    t, b = T[lang], base(lang)
    return f"""<footer><div class="wrap">OVAIC · Open Verifiable AI Consortium · <a href="{b}charter/">{t['foot_charter']}</a> · <a href="{b}memorandum/">{t['m_short']}</a> · <a href="{b}manifesto/">{MANI.get(lang, MANI['en'])}</a> · <a href="{b}record/">{RECORD.get(lang, RECORD['en'])}</a> · <a href="{b}statutes/">{t['s_short']}</a> · <a href="{b}fees/">{t['f_short']}</a> · <a href="{b}policies/">{t['foot_policies']}</a> · <a href="{b}policies/#disclaimer">{t['foot_disclaimer']}</a> · {MAIL} · {t['foot_track']}</div></footer>
{SCRIPT}
</body>
</html>
"""


def home(lang):
    t, b = T[lang], base(lang)
    pr = "\n".join(
        f'    <div class="card"><span class="num">{i}</span><h3>{h}</h3><p>{html.escape(p)}</p></div>'
        for i, (h, p) in enumerate(t["principles"], 1)
    )
    wk = "\n".join(f'    <div class="card"><h3>{h}</h3><p>{html.escape(p)}</p></div>' for h, p in t["work"])
    rows = "\n".join(f"    <tr><td><b>{a}</b></td><td>{w}</td><td>{r}</td></tr>" for a, w, r in t["rows"])
    th = "".join(f"<th>{x}</th>" for x in t["th"])
    return f"""{head(lang, t['title'], '')}
{header(lang, '')}

<main><div class="wrap">
<div class="hero">
  <p class="kicker">{t['kicker']}</p>
  <h1>{html.escape(t['h1'])}</h1>
  <p class="lead">{html.escape(t['lead1'])}</p>
  <p class="lead">{html.escape(t['lead2'])}</p>
  <a class="btn" href="{b}join/">{t['btn_join']}</a><a class="btn ghost" href="{b}charter/">{t['btn_charter']}</a>
</div>

<section id="open">
  <h2>{html.escape(OPEN[lang][0])}</h2>
  <p>{html.escape(OPEN[lang][1])}</p>
  <p>{html.escape(OPEN[lang][2])}</p>
  <p class="muted"><a href="{b}memorandum/">{html.escape(OPEN[lang][3])}</a></p>
</section>

<section id="why">
  <h2>{t['why_h']}</h2>
  <p class="muted">{html.escape(t['why'])}</p>
</section>

<section id="principles">
  <h2>{t['principles_h']}</h2>
  <div class="grid">
{pr}
  </div>
</section>

<section id="work">
  <h2>{t['work_h']}</h2>
  <div class="grid two">
{wk}
  </div>
</section>

<section id="join">
  <h2>{t['join_h']}</h2>
  <table>
    <tr>{th}</tr>
{rows}
  </table>
  <p style="margin-top:16px">{html.escape(t['join1'])}</p>
  <p><a class="btn" href="{b}join/">{t['btn_join']}</a></p>
  <p class="muted">{html.escape(t['join2']).replace('{mail}', MAIL)}</p>
  <div class="status"><b>{t['status_b']}</b> {html.escape(t['status'])}</div>
</section>

<section id="founding">
  <h2>{t['found_h']}</h2>
  <p>{html.escape(t['found_p'])}</p>
  <table>
    <tr><th>{t['found_th'][0]}</th><th>{t['found_th'][1]}</th></tr>
{"".join(f"    <tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td></tr>" for a, b in t['found_rows'])}
  </table>
  <p style="margin-top:16px">{html.escape(t['board'])}</p>
  <p class="muted">{html.escape(t['disclose'])}</p>
</section>

<section id="initiator">
  <h2>{t['init_h']}</h2>
  <p class="muted">{html.escape(t['init'])}</p>
</section>
</div></main>

{footer(lang)}"""


def charter(lang):
    t = T[lang]
    body = md(doc("charter", lang))
    note = f'<p class="status">{t["c_note"]} <a href="/charter/">English</a></p>\n' if t["c_note"] else ""
    comments = html.escape(t["c_comments"]).replace("{mail}", MAIL)
    return f"""{head(lang, t['c_title'], 'charter/')}
{header(lang, 'charter/')}

<main><div class="wrap doc">
{note}{body}
<p class="muted">{comments}</p>
</div></main>
{footer(lang)}"""


def policies(lang):
    t = T[lang]
    src = doc("policies", lang)
    titles = re.findall(r"\{#([a-z]+)\}\n## (.+)", src)
    toc = "".join(f'<li><a href="#{a}">{inline(h)}</a></li>' for a, h in titles)
    note = f' {t["c_note"]} <a href="/policies/">English</a>' if t["c_note"] else ""
    return f"""{head(lang, t['p_title'], 'policies/')}
{header(lang, 'policies/')}

<main><div class="wrap doc">
<h1>{t['p_title']}</h1>
<p class="status">{t['p_status']}{note}</p>
<ol>{toc}</ol>
{md(src)}
</div></main>
{footer(lang)}"""


def statutes(lang):
    t = T[lang]
    body = md(doc("statutes", lang))
    note = f' {t["c_note"]} <a href="/statutes/">English</a>' if t["c_note"] else ""
    return f"""{head(lang, t['s_title'], 'statutes/')}
{header(lang, 'statutes/')}

<main><div class="wrap doc">
<h1>{t['s_title']}</h1>
<p class="status">{t['s_status']}{note}</p>
{body}
</div></main>
{footer(lang)}"""


def memorandum(lang):
    t = T[lang]
    body = md(doc("memorandum", lang))
    note = f' {t["c_note"]} <a href="/memorandum/">English</a>' if t["c_note"] else ""
    return f"""{head(lang, t['m_title'], 'memorandum/')}
{header(lang, 'memorandum/')}

<main><div class="wrap doc">
<h1>{t['m_title']}</h1>
<p class="status">{t['m_status']}{note}</p>
{body}
</div></main>
{footer(lang)}"""


MANI = {"en": "Carried by its members", "de": "Getragen von seinen Mitgliedern", "fr": "Porté par ses membres",
        "it": "Sostenuto dai suoi membri", "es": "Sostenido por sus miembros", "ja": "会員が支える"}


RECORD = {"en": "Public record", "de": "Öffentliches Register", "fr": "Registre public",
          "it": "Registro pubblico", "es": "Registro público", "ja": "公開記録"}


def manifesto(lang, kind="manifesto", names=MANI):
    t = T[lang]
    body = md(doc(kind, lang))
    note = "" if lang in OLD else f'<p class="status">{t["c_note"]} <a href="/{kind}/">English</a></p>'
    return f"""{head(lang, names.get(lang, names['en']) + ' · OVAIC', f'{kind}/')}
{header(lang, f'{kind}/')}

<main><div class="wrap doc">
{note}
{body}
</div></main>
{footer(lang)}"""


def fees(lang):
    t = T[lang]
    body = md(doc("fees", lang))
    note = "" if lang == "en" else (f' <a href="/fees/">English</a>' if lang in OLD else f' {t["c_note"]} <a href="/fees/">English</a>')
    return f"""{head(lang, t['f_title'], 'fees/')}
{header(lang, 'fees/')}

<main><div class="wrap doc">
<h1>{t['f_title']}</h1>
<p class="status">{t['f_status']}{note}</p>
{body}
</div></main>
{footer(lang)}"""


def join(lang):
    t, b = T[lang], base(lang)
    E = lambda x: html.escape(x)

    def field(name, label, kind="text", req=True, area=False):
        r = " required" if req else ""
        lab = E(label) if req else f"{E(label)} <span class=\"muted\">({E(t['opt'])})</span>"
        inp = (f'<textarea name="{name}" rows="3"{r}></textarea>' if area
               else f'<input type="{kind}" name="{name}"{r}>')
        return f'<label>{lab}{inp}</label>'

    sizes = "".join(f'<option value="{i}">{E(x)}</option>' for i, x in enumerate(t["sizes"]))
    pays = "".join(f'<option value="{i}">{E(x)}</option>' for i, x in enumerate(t["pay"]))
    return f"""{head(lang, t['j_title'], 'join/')}
{header(lang, 'join/')}

<main><div class="wrap doc">
<h1>{E(t['j_title'])}</h1>
<p class="status ok-msg" hidden><b>{E(t['ok_title'])}.</b> {E(t['ok_text'])}</p>
<p class="status err-msg" hidden>{E(t['err_text'])}</p>
<p class="muted">{E(t['j_lead'])}</p>
<form class="apply" method="post" action="/apply.php">
<input type="hidden" name="lang" value="{lang}">
<input type="hidden" name="t0" value="">
<div class="hp" aria-hidden="true"><label>Leave empty<input type="text" name="website2" tabindex="-1" autocomplete="off"></label></div>
<fieldset><legend>{E(t['sec_org'])}</legend>
{field('org', t['f_org'])}{field('legal_form', t['f_legal'])}{field('country', t['f_country'])}{field('city', t['f_city'])}{field('uid', t['f_uid'], req=False)}{field('web', t['f_web'], 'url')}
</fieldset>
<fieldset><legend>{E(t['sec_rep'])}</legend>
{field('name', t['f_name'])}{field('role', t['f_role'])}{field('email', t['f_email'], 'email')}{field('phone', t['f_phone'], 'tel', req=False)}
</fieldset>
<fieldset><legend>{E(t['sec_mem'])}</legend>
<label>{E(t['f_cat'])}<select name="category" required><option value="member">{E(t['cat_member'])}</option><option value="observer">{E(t['cat_observer'])}</option></select></label>
<label>{E(t['f_size'])}<select name="size" required>{sizes}</select></label>
<p class="muted">{E(JOIN[lang])}</p>
<label class="check"><input type="checkbox" name="support" value="1"> {E(t['f_support'])}</label>
<label class="check"><input type="checkbox" name="reduce" value="1"> {E(t['f_reduce'])}</label>
</fieldset>
<fieldset><legend>{E(t['sec_decl'])}</legend>
{field('work', t['f_work'], area=True)}{field('products', t['f_products'], area=True)}{field('owners', t['f_owners'], area=True)}{field('relations', t['f_rel'], area=True)}{field('testcase', t['f_case'], req=False, area=True)}
<label>{E(t['f_pay'])} <span class="muted">({E(t['opt'])})</span><select name="pay"><option value=""></option>{pays}</select></label>
{field('note', t['f_note'], req=False, area=True)}
</fieldset>
<label class="check"><input type="checkbox" name="c_sanctions" value="1" required> {E(t['c_sanctions'])}</label>
<label class="check"><input type="checkbox" name="c_accept" value="1" required> {E(t['c_accept'])} <a href="{b}statutes/">{E(t['s_short'])}</a> · <a href="{b}charter/">{E(t['nav'][4])}</a> · <a href="{b}policies/">{E(t['foot_policies'])}</a> · <a href="{b}fees/">{E(t['f_short'])}</a></label>
<label class="check"><input type="checkbox" name="c_privacy" value="1" required> {E(t['c_privacy'])}</label>
<button class="btn" type="submit">{E(t['submit'])}</button>
</form>
<script>
document.querySelector('input[name=t0]').value=Date.now();
var q=location.search;if(q.indexOf('sent=1')>=0){{document.querySelector('.ok-msg').hidden=false;document.querySelector('form.apply').hidden=true;}}
if(q.indexOf('error=1')>=0)document.querySelector('.err-msg').hidden=false;
</script>
</div></main>
{footer(lang)}"""


def governance(lang):
    t, p, b = T[lang], P[lang], base(lang)
    E = html.escape
    org = lambda o: t["found_rows"][o][0] if isinstance(o, int) else o
    mrows = "".join(f"<tr><td>{E(org(o))}</td><td>{p['countries'][c]}</td><td>{FOUNDED[lang] if f else OCT[lang]}</td>"
                    f"<td>{p['founding'] if f else p['member']}</td></tr>" for o, c, f in MEMBERS)
    brows = "".join(f"<tr><td>{E(n)}</td><td>{p[r]}</td><td>{E(org(o))}</td></tr>" for n, r, o in BOARD)
    th = lambda xs: "<tr>" + "".join(f"<th>{x}</th>" for x in xs) + "</tr>"
    rel = re.split(r"[:：]\s*", t["disclose"], maxsplit=1)[1]  # drop the "Disclosed relationships:" label, the heading says it
    ul = lambda xs: "<ul>" + "".join(f"<li>{E(x)}</li>" for x in xs) + "</ul>"
    return f"""{head(lang, p['title'], 'governance/')}
{header(lang, 'governance/')}

<main><div class="wrap doc">
<h1>{E(p['title'])}</h1>
<p class="lead">{E(p['lead'])}</p>
<h2 id="members">{p['m_h']}</h2>
<p>{E(p['m_lead'])}</p>
<table>{th(p['m_th'])}{mrows}</table>
<p>{E(p['m_join'])} <a href="{b}join/">{t['btn_join']}</a></p>
<h2 id="board">{p['b_h']}</h2>
<p>{E(p['b_lead'])}</p>
<table>{th(p['b_th'])}{brows}</table>
<p class="muted">{E(p['secretary'])} <a href="{b}manifesto/">{MANI.get(lang, MANI['en'])}</a></p>
<h2 id="decisions">{p['d_h']}</h2>
{ul(p['d'])}
<h2 id="relationships">{p['r_h']}</h2>
<p>{E(rel)}</p>
<h2 id="money">{p['f_h']}</h2>
{ul(p['f'])}
<p><a href="{b}fees/">{t['f_short']}</a></p>
<h2 id="openness">{p['o_h']}</h2>
{ul(p['o'])}
<p class="status">{E(p['status'])}</p>
</div></main>
{footer(lang)}"""


def main():
    for lang in LANGS:
        out = ROOT if lang == "en" else ROOT / lang
        (out / "charter").mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(home(lang))
        (out / "charter" / "index.html").write_text(charter(lang))
        (out / "policies").mkdir(exist_ok=True)
        (out / "policies" / "index.html").write_text(policies(lang))
        (out / "statutes").mkdir(exist_ok=True)
        (out / "statutes" / "index.html").write_text(statutes(lang))
        (out / "memorandum").mkdir(exist_ok=True)
        (out / "memorandum" / "index.html").write_text(memorandum(lang))
        (out / "manifesto").mkdir(exist_ok=True)
        (out / "manifesto" / "index.html").write_text(manifesto(lang))
        (out / "record").mkdir(exist_ok=True)
        (out / "record" / "index.html").write_text(manifesto(lang, "record", RECORD))
        (out / "fees").mkdir(exist_ok=True)
        (out / "fees" / "index.html").write_text(fees(lang))
        (out / "join").mkdir(exist_ok=True)
        (out / "join" / "index.html").write_text(join(lang))
        (out / "governance").mkdir(exist_ok=True)
        (out / "governance" / "index.html").write_text(governance(lang))
    print("built", ", ".join(LANGS))


if __name__ == "__main__":
    main()
