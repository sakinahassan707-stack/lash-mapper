"""Lash Mapper.

Asks about a client's eye shape, eye spacing, natural lash condition and the
look they want, then applies a set of mapping rules to recommend a curl,
a style and a length map across six sections of the lash line.

All the rules live in lash_rules.json, so the mapping logic can be changed
by editing data rather than code.
"""

import json
import sys

RULES_FILE = "lash_rules.json"


def load_rules(path=RULES_FILE):
    """Load the rules file, exiting with a clear message if it is missing
    or malformed."""
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        sys.exit(f"Could not find {path}. It must sit in the same folder as this program.")
    except json.JSONDecodeError as error:
        sys.exit(f"{path} is not valid JSON: {error}")


def choose(prompt, options, descriptions=None):
    """Show a numbered menu and keep asking until a valid number is entered.

    Returns the chosen key from options.
    """
    print(f"\n{prompt}")
    for index, key in enumerate(options, start=1):
        label = key.replace("_", " ").title()
        if descriptions and key in descriptions:
            print(f"  {index}. {label}")
            print(f"     {descriptions[key]}")
        else:
            print(f"  {index}. {label}")

    valid = [str(number) for number in range(1, len(options) + 1)]
    while True:
        answer = input(f"Enter a number between 1 and {len(options)}: ").strip()
        if answer in valid:
            return options[int(answer) - 1]
        print("Invalid input, please try again.")


def pick_style(shape_rule, effect_rule):
    """Choose a style that satisfies the desired effect without being one the
    eye shape rules out. Falls back to the shape's own best style."""
    avoided = shape_rule.get("styles_avoid", [])
    preferred = shape_rule.get("styles_best", [])

    for style in effect_rule["style_preference"]:
        if style in avoided:
            continue
        return style, None

    # Every style the client wanted is ruled out by their eye shape.
    fallback = preferred[0] if preferred else "kitten"
    warning = (
        f"The styles usually used for that look are not ideal for this eye shape, "
        f"so {fallback.replace('_', ' ')} has been used instead."
    )
    return fallback, warning


def build_map(base_profile, shape_adjust, spacing_adjust, effect_modifier, cap):
    """Combine the style profile with the shape and spacing corrections.

    Returns a list of six lengths in millimetres, rounded to the nearest 0.5
    and capped at what the natural lashes can carry.
    """
    raw = [
        base + shape_adjust[index] + spacing_adjust[index] + effect_modifier
        for index, base in enumerate(base_profile)
    ]

    # If the longest lash would exceed what the natural lashes can carry,
    # shift the whole map down rather than clipping the top flat. Clipping
    # would destroy the shape of the map, which is the entire point of it.
    overshoot = max(raw) - cap
    if overshoot > 0:
        raw = [value - overshoot for value in raw]

    lengths = []
    for value in raw:
        value = max(value, 4)  # nothing shorter than 4mm is practical
        lengths.append(round(value * 2) / 2)
    return lengths


def print_map(zones, lengths):
    """Print the finished map as an aligned table."""
    print("\n  Length map, inner corner to outer corner")
    print("  " + "-" * 44)
    for zone, length in zip(zones, lengths):
        bar = "#" * int(length - 4)
        print(f"  {zone:<14}{length:>5}mm  {bar}")
    print("  " + "-" * 44)


def main():
    rules = load_rules()
    zones = rules["_meta"]["zones"]

    print("\n" + "=" * 52)
    print("LASH MAPPER".center(52))
    print("=" * 52)

    # Eye shape. The spacing options are handled separately below.
    spacing_keys = ["close_set", "wide_set"]
    shape_keys = [key for key in rules["eye_shapes"] if key not in spacing_keys]
    shape_descriptions = {
        key: rules["eye_shapes"][key]["identify"] for key in shape_keys
    }
    shape = choose("What is the client's eye shape?", shape_keys, shape_descriptions)

    spacing = choose(
        "How far apart are the eyes?",
        ["average", "close_set", "wide_set"],
        {
            "average": "About one eye width between them.",
            "close_set": "Less than one eye width between them.",
            "wide_set": "More than one eye width between them.",
        },
    )

    condition_keys = list(rules["natural_lash_conditions"])
    condition_descriptions = {
        key: rules["natural_lash_conditions"][key]["identify"] for key in condition_keys
    }
    condition = choose(
        "What are the natural lashes like?", condition_keys, condition_descriptions
    )

    natural_length = 0.0
    while True:
        answer = input("\nRoughly how long are the natural lashes in mm? ").strip()
        try:
            natural_length = float(answer)
        except ValueError:
            print("Please enter a number, for example 8")
            continue
        if 3 <= natural_length <= 15:
            break
        print("That seems out of range. Natural lashes are usually 5mm to 12mm.")

    effect = choose("What look does the client want?", list(rules["desired_effects"]))

    # Pull the matching rules.
    shape_rule = rules["eye_shapes"][shape]
    condition_rule = rules["natural_lash_conditions"][condition]
    effect_rule = rules["desired_effects"][effect]

    if spacing == "average":
        spacing_adjust = [0, 0, 0, 0, 0, 0]
        spacing_rule = None
    else:
        spacing_rule = rules["eye_shapes"][spacing]
        spacing_adjust = spacing_rule["adjustment_mm"]

    style, style_warning = pick_style(shape_rule, effect_rule)
    style_rule = rules["styles"][style]

    cap = natural_length + condition_rule["max_added_mm"]
    lengths = build_map(
        style_rule["profile"],
        shape_rule["adjustment_mm"],
        spacing_adjust,
        effect_rule["length_modifier_mm"],
        cap,
    )

    # Output.
    print("\n" + "=" * 52)
    print("RECOMMENDATION".center(52))
    print("=" * 52)

    print(f"\n  Eye shape:  {shape.replace('_', ' ').title()}")
    print(f"  Spacing:    {spacing.replace('_', ' ').title()}")
    print(f"  Lashes:     {condition.replace('_', ' ').title()}")
    print(f"  Wanted:     {effect.replace('_', ' ').title()}")

    print(f"\n  Style:      {style.replace('_', ' ').title()}")
    print(f"              {style_rule['description']}")
    if style_warning:
        print(f"\n  Note: {style_warning}")

    print(f"\n  Curl:       {', '.join(shape_rule['curls_best'])}")
    if shape_rule["curls_avoid"]:
        print(f"  Avoid:      {', '.join(shape_rule['curls_avoid'])}")
        print(f"              {shape_rule['curls_avoid_reason']}")

    print(f"\n  Thickness:  {condition_rule['max_weight']}")
    print(f"  Max length: {cap}mm ({natural_length}mm natural "
          f"+ {condition_rule['max_added_mm']}mm)")

    print_map(zones, lengths)

    print("\n  Why this map")
    print(f"  {shape_rule['goal']}")
    print(f"  {shape_rule['length_bias']}")
    if spacing_rule:
        print(f"  {spacing_rule['goal']}")

    print("\n  Things to watch")
    for note in shape_rule["notes"]:
        print(f"  - {note}")
    print(f"  - {condition_rule['notes']}")

    print("\n  Safety")
    for rule in rules["safety_rules"][:3]:
        print(f"  - {rule}")

    print("\n" + "=" * 52)
    print("  Always check the map with the eyes open before you start.")
    print("=" * 52 + "\n")


if __name__ == "__main__":
    main()
