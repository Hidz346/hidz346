# Contributing

Thanks for contributing to **SYAHID SUBHAN PUTRA — GitHub Profile Card**.

## Development

Requirements:

- Python 3.12+
- Pillow
- NumPy
- Requests

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Generate the card locally:

```bash
GITHUB_LOGIN="your-username" python scripts/generate_card.py
```

The generated SVG is written to `assets/profile.svg` by default.

## Before opening a pull request

Run:

```bash
python -m py_compile scripts/generate_card.py scripts/generate_card_v2.py
GITHUB_LOGIN="your-username" python scripts/generate_card.py
```

Then open `assets/profile.svg` in a browser and verify that:

- the card is readable at full size and when scaled down;
- the avatar remains inside its panel;
- long profile values do not overlap the statistics area;
- the terminal prompt remains readable;
- the SVG is valid XML;
- no secrets or personal access tokens are committed.

## Design rules

- Keep the generated SVG self-contained.
- Do not add JavaScript to the generated card.
- Prefer CSS animation that has a readable static fallback.
- Keep profile data configurable through environment variables where practical.
- Avoid duplicated generator implementations.
- Do not commit `GITHUB_TOKEN` or any other credential.

## Pull requests

Keep each pull request focused. Explain what changed, why it changed, and how it was tested.
