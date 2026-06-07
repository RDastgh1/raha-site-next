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

GitHub Pages deployment is handled by `.github/workflows/deploy.yml`.

The workflow renders Quarto first, then builds Hugo, then deploys the generated `public/` artifact through GitHub Pages Actions.

## Content model

- `content/software/`: first-class scientific software and infrastructure.
- `content/publication/`: BibTeX-assisted publication portals.
- `content/talks/`: talks, workshops, invited presentations, and scientific communication.
- `content/research/`: conceptual research architecture pages.
- `content/community/`: community leadership and scientific infrastructure.
- `content/posts/`: optional longform essays.

There is intentionally no `content/project/` in v1.
