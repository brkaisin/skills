#!/usr/bin/env python3
"""Build printable wine tasting sheets (one A4 landscape page per wine) as HTML.

Usage:
  python3 build_sheets.py DATA.json --out sheets.html [--theme color|print] [--lang fr] [--geo countries.geojson]

Standard library only. The country outlines come from Natural Earth (public domain).
If --geo is not given, the file is downloaded once into a cache folder.
Turn the HTML into a PDF with render_pdf.py, or open it in a browser and print it.
"""
import argparse, html, json, math, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEO_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson"
GEO_CACHE = os.path.join(os.path.expanduser("~"), ".cache", "wine-tasting-sheets", "ne_50m_admin_0_countries.geojson")

# ---------------------------------------------------------------- strings
STRINGS = {
    "fr": dict(sheet="Fiche de dégustation · Vin", story="L’histoire", technique="La technique", tasting="La dégustation",
               profile="Le profil", table="À table", avoid="À éviter :", know="Le saviez-vous ?", sources="Sources :",
               indicative="Profil indicatif.", eye="L’œil", nose="Le nez", palate="La bouche", finish="La finale"),
    "en": dict(sheet="Tasting sheet · Wine", story="The story", technique="The winemaking", tasting="Tasting notes",
               profile="Profile", table="At the table", avoid="Avoid:", know="Did you know?", sources="Sources:",
               indicative="Indicative profile.", eye="Eye", nose="Nose", palate="Palate", finish="Finish"),
    "nl": dict(sheet="Proefnotitie · Wijn", story="Het verhaal", technique="De techniek", tasting="De proeverij",
               profile="Profiel", table="Aan tafel", avoid="Te vermijden:", know="Wist je dat?", sources="Bronnen:",
               indicative="Indicatief profiel.", eye="Kleur", nose="Neus", palate="Smaak", finish="Afdronk"),
    "es": dict(sheet="Ficha de cata · Vino", story="La historia", technique="La técnica", tasting="La cata",
               profile="El perfil", table="En la mesa", avoid="Evitar:", know="¿Sabías que…?", sources="Fuentes:",
               indicative="Perfil orientativo.", eye="Vista", nose="Nariz", palate="Boca", finish="Final"),
    "de": dict(sheet="Verkostungsblatt · Wein", story="Die Geschichte", technique="Die Technik", tasting="Die Verkostung",
               profile="Das Profil", table="Zu Tisch", avoid="Zu meiden:", know="Schon gewusst?", sources="Quellen:",
               indicative="Richtwerte.", eye="Auge", nose="Nase", palate="Gaumen", finish="Abgang"),
    "it": dict(sheet="Scheda di degustazione · Vino", story="La storia", technique="La tecnica", tasting="La degustazione",
               profile="Il profilo", table="A tavola", avoid="Da evitare:", know="Lo sapevi?", sources="Fonti:",
               indicative="Profilo indicativo.", eye="Vista", nose="Naso", palate="Bocca", finish="Finale"),
}

# Side-panel palettes per wine colour, for the "color" theme. The "print" theme ignores them.
PANELS = {
    "white":     dict(panel="#F2E6C8", ink="#2A181C", soft="#5B4649", accent="#7E2236", land="#FBF6EA", other="#E6D6AE", stroke="#B88A3E", dot="#7E2236", sea="#EADBB6"),
    "red":       dict(panel="#4E1825", ink="#F6EDE3", soft="#E3CFC4", accent="#E8C27E", land="#6E2638", other="#5F1E2E", stroke="#E8C27E", dot="#F2CF8A", sea="#46141F"),
    "rose":      dict(panel="#F3D9D2", ink="#2A181C", soft="#5B4649", accent="#9C2F45", land="#FCF1EE", other="#E9C6BD", stroke="#C0707E", dot="#9C2F45", sea="#EBCFC7"),
    "orange":    dict(panel="#EFD2A8", ink="#2A181C", soft="#5B4649", accent="#8A3B12", land="#FBF2E4", other="#E3C192", stroke="#B8752E", dot="#8A3B12", sea="#E6C99C"),
    "sparkling": dict(panel="#ECE7D6", ink="#2A181C", soft="#5B4649", accent="#6E5A1E", land="#FBF9F1", other="#DDD5BC", stroke="#A88E3E", dot="#7E2236", sea="#E2DBC5"),
    "sweet":     dict(panel="#F0D9A0", ink="#2A181C", soft="#5B4649", accent="#7A4A0E", land="#FCF4DE", other="#E3C682", stroke="#B88A3E", dot="#7E2236", sea="#E8CE90"),
}
PRINT_PANEL = dict(panel="#FFFFFF", ink="#1E1E1E", soft="#555555", accent="#7E2236", land="#FFFFFF", other="#F1F1F1", stroke="#333333", dot="#7E2236", sea="#FFFFFF")

