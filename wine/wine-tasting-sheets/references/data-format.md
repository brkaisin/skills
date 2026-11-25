# Data format

One JSON file describes the whole booklet. All text is plain Unicode. Don't use HTML or Markdown in it.

Write the text exactly as it should appear, in the target language. Use that language's punctuation: in French, `« »` and a space before `: ; ? !`. The build script adds the non-breaking spaces itself.

```json
{
  "lang": "en",
  "theme": "color",
  "title": "Tasting evening, 4 wines",
  "wines": [ { ...one object per wine, in serving order... } ]
}
```

- `lang`: one of `fr`, `en`, `nl`, `es`, `de`, `it`. It sets the section labels. The `--lang` option overrides it.
- `theme`: `color` or `print`. The `--theme` option overrides it.
- `title`: the PDF's document title. Optional.

## One wine

The budgets below are for a sheet that fits without shrinking. A little over is fine, because the page shrinks text down to 78 %. Far over means you must shorten the text.

| Field | Type | Budget | Notes |
|---|---|---|---|
| `color` | string | | `white`, `red`, `rose`, `orange`, `sparkling` or `sweet`. Sets the side panel colour. |
| `number` | string | | Optional. Defaults to `01`, `02`… in file order. |
| `type_label` | string | ≤ 18 chars | Shown as a pill, for example "Blanc sec", "Red · Organic". |
| `name` | string | ≤ 22 chars | The cuvée name. It may wrap to two lines. |
| `producer` | string | ≤ 30 chars | |
| `appellation` | string | ≤ 40 chars | Appellation, region and vintage, for example "AOP Corbières · Languedoc · 2019". |
| `hook` | string | ≤ 190 chars | One sentence: the most surprising true thing about the wine. |
| `story` | array of 2 strings | ≤ 340 chars each | First paragraph: the grape, place or history. Second: the producer. |
| `technique` | array of 5 `{label, text}` | label ≤ 12, text ≤ 125 chars | Pick from: terroir, climate, vineyard, harvest, vinification, élevage, ageing, grape. |
| `tasting` | `{eye, nose, palate, finish}` | ≤ 115 chars each | The labels are added for you in the right language. |
| `profile` | array of 5 `{label, value}` | label ≤ 11 chars, value 1–5 | Whites: acidity, body, oak, sweetness, intensity. Reds: acidity, body, tannins, oak, spice or fruit. |
| `did_you_know` | string | ≤ 170 chars | Optional. A fact that starts a conversation. |
| `pairings` | array of 3 `{kind, dish, note}` | kind ≤ 22, dish ≤ 26, note ≤ 45 chars | `kind` is the course or the source, for example "Starter" or "The producer’s pick". |
| `avoid` | string | ≤ 75 chars | Optional. The "Avoid:" label is added for you. |
| `facts` | array of 6 `{label, value}` | label ≤ 12, value ≤ 30 chars | Usually: grape(s), ABV, élevage, serving temperature, ageing, awards. |
| `map` | object | | See below. |
| `sources` | string | ≤ 150 chars | Short source names, separated by ` · `. Add vintage notes here. |

### `map`

```json
{
  "country_iso3": "FRA",
  "country_label": "France",
  "place": "Corbières, Aude",
  "lat": 43.087, "lon": 2.700,
  "caption": "The winery in Saint-Laurent-de-la-Cabrerisse.",
  "ref": { "name": "Paris", "lat": 48.857, "lon": 2.352 }
}
```

- `country_iso3`: the ISO 3166-1 alpha-3 code: `FRA`, `ESP`, `ITA`, `PRT`, `DEU`, `ARM`, `CHL`, `USA`…
- `place`: the label next to the dot. At most 24 characters.
- `lat` and `lon`: decimal degrees, south and west negative. Use the vineyard or village if it is known, otherwise the winery. Look them up; don't guess.
- `caption`: one line under the map saying what the dot is. At most 90 characters.
- `ref`: optional. A reference city to help people find their way, usually the capital. Leave it out if it would sit on top of the dot.

## Example

`examples/four-wines.fr.json` is a complete, real example: four wines, in French.
