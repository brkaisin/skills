# Wine skills

One skill, **wine-tasting-sheets**: from a list of wines to a printable PDF of tasting sheets, one A4 landscape page per wine.

```
list of wines → research (producer sheets, critics) → wines.json → HTML → PDF (colour and/or print)
```

Each sheet has:

- **The wine**: name, producer and appellation.
- **A small map of the country**, with a dot on the vineyard, village or winery.
- **The content**:
  - a hook and the story;
  - the winemaking;
  - tasting notes;
  - a 1–5 profile and a "did you know?" box;
  - three food pairings and one thing to avoid;
  - a box of key facts.

```
wine-tasting-sheets/
  SKILL.md                     the workflow: inputs, research rules, build, check, deliver
  references/data-format.md    the JSON format, with length budgets per field
  scripts/build_sheets.py      wines.json → HTML (standard-library Python, maps from Natural Earth)
  scripts/render_pdf.py        HTML → PDF with headless Chrome / Chromium / Edge / Brave
  assets/sheet.css             layout and the two themes
  examples/four-wines.fr.json  a complete example: four wines, in French
```

- **Languages:** section labels are built in for `fr`, `en`, `nl`, `es`, `de` and `it`. The agent writes the content itself in the requested language.
- **Themes:**
  - `color`: tinted panels, with the panel colour following the wine's colour.
  - `print`: white paper, thin lines. Saves ink.
- **Long text:** pages shrink their text, down to 78 %, when it would overflow.

## Install

Claude Code: `/plugin install wine --marketplace brkaisin/skills`. Codex / Copilot: the `wine@brkaisin` plugin. Any other agent: `npx skills add brkaisin/skills -s wine-tasting-sheets`. Details in the [repo README](../README.md#install). Then ask your agent:

> "make tasting sheets for these wines" / "fais-moi des fiches de dégustation pour ces vins, en anglais, version imprimable"

## Requirements

- **Python 3**, standard library only.
- **A browser for the PDF:** Chrome, Chromium, Edge or Brave. Without one, open the HTML and print it to PDF in landscape, with background graphics on.
- **Network access:**
  - for the research;
  - once, to download about 3 MB of country outlines;
  - to load the Google Fonts. Offline, the sheets fall back to Georgia and Arial.
