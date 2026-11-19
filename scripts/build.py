# -*- coding: utf-8 -*-
"""工序查查站构建：从 site_data.py 渲染全部页面到仓库根（仓库根＝站点根，CF Pages 直发）。
改内容只改 site_data.py，然后跑：python3 scripts/build.py"""
import json, os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_data import SITE, PROCESSES, QA_PAGES, CALC_RATES, CALC_TONNAGE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = SITE["domain"]
GSC = "G97sFvVAFn4qMJCTupV0JXGVb_nc5mUWkDNsn0YLFvk"
BING = "9B4026C98FB641D53056F9D959BE029E"
GA_ID = "G-36PLK4JM29"
GA_SNIPPET = """<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=__GA_ID__"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', '__GA_ID__');
</script>
""".replace("__GA_ID__", GA_ID)

def head(title, desc, url, extra=""):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="{GSC}" />
<meta name="msvalidate.01" content="{BING}" />
{GA_SNIPPET}<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="工序查查站">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{D}/og.png">
<link rel="stylesheet" href="/assets/style.css">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{extra}</head>"""

def header():
    return """<header class="site-header"><div class="in">
<a class="brand" href="/">工序查查站<small>机加工工序库 · 加工费参考</small></a>
<nav><a href="/">工序库</a><a href="/calculator/">加工费计算器</a><a href="/wenda/baojia-jisuan-fangfa/">报价计算方法</a><a href="/about/">关于本站</a></nav>
</div></header>"""

def footer():
    return f"""<footer><div class="in">
<p>工序查查站 — 机加工工序与加工费参考。{SITE['data_note']}</p>
<p><a href="/">工序库</a> · <a href="/calculator/">加工费计算器</a> · <a href="/about/">关于本站</a> · <a href="https://gxccz.com/">gxccz 工具导航</a></p>
<p>友情链接：<a href="https://www.shtezheng.com">特正包装</a> · <a href="https://esxiaomiao.com">小苗科技</a></p>
<p>© 2026 gxccz.com · 站长QQ：65363885 · 联系邮箱 <a href="mailto:kefu@gxccz.com">kefu@gxccz.com</a> · <a href="https://gxccz.com/privacy/">隐私与条款</a></p>
</div></footer>
</body></html>"""

def table(rows):
    out = ["<table>"]
    for i, r in enumerate(rows):
        tag = "th" if i == 0 else "td"
        out.append("<tr>" + "".join(f"<{tag}>{html.escape(c)}</{tag}>" for c in r) + "</tr>")
    out.append("</table>")
    return "\n".join(out)

def sections_html(sections):
    out = []
    for h, paras in sections:
        out.append(f"<h2>{html.escape(h)}</h2>")
        for p in paras:
            out.append(f"<p>{html.escape(p)}</p>")
    return "\n".join(out)

def more_html(more):
    if not more:
        return ""
    items = "".join(f'<li><a href="{html.escape(u)}">{html.escape(t)}</a></li>' for t, u in more)
    return f"<h2>相关阅读</h2>\n<ul>{items}</ul>"

def faq_html(faqs):
    items = "".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q, a in faqs)
    return f'<h2>常见问题</h2><div class="faq">{items}</div>'

def faq_ld(faqs):
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q,
                          "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    return f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n'

def crumb_ld(items):
    # Google 要求 BreadcrumbList 的每个 ListItem 都带 item（URL），缺了就报
    # “未填写字段 item”结构化数据问题。中间层级（工序分类/热门问答）没有独立
    # 落地页，编不出真实 URL，所以直接从 JSON-LD 里去掉这一级（只保留有 URL
    # 的首页和当前页），不要发无 item 的 ListItem。页面上可见的面包屑文字不动。
    els = []
    for name, u in items:
        if not u:
            continue
        els.append({"@type": "ListItem", "position": len(els) + 1, "name": name, "item": u})
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": els}
    return f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n'

def write(path, content):
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)

URLS = [("/", "工序查查站 - 机加工工序库与加工费计算器", "1.0")]

# ---------- 工序页 ----------
for p in PROCESSES:
    url = f"{D}/gongxu/{p['slug']}/"
    title = f"{p['kw']} - 工序查查站"
    desc = p["lead"][:110]
    related = [q for q in PROCESSES if q["cat"] == p["cat"] and q["slug"] != p["slug"]][:3]
    rel = "".join(f'<li><a href="/gongxu/{q["slug"]}/">{html.escape(q["name"])}：{html.escape(q["kw"])}</a></li>' for q in related)
    body = f"""{head(title, desc, url, faq_ld(p['faq']) + crumb_ld([("工序库", D + "/"), (p['cat'], None), (p['name'], url)]))}
