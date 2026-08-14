# Raha Site Next

Dark-mode-first personal academic and research website for Raha Dastgheyb.

The site is structured around research architecture, scientific software, publications, talks, living systems, and community infrastructure. The content model follows Hugo Blox conventions, while v1 uses local layouts and SCSS for the cinematic homepage and reliable deployment.

## Local development

Install:

- Hugo Extended
- Quarto
- Go

Run:

```sh
quarto render quarto
hugo server
```

## Deployment

Netlify serves rahadastgheyb.com. Build settings are committed in `netlify.toml`;
see `DEPLOYMENT.md` for the full procedure and rollback steps.

A GitHub Pages workflow used to live at `.github/workflows/deploy.yml`. It was
removed: it pinned Hugo 0.125.7 and so had failed on every run since June 2026
(the site needs >= 0.144 for `hugo.Data`), and had it worked it would have
published a second copy of the site at `rdastgh1.github.io`, competing with the
canonical domain. Restore it with `git revert` only if you actually want a
second published copy.

## Content model

- `content/software/`: first-class scientific software and infrastructure.
- `content/publication/`: BibTeX-assisted publication portals.
- `content/talks/`: talks, workshops, invited presentations, and scientific communication.
- `content/research/`: conceptual research architecture pages.
- `content/community/`: community leadership and scientific infrastructure.
- `content/posts/`: optional longform essays.

There is intentionally no `content/project/` in v1.
