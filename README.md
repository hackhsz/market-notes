# Market Notes

Plain-English learning notes on five market sectors: AI chips, memory and power, games, Big Tech, and Tesla and other hot topics. Live at https://hackhsz.github.io/market-notes/

Educational only, not investment advice.

## How it's built

- `src/` holds each page as an HTML fragment (title, styles, then the page body).
- `python3 build.py` wraps every fragment in a full page, adds the site menu, and writes the site to `docs/`.
- GitHub Pages serves `docs/` from the `main` branch.

To add a page: put `src/<slug>.html` in place, add the slug to `PAGES` in `build.py`, update the home page (`src/index.html`) list and update log, then rebuild and push.