<body>
{header()}
<main>
<p class="crumb"><a href="/">工序库</a> / {html.escape(p['cat'])} / {html.escape(p['name'])}</p>
<h1>{html.escape(p['kw'])}</h1>
<p class="lede">{html.escape(p['lead'])}</p>
<h2>{html.escape(p['name'])}是什么</h2>
<p>{html.escape(p['what'])}</p>
<h2>计价方式与参考区间</h2>
<p>{html.escape(p['pricing'])}</p>
{table(p['rates'])}
<div class="note">{SITE['data_note']}</div>
<p class="meta">本页数据核验日期：{SITE['verified']}</p>
<h2>影响价格的因素</h2>
<ul>{''.join(f'<li>{html.escape(x)}</li>' for x in p['factors'])}</ul>{more_html(p.get('more', []))}
{faq_html(p['faq'])}
<h2>相关工序</h2>
<ul>{rel}<li><a href="/calculator/">加工费计算器：按费率×工时快速估价</a></li></ul>
</main>
{footer()}"""
    write(f"gongxu/{p['slug']}/index.html", body)
    URLS.append((f"/gongxu/{p['slug']}/", p["kw"], "0.8"))

# ---------- 问答页 ----------
for q in QA_PAGES:
    url = f"{D}/wenda/{q['slug']}/"
    qa_extra = sections_html(q.get('sections', []))
    if q.get('more'):
        qa_extra += ("\n" if qa_extra else "") + more_html(q.get('more', []))
    if qa_extra:
        qa_extra = "\n" + qa_extra
    title = f"{q['kw']} - 工序查查站"
    desc = q["lead"][:110]
    body = f"""{head(title, desc, url, faq_ld(q['faq']) + crumb_ld([("工序库", D + "/"), ("热门问答", None), (q['name'], url)]))}
<body>
{header()}
<main>
<p class="crumb"><a href="/">工序库</a> / 热门问答 / {html.escape(q['name'])}</p>
<h1>{html.escape(q['kw'])}</h1>
<p class="lede">{html.escape(q['lead'])}</p>
<p>{html.escape(q['body'])}</p>
{table(q['rates'])}{qa_extra}
<div class="note">{SITE['data_note']}</div>
<p class="meta">本页数据核验日期：{SITE['verified']}</p>
{faq_html(q['faq'])}
<p><a href="/calculator/">→ 用加工费计算器按你的参数算一遍</a></p>
</main>
{footer()}"""
    write(f"wenda/{q['slug']}/index.html", body)
    URLS.append((f"/wenda/{q['slug']}/", q["kw"], "0.8"))

# ---------- 计算器页 ----------
calc_ld = {"@context": "https://schema.org", "@type": "WebApplication",
           "name": "加工费计算器 - 工序查查站", "url": f"{D}/calculator/",
           "applicationCategory": "BusinessApplication", "operatingSystem": "Web",
           "browserRequirements": "Requires JavaScript",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "CNY"},
           "description": "在线估算机加工费用：通用机加工（机时费率×工时）、线切割（面积法）、激光切割（按米）、注塑（吨位工缴费）四个模块，结果均为参考区间。"}
rates_js = json.dumps([{"name": n, "lo": lo, "hi": hi} for n, lo, hi in CALC_RATES], ensure_ascii=False)
ton_js = json.dumps([{"name": n, "lo": lo, "hi": hi} for n, lo, hi in CALC_TONNAGE], ensure_ascii=False)
calc = head("加工费计算器（CNC/线切割/激光切割/注塑）- 工序查查站",
            "在线估算机加工费用：按机时费率×工时估 CNC 与常规切削，线切割面积法、激光切割按米、注塑吨位工缴费四个模块，结果均为参考区间。",
            f"{D}/calculator/",
            '<style>.copybtn{margin-top:10px;border:1px solid var(--line);background:#fff;border-radius:8px;padding:7px 14px;font-size:14px;cursor:pointer}.copybtn:hover{border-color:var(--accent);color:var(--accent)}.err{color:#b3261e;font-weight:600}#toast{position:fixed;left:50%;bottom:28px;transform:translateX(-50%);background:#222;color:#fff;padding:9px 18px;border-radius:999px;font-size:14px;opacity:0;pointer-events:none;transition:opacity .25s;z-index:50}#toast.show{opacity:1}</style>\n'
            + f'<script type="application/ld+json">{json.dumps(calc_ld, ensure_ascii=False)}</script>\n')
calc += """
<body>
""" + header() + """
<main>
<p class="crumb"><a href="/">工序库</a> / 加工费计算器</p>
<h1>加工费计算器</h1>
<p class="lede">四个常用估算模块：通用机加工（费率×工时）、线切割（面积法）、激光切割（按米）、注塑（吨位工缴费）。全部按参考区间出数——实际价格以厂家按图报价为准。</p>
<div class="tabs">
<button class="on" data-t="gen">通用机加工</button>
<button data-t="wire">线切割</button>
<button data-t="laser">激光切割</button>
<button data-t="inj">注塑</button>
</div>

