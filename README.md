# Open Benchmark Review

Source for [openbenchmarkreview.org](https://openbenchmarkreview.org): independent reviews of AI benchmarks.
*Every benchmark score deserves an asterisk.*

The published site is the `docs/` folder. Everything else builds it.

## Preview locally

```bash
python3 -m http.server -d docs 8000
```

Then open http://localhost:8000.

## Rebuild after editing

```bash
python3 build.py        # writes docs/
node render_cards.js    # optional: renders the social share images (needs Node + Playwright)
```

## What to edit

| File | Controls |
| --- | --- |
| `content/site.json` | Site name, tagline, domain, GitHub repository link, contact email, benchmark sections (e.g. ML Benchmarks) |
| `content/benchmarks.json` | One entry per review: section, verdict, defect counts, summary, rubric statuses |
| `content/reviews/<slug>.html` | The full review page for each benchmark |
| `content/pages/*.html` | Methodology, About, Submit a review |
| `content/style.css` | All styling: one red `#8B1E1A`, Open Sans and IBM Plex Mono |
| `assets/` | The OBR* mark, favicons, ridgeline art, the X banner |

To add a review, add its page to `content/reviews/`, add an entry to `content/benchmarks.json` with its `section`, and rebuild. To add a new area of benchmarks, add a section to `content/site.json`; it appears as its own group on the Benchmarks page.

## Publish on GitHub Pages

1. Push this folder to `github.com/Open-Benchmark-Review/website`.
2. Repository Settings → Pages → Build and deployment: Deploy from a branch, branch `main`, folder `/docs`.
3. Custom domain: `openbenchmarkreview.org` (already set by `docs/CNAME`).
4. At the domain registrar, add these DNS records:

   | Type | Host | Value |
   | --- | --- | --- |
   | A | @ | 185.199.108.153 |
   | A | @ | 185.199.109.153 |
   | A | @ | 185.199.110.153 |
   | A | @ | 185.199.111.153 |
   | AAAA | @ | 2606:50c0:8000::153 |
   | AAAA | @ | 2606:50c0:8001::153 |
   | AAAA | @ | 2606:50c0:8002::153 |
   | AAAA | @ | 2606:50c0:8003::153 |
   | CNAME | www | `open-benchmark-review.github.io.` |

5. When DNS has propagated, tick **Enforce HTTPS** in the Pages settings.