# ---------------------------------------------------------------- typography helpers
NB, NNB = " ", " "

def esc(text, lang):
    t = str(text)
    if lang == "fr":
        t = t.replace("« ", "«" + NB).replace(" »", NB + "»")
        t = re.sub(r" ([:;?!])", NNB + r"\1", t)
    t = re.sub(r"(\d) (?=\d{3}\b)", r"\1" + NB, t)
    t = re.sub(r"(\d) (%|°C|°F|ha|hl|mm|cm|m|km|g/l|g/L|h)\b", r"\1" + NB + r"\2", t)
    t = t.replace(" %", NB + "%").replace(" °C", NB + "°C")
    return html.escape(t)

# ---------------------------------------------------------------- geography
def load_geo(path):
    if not path:
        path = GEO_CACHE
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            print(f"Downloading country outlines (Natural Earth, ~3 MB) to {path}", file=sys.stderr)
            urllib.request.urlretrieve(GEO_URL, path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out = {}
    for feat in data["features"]:
        p = feat["properties"]
        codes = {p.get("ADM0_A3"), p.get("ISO_A3"), p.get("SOV_A3"), p.get("ADM0_ISO")}
        g = feat["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for c in codes:
            if c and c != "-99" and c not in out:
                out[c] = polys
    return out

def bbox_of(rings):
    xs = [x for r in rings for x, _ in r]
    ys = [y for r in rings for _, y in r]
    return min(xs), max(xs), min(ys), max(ys)

def point_in_ring(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]; xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside

def view_box(polys, lon, lat):
    """Frame the mainland and its nearby islands; frame far-off islands (Canaries, Madeira...) on their own."""
    def area(poly):
        a, b, c, d = bbox_of([poly[0]])
        return (b - a) * (d - c)
    def group(main):
        x0, x1, y0, y1 = bbox_of([main[0]])
        w, h = x1 - x0, y1 - y0
        ex0, ex1, ey0, ey1 = x0 - w / 2, x1 + w / 2, y0 - h / 2, y1 + h / 2
        for poly in polys:  # keep nearby islands (Corsica, Balearics, Sicily...)
            a, b, c, d = bbox_of([poly[0]])
            cx, cy = (a + b) / 2, (c + d) / 2
            if ex0 <= cx <= ex1 and ey0 <= cy <= ey1:
                x0, x1, y0, y1 = min(x0, a), max(x1, b), min(y0, c), max(y1, d)
        return x0, x1, y0, y1
    x0, x1, y0, y1 = group(max(polys, key=area))
    if not (x0 <= lon <= x1 and y0 <= lat <= y1):
        home = next((p for p in polys if point_in_ring(lon, lat, p[0])), None)
        if home is None:  # point on the coast: nearest polygon
            def dist(poly):
                a, b, c, d = bbox_of([poly[0]])
                return max(a - lon, 0, lon - b) + max(c - lat, 0, lat - d)
            home = min(polys, key=dist)
        x0, x1, y0, y1 = group(home)
    mx, my = (x1 - x0) * 0.08 + 0.15, (y1 - y0) * 0.08 + 0.15
    x0, x1, y0, y1 = x0 - mx, x1 + mx, y0 - my, y1 + my
    # very long or very wide countries: crop a window around the point
    k = math.cos(math.radians((y0 + y1) / 2))
    wp, hp = (x1 - x0) * k, (y1 - y0)
    if hp > wp * 1.5:
        nh = wp * 1.25
        cy = min(max(lat, y0 + nh / 2), y1 - nh / 2)
        y0, y1 = cy - nh / 2, cy + nh / 2
    elif wp > hp * 1.8:
        nw = hp * 1.4 / k
        cx = min(max(lon, x0 + nw / 2), x1 - nw / 2)
        x0, x1 = cx - nw / 2, cx + nw / 2
    return x0, x1, y0, y1

def map_svg(geo, m, pal, lang):
    code = m["country_iso3"].upper()
    if code not in geo:
        raise SystemExit(f"Unknown country code {code!r} (use ISO 3166-1 alpha-3, e.g. FRA, ESP, ITA, ARM).")
    lo0, lo1, la0, la1 = view_box(geo[code], m["lon"], m["lat"])
    k = math.cos(math.radians((la0 + la1) / 2))
    W = 1000.0
    s = W / ((lo1 - lo0) * k)
    H = (la1 - la0) * s
    P = lambda lon, lat: ((lon - lo0) * k * s, (la1 - lat) * s)
    def path(polys):
        d = []
        for poly in polys:
            for ring in poly:
                d.append("M" + "L".join("%.1f,%.1f" % P(x, y) for x, y in ring) + "Z")
        return "".join(d)
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">',
         f'<rect width="{W:.0f}" height="{H:.0f}" fill="{pal["sea"]}"/>']
    seen = set()
    for c, polys in geo.items():
        if c == code or id(polys) in seen or id(polys) == id(geo[code]):
            continue
        seen.add(id(polys))
        a, b, cc, d = bbox_of([p[0] for p in polys])
        if b < lo0 or a > lo1 or d < la0 or cc > la1:
            continue
        o.append(f'<path d="{path(polys)}" fill="{pal["other"]}" stroke="{pal["sea"]}" stroke-width="2"/>')
    o.append(f'<path d="{path(geo[code])}" fill="{pal["land"]}" stroke="{pal["stroke"]}" stroke-width="3" stroke-linejoin="round"/>')
    ref = m.get("ref")
    if ref:
        rx, ry = P(ref["lon"], ref["lat"])
        o.append(f'<circle cx="{rx:.1f}" cy="{ry:.1f}" r="9" fill="{pal["soft"]}" opacity="0.85"/>')
        o.append(f'<text x="{rx+18:.1f}" y="{ry+11:.1f}" font-size="34" fill="{pal["soft"]}" font-family="DM Sans, Arial, sans-serif">{esc(ref["name"], lang)}</text>')
    x, y = P(m["lon"], m["lat"])
    o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="40" fill="{pal["dot"]}" opacity="0.22"/>')
    o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="24" fill="none" stroke="{pal["dot"]}" stroke-width="4"/>')
    o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="{pal["dot"]}"/>')
    left = x > W * 0.58
    tx, anchor = (x - 52, "end") if left else (x + 52, "start")
    ty = y - 34 if y > H * 0.22 else y + 64
    o.append(f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anchor}" font-size="44" font-weight="700" fill="{pal["dot"]}" '
             f'font-family="DM Sans, Arial, sans-serif" paint-order="stroke" stroke="{pal["sea"]}" stroke-width="10">{esc(m["place"], lang)}</text>')
    if m.get("country_label"):
        o.append(f'<text x="28" y="62" font-size="40" font-weight="700" letter-spacing="6" fill="{pal["soft"]}" '
                 f'font-family="DM Sans, Arial, sans-serif">{esc(m["country_label"].upper(), lang)}</text>')
    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------------------- page