<div class="calc pane on" id="pane-gen">
<div class="row"><div><label>设备类型（费率区间内置）</label><select id="g-dev"></select></div>
<div><label>单件工时（分钟）</label><input id="g-min" type="number" value="30" min="0"></div></div>
<div class="row"><div><label>材料费（元/件，可空）</label><input id="g-mat" type="number" value="0" min="0"></div>
<div><label>数量（件）</label><input id="g-qty" type="number" value="10" min="1"></div></div>
<div class="out" id="g-out"></div>
<button type="button" class="copybtn" data-m="gen">复制结果链接</button>
<p class="meta">公式：单件加工费＝机时费率（元/小时）×工时（分钟）÷60；区间由费率上下限分别计算。费率口径见各工序页。</p>
</div>

<div class="calc pane" id="pane-wire">
<div class="row"><div><label>切割轨迹总长（mm）</label><input id="w-len" type="number" value="500" min="0"></div>
<div><label>材料厚度（mm）</label><input id="w-th" type="number" value="20" min="0"></div></div>
<div class="out" id="w-out"></div>
<button type="button" class="copybtn" data-m="wire">复制结果链接</button>
<p class="meta">公式：截面面积＝轨迹长×厚度；费用≈（面积÷1200）×5 元（快走丝流传口径）。慢走丝与多次切割请按工时法，见慢走丝页。</p>
</div>

<div class="calc pane" id="pane-laser">
<div class="row"><div><label>板厚（mm）</label><input id="l-th" type="number" value="3" min="0" step="0.5"></div>
<div><label>材质</label><select id="l-mat"><option value="1.5">碳钢（×1.5）</option><option value="3.75">不锈钢（约×2.5）</option><option value="6">铝板（约×4）</option></select></div></div>
<div class="row"><div><label>切割总长度（米）</label><input id="l-len" type="number" value="10" min="0"></div>
<div><label>穿孔数（个，穿孔费按 1 元/个估）</label><input id="l-hole" type="number" value="20" min="0"></div></div>
<div class="out" id="l-out"></div>
<button type="button" class="copybtn" data-m="laser">复制结果链接</button>
<p class="meta">公式：每米价＝板厚×材质系数；总价＝每米价×总长＋穿孔费。材质系数（碳钢×1.5、不锈钢约×2.5、铝约×4）为业内流传经验口径，2026 年 11 月据公开报价资料整理，实际以厂家报价为准。小单有最低消费。</p>
</div>

