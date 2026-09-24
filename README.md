# Lash Mapper

Works out a recommended lash extension map from a client's eye shape, eye spacing,
natural lash condition and the look they want. Outputs a suggested style, curl,
thickness and a length map across six sections of the lash line, with the reasoning
behind each choice.

Built because getting a lash map right is mostly experience, and that experience is
hard to transfer. This encodes it as rules so the reasoning is explicit rather than
instinctive.

## How it works

The program asks four questions, then combines four sets of rules:

1. **Style profile** - a base length curve for the chosen style (cat, kitten, doll,
   squirrel, open eye, wispy, natural).
2. **Eye shape correction** - a per-section adjustment in millimetres. A downturned
   eye, for example, peaks before the outer corner and then steps down, because
   maximum length at the outer corner exaggerates the droop.
3. **Spacing correction** - close set eyes shift weight outwards, wide set eyes
   shift it inwards.
4. **Safety cap** - the natural lash length plus the maximum safe addition for that
   lash condition. If the map would exceed it, the whole profile shifts down rather
   than being clipped flat, so the shape of the map survives.

It also refuses to recommend a style the eye shape rules out. Asking for a dramatic
cat eye on a hooded eye returns the nearest suitable alternative and says why.

## Running it

Requires Python 3.10 or later. No dependencies.

```bash
python main.py
```

## Editing the rules

All the mapping knowledge lives in `lash_rules.json`. Adding an eye shape, changing
a curl recommendation or adjusting a length profile means editing that file, not the
code. Each section is:

```json
"hooded": {
  "identify": "how to recognise it",
  "goal": "what the map is trying to achieve",
  "curls_best": ["M", "L"],
  "curls_avoid": ["D", "DD"],
  "adjustment_mm": [0, 0, 0, 1, 1, 0]
}
```

`adjustment_mm` runs inner corner to outer corner and is added to the style profile.

## Status

The rules file is a working draft and is being corrected against real sets. The
program logic is finished.

## Planned

- Web version so other lash techs can use it from a link
- Visual output: a diagram of the eye with the lengths drawn across the sections
- Save client profiles so repeat clients come back with their previous map

## Disclaimer

A planning aid, not a substitute for training. Patch test every new client, and
refer anyone reporting itching, swelling or redness to a doctor.