def page(w, i, n, geo, lang, theme):
    S = STRINGS.get(lang, STRINGS["en"])
    E = lambda t: esc(t, lang)
    pal = PRINT_PANEL if theme == "print" else PANELS.get(w.get("color", "red"), PANELS["red"])
    num = w.get("number") or f"{i+1:02d}"
    tech = "".join(f'<div class="ti"><span class="tk">{E(t["label"])}</span><span class="tv">{E(t["text"])}</span></div>' for t in w["technique"])
    tz = w["tasting"]
    taste = "".join(f'<div class="si"><span class="sk">{S[k]}</span><span class="sv">{E(tz[k])}</span></div>' for k in ("eye", "nose", "palate", "finish") if tz.get(k))
    prof = "".join(
        f'<div class="pr"><span class="pk">{E(p["label"])}</span><span class="bar">'
        + "".join(f'<span class="seg{" on" if j < int(p["value"]) else ""}"></span>' for j in range(5))
        + f'</span><span class="pn">{int(p["value"])}/5</span></div>' for p in w["profile"])
    pairs = "".join(f'<div class="pair"><div class="pkind">{E(p["kind"])}</div><div class="pdish">{E(p["dish"])}</div>'
                    + (f'<div class="pnote">{E(p["note"])}</div>' if p.get("note") else "") + "</div>" for p in w["pairings"])
    facts = "".join(f'<div class="f"><span class="fk">{E(f["label"])}</span><span class="fv">{E(f["value"])}</span></div>' for f in w["facts"])
    story = "".join(f"<p>{E(p)}</p>" for p in w["story"])
    know = f'<div class="know"><b>{S["know"]}</b> {E(w["did_you_know"])}</div>' if w.get("did_you_know") else ""
    avoid = f'<div class="avoid"><b>{S["avoid"]}</b> {E(w["avoid"])}</div>' if w.get("avoid") else ""
    m = w["map"]
    style = ";".join(f"--{k}:{v}" for k, v in pal.items())
    return f'''
<div class="page" style="{style}">
  <aside class="side">
    <div class="num">{E(num)}<span class="of"> / {n:02d}</span></div>
    <div class="type">{E(w["type_label"])}</div>
    <h1>{E(w["name"])}</h1>
    <div class="prod">{E(w["producer"])}</div>
    <div class="app">{E(w["appellation"])}</div>
    <div class="map">{map_svg(geo, m, pal, lang)}</div>
    <div class="cap">{E(m.get("caption", ""))}</div>
    <div class="facts">{facts}</div>
  </aside>
  <main class="main">
    <div class="eyebrow">{S["sheet"]} {E(num)}</div>
    <p class="hook">{E(w["hook"])}</p>
    <div class="row r1">
      <section><h2>{S["story"]}</h2><div class="story">{story}</div></section>
      <section><h2>{S["technique"]}</h2><div class="tech">{tech}</div></section>
    </div>
    <div class="row r2">
      <section><h2>{S["tasting"]}</h2><div class="taste">{taste}</div></section>
      <section><h2>{S["profile"]}</h2>{prof}{know}</section>
    </div>
    <section><h2>{S["table"]}</h2><div class="pairs">{pairs}</div>{avoid}</section>
    <div class="src">{S["sources"]} {E(w.get("sources", ""))} · {S["indicative"]}</div>
  </main>
</div>'''