<div class="calc pane" id="pane-inj">
<div class="row"><div><label>机台吨位</label><select id="i-ton"></select></div>
<div><label>成型周期（秒）</label><input id="i-cyc" type="number" value="30" min="1"></div></div>
<div class="row"><div><label>模穴数</label><input id="i-cav" type="number" value="2" min="1"></div>
<div><label>原料费（元/件，可空）</label><input id="i-mat" type="number" value="0" min="0"></div></div>
<div class="out" id="i-out"></div>
<button type="button" class="copybtn" data-m="inj">复制结果链接</button>
<p class="meta">公式：单件工缴费＝机台费率×周期÷3600÷穴数。此处不含模具费（开模单独计）。</p>
</div>

<div class="note">计算结果为参考估算，实际以厂家报价为准。费率区间为 2026 年 11 月据公开报价资料多源交叉整理，地区、设备新旧、批量差异很大。</div>
<h2>算之前先看</h2>
<ul>
<li><a href="/wenda/baojia-jisuan-fangfa/">机械加工报价计算方法：材料＋工时＋费率的完整构成</a></li>
<li><a href="/gongxu/gongshi-dinge/">机加工工时定额怎么算：工时构成别漏宽放与准备时间</a></li>
<li><a href="/wenda/cnc-yige-lingjian-duoshao/">CNC 加工一个零件多少钱：为什么批量决定单价</a></li>
</ul>
<div id="toast" role="status"></div>
</main>
""" + footer()
calc += """
<script>
var RATES=__RATES__, TONS=__TONS__;
function $(i){return document.getElementById(i)}
function money(x){return (Math.round(x*10)/10).toLocaleString('zh-CN')}
var gd=$('g-dev'); RATES.forEach(function(r,i){var o=document.createElement('option');o.value=i;o.textContent=r.name+'（'+r.lo+'–'+r.hi+' 元/时）';gd.appendChild(o)});
var it=$('i-ton'); TONS.forEach(function(r,i){var o=document.createElement('option');o.value=i;o.textContent=r.name+'（'+r.lo+'–'+r.hi+' 元/时）';it.appendChild(o)});
// 取值校验：req=必填正数（带上限），opt=可空非负数（空按 0）；非法一律返回 NaN，由各模块给出提示
function req(id,max){var v=$(id).value.trim(); if(v==='')return NaN; var n=Number(v); if(!isFinite(n)||n<=0||n>(max||1000000))return NaN; return n}
function opt(id,max){var v=$(id).value.trim(); if(v==='')return 0; var n=Number(v); if(!isFinite(n)||n<0||n>(max||100000000))return NaN; return n}
function err(out,msg){$(out).innerHTML='<span class="err">'+msg+'</span>'}
function gen(){var r=RATES[+gd.value],m=req('g-min',100000),mat=opt('g-mat'),q=req('g-qty',1000000);
 if(isNaN(m))return err('g-out','请先填写有效的单件工时（分钟，需大于 0）');
 if(isNaN(q)||Math.floor(q)!==q)return err('g-out','请先填写有效的数量（件，正整数）');
 if(isNaN(mat))return err('g-out','材料费请填写 0 或正数（可留空按 0 算）');
 var lo=r.lo*m/60+mat, hi=r.hi*m/60+mat;
 $('g-out').innerHTML='单件参考：<b>'+money(lo)+' – '+money(hi)+' 元</b>（其中加工费 '+money(r.lo*m/60)+' – '+money(r.hi*m/60)+' 元）<br>共 '+q+' 件合计约：<b>'+money(lo*q)+' – '+money(hi*q)+' 元</b>';}
function wire(){var len=req('w-len'),th=req('w-th');
 if(isNaN(len))return err('w-out','请先填写有效的切割轨迹总长（mm，需大于 0）');
 if(isNaN(th))return err('w-out','请先填写有效的材料厚度（mm，需大于 0）');
 var a=len*th, fee=a/1200*5;
 $('w-out').innerHTML='截面面积 '+money(a)+' mm²，按面积法参考加工费约 <b>'+money(fee)+' 元</b>（小单多有 30–50 元最低消费）';}
