<h1 align="center">SYAHID SUBHAN PUTRA</h1>

<p align="center">
  <img src="./assets/profile.gif" alt="Animated GitHub profile card for SYAHID SUBHAN PUTRA" width="100%">
</p>

<p align="center">
  <strong>Web Developer • Automation • Security • HIDZ PROJECT</strong>
</p>

<p align="center">
  Animated profile card built for GitHub Profile README. The image and terminal text are animated as a GIF, while GitHub statistics are refreshed by GitHub Actions.
</p>

## What this version fixes

- Uses the supplied hacker artwork directly instead of turning it into a large ASCII portrait.
- Uses GIF for the profile card animation. GitHub does not support inline SVG scripting or animation, so CSS animation inside an SVG is not a reliable way to create a live GitHub profile card. citeturn0search3
- The hacker image remains visible while the terminal text, cursor, scanline, and interface subtly animate.
- GitHub statistics are fetched during the scheduled/manual GitHub Actions run and written into the animated card.
- The workflow automatically uses the repository owner as `GITHUB_LOGIN`, so the username is not hardcoded.
- The profile README uses a relative image path, which GitHub supports for repository images. citeturn0search0turn0search1

## GitHub profile setup

Create a **public repository whose name exactly matches your GitHub username**. GitHub automatically surfaces that repository's `README.md` on your profile. citeturn0search0turn0search2

Then upload this project to that repository and push to `main`.

The workflow will:

1. detect the repository owner;
2. fetch GitHub statistics;
3. generate `assets/profile.gif`;
4. commit the updated GIF back to the repository.

No personal access token is required. The workflow uses GitHub's built-in `GITHUB_TOKEN`.

## Local generation

```bash
python -m pip install -r requirements.txt
GITHUB_LOGIN=your-username python scripts/generate_profile.py
```

On Windows PowerShell:

```powershell
$env:GITHUB_LOGIN="your-username"
python scripts/generate_profile.py
```

## Files

```text
.
├── .github/workflows/generate-profile.yml
├── assets/
│   ├── hacker.jpg
│   ├── avatar.png
│   └── profile.gif
├── scripts/
│   └── generate_profile.py
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── requirements.txt
```

## Important note about "live"

The **visual animation is live on the rendered GitHub README because it is a GIF**. GitHub supports GIF images in README content. The GitHub statistics are **refresh-on-generation**, not a per-second API stream: the included Action refreshes them daily and can also be run manually. GitHub supports GIF files in README content and supports relative repository image paths. citeturn0search1turn0search8

## Customize

Set these environment variables in the workflow if you want to change the profile later:

| Variable | Default |
| --- | --- |
| `PROFILE_NAME` | `SYAHID SUBHAN PUTRA` |
| `PROFILE_BRAND` | `HIDZ PROJECT` |
| `PROFILE_ROLE` | `WEB DEVELOPER & SECURITY ENTHUSIAST` |
| `PROFILE_LOCATION` | `INDONESIA` |
| `AVATAR_PATH` | `assets/hacker.jpg` |
| `OUT_PATH` | `assets/profile.gif` |

The actual GitHub username is supplied automatically by `${{ github.repository_owner }}` in Actions.

## License

The original project license is retained in `LICENSE`. Review it before redistributing modified versions.