FIT_JS = """
<script>
// Shrink text on a page (down to 78 %) until nothing overflows its column.
function fit(){
  document.querySelectorAll('.side,.main').forEach(function(box){
    var s = 1; box.style.setProperty('--s', s);
    while (box.scrollHeight > box.clientHeight + 1 && s > 0.78) { s -= 0.02; box.style.setProperty('--s', s.toFixed(2)); }
    if (box.scrollHeight > box.clientHeight + 1) { box.closest('.page').setAttribute('data-overflow', '1'); console.warn('Text still overflows on a page: shorten it.'); }
  });
  document.body.setAttribute('data-fitted', '1');
}
(document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(fit);
</script>"""

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data", help="JSON file describing the wines (see references/data-format.md)")
    ap.add_argument("--out", required=True, help="output HTML file")
    ap.add_argument("--theme", choices=["color", "print"], default=None, help="color (default) or print (ink-saving)")
    ap.add_argument("--lang", default=None, help="fr, en, nl, es, de, it (overrides the JSON)")
    ap.add_argument("--geo", default=None, help="Natural Earth admin-0 countries GeoJSON (downloaded if omitted)")
    a = ap.parse_args()
    with open(a.data, encoding="utf-8") as f:
        data = json.load(f)
    lang = (a.lang or data.get("lang") or "en").lower()
    theme = a.theme or data.get("theme") or "color"
    if lang not in STRINGS:
        print(f"Warning: no built-in labels for {lang!r}; using English labels. Add them to STRINGS.", file=sys.stderr)
    geo = load_geo(a.geo)
    wines = data["wines"]
    body = "".join(page(w, i, len(wines), geo, lang, theme) for i, w in enumerate(wines))
    with open(os.path.join(ROOT, "assets", "sheet.css"), encoding="utf-8") as f:
        css = f.read()
    title = esc(data.get("title", "Wine tasting sheets"), lang)
    doc = (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{title}</title>'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=DM+Sans:wght@400;500;700&display=block">'
           f'<style>{css}</style></head><body class="theme-{theme}">{body}{FIT_JS}</body></html>')
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"Wrote {a.out} ({len(wines)} sheets, lang={lang}, theme={theme})")

if __name__ == "__main__":
    main()