function laser(){var th=req('l-th',1000),k=+$('l-mat').value,len=req('l-len',100000),h=opt('l-hole',1000000);
 if(isNaN(th))return err('l-out','请先填写有效的板厚（mm，需大于 0）');
 if(isNaN(len))return err('l-out','请先填写有效的切割总长度（米，需大于 0）');
 if(isNaN(h))return err('l-out','穿孔数请填写 0 或正数（没有穿孔填 0）');
 var per=th*k, tot=per*len+h*1;
 $('l-out').innerHTML='每米参考价约 <b>'+money(per)+' 元/米</b>，总价约 <b>'+money(tot)+' 元</b>（含穿孔费估 '+money(h)+' 元）';}
function inj(){var r=TONS[+it.value],cyc=req('i-cyc',36000),cav=req('i-cav',1000),mat=opt('i-mat');
 if(isNaN(cyc))return err('i-out','请先填写有效的成型周期（秒，需大于 0）');
 if(isNaN(cav)||Math.floor(cav)!==cav)return err('i-out','请先填写有效的模穴数（正整数）');
 if(isNaN(mat))return err('i-out','原料费请填写 0 或正数（可留空按 0 算）');
 var lo=r.lo*cyc/3600/cav+mat, hi=r.hi*cyc/3600/cav+mat;
 $('i-out').innerHTML='单件参考：<b>'+money(lo)+' – '+money(hi)+' 元</b>（工缴费 '+money(r.lo*cyc/3600/cav)+' – '+money(r.hi*cyc/3600/cav)+' 元，不含模具费）';}
var FIELDS={gen:['g-dev','g-min','g-mat','g-qty'],wire:['w-len','w-th'],laser:['l-th','l-mat','l-len','l-hole'],inj:['i-ton','i-cyc','i-cav','i-mat']};
['g-dev','g-min','g-mat','g-qty'].forEach(function(i){document.getElementById(i).addEventListener('input',gen)});
['w-len','w-th'].forEach(function(i){document.getElementById(i).addEventListener('input',wire)});
['l-th','l-mat','l-len','l-hole'].forEach(function(i){document.getElementById(i).addEventListener('input',laser)});
['i-ton','i-cyc','i-cav','i-mat'].forEach(function(i){document.getElementById(i).addEventListener('input',inj)});
document.querySelectorAll('.tabs button').forEach(function(b){b.addEventListener('click',function(){
 document.querySelectorAll('.tabs button').forEach(function(x){x.classList.remove('on')}); b.classList.add('on');
 document.querySelectorAll('.pane').forEach(function(x){x.classList.remove('on')});
 document.getElementById('pane-'+b.dataset.t).classList.add('on');});});
