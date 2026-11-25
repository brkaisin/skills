---
name: wine-tasting-sheets
description: Research a list of wines and produce a printable PDF of tasting sheets, one A4 landscape page per wine, with story, winemaking, tasting notes, a 1–5 profile, food pairings, key facts and a small country map with a dot on where the wine comes from. Use when the user asks for wine tasting sheets, wine cards, a tasting booklet or "fiches de dégustation" for a tasting with friends, in any language, as a colour version or an ink-saving print version.
---

# Wine tasting sheets

Turns a list of wines into a PDF of tasting sheets: one A4 landscape page per wine.

Each page has two parts:

- **Side panel**:
  - the wine's name, producer, appellation and vintage;
  - a map of the country with a dot on the place the wine comes from;
  - a short list of key facts.
- **Main column**:
  - a one-sentence hook;
  - the story;
  - the winemaking;
  - tasting notes (eye, nose, palate, finish);
  - a 1–5 profile and a "did you know?" box;
  - three food pairings and one thing to avoid.

The tooling needs only:

- **Python 3**, standard library only.
- **A Chromium-family browser** (Chrome, Chromium, Edge or Brave) to print the PDF. If none is installed, the HTML can be printed by hand.

Nothing in this skill depends on a particular agent or harness.

## Files

- `scripts/build_sheets.py`: turns the wine data (JSON) into one HTML file.
- `scripts/render_pdf.py`: prints that HTML to PDF with a headless browser.
- `assets/sheet.css`: the layout and both themes.
- `references/data-format.md`: the JSON format, with length budgets for every field. Read it before writing the data.
- `examples/four-wines.fr.json`: a complete example with four wines, in French.

## Inputs to settle first

1. **The wines.** For each one: name, producer and vintage. The person may give a photo, an order form or a plain list.
2. **The language.** Use the language the person asks for. If they don't say, use the language they are writing in. The built-in section labels cover `fr`, `en`, `nl`, `es`, `de` and `it`. For another language, add a block to `STRINGS` in `build_sheets.py`.
3. **The theme.**
   - `color`: tinted side panel and backgrounds.
   - `print`: white paper, thin lines, colour only in small text. Uses very little ink.

   If the person doesn't choose, build both.

Ask only for what you cannot infer. Don't ask the person about grape varieties, regions or anything else you can research.

## Workflow

### 1. Research each wine

Use whatever web search and page-reading tools you have. Prefer sources in this order:

1. The producer's technical sheet ("fiche technique", "ficha técnica", "scheda tecnica"). Its PDF is often linked from the product page.
2. The producer's product page and the back label.
3. Critics and competitions: Decanter, Guía Peñín, Falstaff, Jancis Robinson, Andreas Larsson, Concours Mondial, IWSC and similar.
4. Retailers and Vivino. Use them for scores and ABV when nothing better exists.
5. Wikipedia or encyclopaedias, only for the history of the grape and the region.

Collect, for each wine:

- **The producer**: who they are and a story worth telling.
- **The place**: region, soils, altitude, climate.
- **The vineyard and the wine**: grapes and their percentages, viticulture, harvest, vinification, élevage (vessel, oak, months).
- **The numbers**: ABV, serving temperature, ageing potential.
- **Tasting and food**: tasting notes from the producer and critics, and the producer's food pairings.
- **Recognition**: scores and medals, each with its vintage.
- **For the map**: the exact place, with its latitude and longitude.
  - Use the vineyard or village if it is known. Otherwise use the winery.
  - Add a reference city, usually the capital.

Rules:

- **Never invent a fact.** If something is missing, leave it out, or mark it clearly in the target language, for example "(estimate)" or "(estimation)".
- **Flag vintage mismatches**, for example "Gold 2024 (2023 vintage)".
- **When sources disagree, say so on the sheet**, for example: "Barrel-aged per the producer; one competition listing says unoaked."
- **The 1–5 profile is your own judgement** from the notes. The sheet already labels it as indicative.
- **Food pairings**: start with the producer's suggestions. Add classic pairings for the style and, where it fits, a local dish from the wine's region. The `sources` line should show which ones came from the producer.

### 2. Write the data file

Write one JSON file following `references/data-format.md`. Rules for the text:

- Write every text field directly in the target language: the labels in `technique`, `profile` and `facts` too.
- Stay within the length budgets. The page fits a fixed A4 sheet.
- Keep the wines in serving order: sparkling, then whites, rosés, reds, and sweet wines last.

### 3. Build and render

Run these from any folder. Replace `SKILL_DIR` with this skill's folder.

```bash
python3 SKILL_DIR/scripts/build_sheets.py wines.json --out out/sheets-color.html --theme color
python3 SKILL_DIR/scripts/render_pdf.py out/sheets-color.html out/sheets-color.pdf
python3 SKILL_DIR/scripts/build_sheets.py wines.json --out out/sheets-print.html --theme print
python3 SKILL_DIR/scripts/render_pdf.py out/sheets-print.html out/sheets-print.pdf
```

- **Language:** `--lang en` overrides the language set in the JSON.
- **Country outlines:** the first run downloads them, about 3 MB of public-domain Natural Earth data, into `~/.cache/wine-tasting-sheets/`. Without network access, pass `--geo path/to/ne_50m_admin_0_countries.geojson`.
- **Browser:** `render_pdf.py` looks for Chrome, Chromium, Edge or Brave, or uses `$CHROME_PATH`. If none is found, tell the person to open the HTML in a browser and print it to PDF with these settings:
  - Layout: Landscape.
  - Margins: None.
  - Background graphics: on.

### 4. Check the result

- **Look at every page if you can view images.** For example, convert pages with `pdftoppm -png -r 60` or PyMuPDF, or open the PDF.
- **Long text is shrunk automatically.** The page shrinks text down to 78 % to make it fit.
  - If a page still looks cramped, shorten that wine's longest fields and rebuild.
  - If you cannot look at the pages, compare each field with the length budgets.
- **Check the map:**
  - the dot sits on the right place;
  - the place label does not cover the reference city.
  - If the dot is in the sea, recheck the coordinates.

### 5. Deliver

- Give the paths of the PDFs.
- Say which facts are estimates or come from another vintage.
- Keep the JSON file next to the PDFs. The person can then ask for edits or for another language later.
- **Another language:** translate the JSON and rebuild. Don't research again.

## Design notes

- **Side panel colour** follows the wine's `color` field: `white`, `red`, `rose`, `orange`, `sparkling` or `sweet`. The `print` theme ignores it.
- **Fonts**: Cormorant Garamond and DM Sans, loaded from Google Fonts. Offline, the page falls back to Georgia and Arial; it still works, but looks plainer.
- **Map framing**: the map shows the mainland and nearby islands, such as Corsica, Sicily or the Balearics. A wine from far-off islands, such as the Canaries or Madeira, gets a map of its islands only. Very long or very wide countries, such as Chile, are cropped around the dot.