// 带参数打开：还原各模块输入，并切到 t 指定的模块；末尾统一重算，结果即出
(function(){var qs=new URLSearchParams(location.search);
 Object.keys(FIELDS).forEach(function(mod){FIELDS[mod].forEach(function(id){var v=qs.get(id); if(v===null)return; var el=$(id);
  if(el.tagName==='SELECT'){for(var j=0;j<el.options.length;j++){if(el.options[j].value===v){el.value=v;break}}} else {el.value=v}})});
 var t=qs.get('t'); if(t&&FIELDS[t]){document.querySelectorAll('.tabs button').forEach(function(b){if(b.dataset.t===t)b.click()});}
})();
// 复制结果链接：把该模块全部输入编码进 URL，打开即还原同组输入与结果
function toast(msg){var t=$('toast'); t.textContent=msg; t.classList.add('show'); setTimeout(function(){t.classList.remove('show')},1800)}
document.querySelectorAll('.copybtn').forEach(function(b){b.addEventListener('click',function(){
 var mod=b.dataset.m, parts=['t='+mod];
 FIELDS[mod].forEach(function(id){parts.push(id+'='+encodeURIComponent($(id).value))});
 var url=location.origin+location.pathname+'?'+parts.join('&');
 function done(){toast('结果链接已复制，发给同事打开即是这个结果')}
 function fallback(){var ta=document.createElement('textarea'); ta.value=url; document.body.appendChild(ta); ta.select(); try{document.execCommand('copy'); done()}catch(e){toast('复制失败，请手动复制地址栏链接')} document.body.removeChild(ta)}
 if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(url).then(done,fallback)}else{fallback()}
})});
gen(); wire(); laser(); inj();
</script>
</body></html>"""
calc = calc.replace("__RATES__", rates_js).replace("__TONS__", ton_js)
write("calculator/index.html", calc)
URLS.append(("/calculator/", "加工费计算器", "0.9"))

# ---------- 首页 ----------
cats = []
seen = []
for p in PROCESSES:
    if p["cat"] not in seen:
        seen.append(p["cat"])
for c in seen:
    cards = "".join(f'<a class="card" href="/gongxu/{p["slug"]}/"><b>{html.escape(p["name"])}</b><span>{html.escape(p["kw"])}</span></a>'
                    for p in PROCESSES if p["cat"] == c)
    cats.append(f'<h2>{html.escape(c)}</h2><div class="grid">{cards}</div>')
qa_cards = "".join(f'<a class="card" href="/wenda/{q["slug"]}/"><b>{html.escape(q["name"])}</b><span>{html.escape(q["kw"])}</span></a>' for q in QA_PAGES)
home_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "工序查查站", "url": D + "/",
           "description": "机加工工序库与加工费计算器：单工序加工费怎么算、机时费率参考区间、工时定额构成。"}
home = head("工序查查站 - 机加工工序库｜加工费怎么算｜机时费率参考",
            "机加工每道工序的加工费怎么算：线切割、激光切割、折弯、注塑、钻孔、攻丝等工序的计价公式、参考费率区间与在线计算器。",
            D + "/", f'<script type="application/ld+json">{json.dumps(home_ld, ensure_ascii=False)}</script>\n')
home += f"""
<body>
{header()}
<main>
<h1>机加工工序库：每道工序的加工费怎么算</h1>
<p class="lede">工序查查站只做一件事：把机加工每道工序的计价方式讲清——用什么公式、机时费率大概多少、哪些因素让价格翻倍。所有费率只给参考区间并标注口径，不编造统一标准价。</p>
<p><a class="cta" href="/calculator/">打开加工费计算器（费率×工时 / 线切割面积法 / 激光按米 / 注塑吨位）</a></p>
<h2>能查什么</h2>
<p>本站收录机加工常用工序的计价方式，每道工序一页：用什么公式算（机时费率×工时、按切割面积、按米、按件等）、参考费率区间是多少、哪些因素会让价格上下浮动（材料、厚度、批量、精度要求等）。拿着自己的参数，还可以用加工费计算器当场估一遍四个常用场景：通用机加工、线切割、激光切割、注塑。</p>
<h2>数据口径</h2>
<p>本站所有费率与工时都是<strong>参考区间</strong>，来自 2026 年 11 月对公开报价资料的多源交叉整理，不是任何一家厂家的报价，更不是统一标准价——机加工本来就没有全国统一价。地区、设备新旧、订单批量都会让实际价格偏离区间，正式下单请以厂家按图报价为准。</p>
{''.join(cats)}
<h2>热门问答</h2>
<div class="grid">{qa_cards}</div>
<div class="note">{SITE['data_note']}</div>
</main>
{footer()}"""
write("index.html", home)

# ---------- 关于页 ----------
FB_SCRIPT = """
<script>
(function(){
var form=document.getElementById('fb-form');
if(!form)return;
form.addEventListener('submit',function(ev){
ev.preventDefault();
var st=document.getElementById('fb-status');
var email=document.getElementById('fb-email').value.trim();
var topic=document.getElementById('fb-topic').value.trim();
var msg=document.getElementById('fb-msg').value.trim();
if(!email||!msg){st.textContent='请填写邮箱和反馈内容。';return;}
var note=(topic?('主题='+topic+' | '):'')+'内容='+msg;
st.textContent='提交中...';
fetch('https://lunasign.me/api/leads',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({site:'gxccz',email:email,source:'feedback',note:note.slice(0,480),hp:document.getElementById('fb-hp').value})})
.then(function(r){return r.json();})
.then(function(d){if(d&&d.ok){st.textContent='已收到，谢谢反馈。如需回复，我们会通过邮箱联系你。';form.reset();}else{st.textContent='提交失败，请稍后再试。';}})
.catch(function(){st.textContent='提交失败，请稍后再试。';});
});
})();
</script>
"""
about = head("关于本站 - 工序查查站", "工序查查站：机加工工序与加工费参考站，数据口径与联系说明。",
             f"{D}/about/",
             '<style>#fb-form{max-width:560px}#fb-form label{display:block;margin:12px 0 4px;font-size:14px}#fb-form input,#fb-form textarea{width:100%;padding:9px 10px;font-size:15px;border:1px solid var(--line);border-radius:8px;font-family:inherit;background:#fff}#fb-hp{display:none!important}#fb-form button{margin-top:14px;background:var(--accent);color:#fff;border:0;border-radius:8px;padding:10px 22px;font-size:15px;cursor:pointer}</style>\n')
about += f"""
<body>
{header()}
<main>
<h1>关于工序查查站</h1>
<p>工序查查站（gxccz.cn）是一个机加工信息参考站，v1 只做机加工：工序库（每道工序一页：是什么、计价方式、参考费率区间、影响价格的因素）＋工时/机时费率计算器。</p>
<h2>数据口径</h2>
<p>{SITE['data_note']}每道工序页都标注了计价口径与公式来源类型（行业流传公式、公开报价资料整理等）。本站不提供报价服务，不对任何按本站数据达成的交易负责。</p>
<h2>反馈与联系</h2>
<p>数据勘误、工序补充建议，或对本站的意见，都可以通过下面的表单告诉我们。邮箱只用于回复你的反馈，不作他用。</p>
<form id="fb-form" method="post" action="#">
<label for="fb-email">你的邮箱（用于回复）</label>
<input id="fb-email" name="email" type="email" required placeholder="you@example.com">
<label for="fb-topic">相关工序或主题（可空）</label>
<input id="fb-topic" name="topic" type="text" placeholder="如：线切割">
<label for="fb-msg">反馈内容</label>
<textarea id="fb-msg" name="message" rows="5" required placeholder="写下你的勘误、建议或问题"></textarea>
<input type="text" name="hp" id="fb-hp" autocomplete="off" tabindex="-1" aria-hidden="true">
<button type="submit">提交反馈</button>
<p class="meta" id="fb-status" role="status"></p>
</form>
</main>
""" + FB_SCRIPT + footer()
write("about/index.html", about)
URLS.append(("/about/", "关于本站", "0.3"))

# ---------- 404 / robots / sitemap / llms ----------
write("404.html", head("页面不存在 - 工序查查站", "页面不存在", D + "/404.html") + f"""
<body>{header()}<main><h1>页面不存在</h1><p>回到<a href="/">工序库首页</a>，或打开<a href="/calculator/">加工费计算器</a>。</p></main>{footer()}""")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {D}/sitemap.xml\n")
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path, _t, pri in URLS:
    sm.append(f"<url><loc>{D}{path}</loc><priority>{pri}</priority></url>")
sm.append("</urlset>")
write("sitemap.xml", "\n".join(sm) + "\n")
llms = ["# 工序查查站（gxccz.cn）", "",
        "机加工工序与加工费参考站：每道工序的计价公式、参考费率区间、影响因素与在线计算器。费率均为参考区间，非统一标准价。", "",
        "## 主要页面", f"- 首页/工序库: {D}/", f"- 加工费计算器: {D}/calculator/", ""]
llms.append("## 工序页")
for p in PROCESSES:
    llms.append(f"- {p['name']}（{p['kw']}）: {D}/gongxu/{p['slug']}/")
llms.append("")
llms.append("## 问答页")
for q in QA_PAGES:
    llms.append(f"- {q['name']}（{q['kw']}）: {D}/wenda/{q['slug']}/")
write("llms.txt", "\n".join(llms) + "\n")
print("TOTAL URLS:", len(URLS))
