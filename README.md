# Open Benchmark Review: website

Source for [openbenchmarkreview.org](https://openbenchmarkreview.org). The published site is the `docs/` folder;
everything else builds it. The evidence behind each review is in
[Open-Benchmark-Review/audits](https://github.com/Open-Benchmark-Review/audits).

## Build and preview

```bash
python3 build.py                      # writes docs/
python3 -m http.server -d docs 8000   # preview at http://localhost:8000
node render_cards.js                  # optional: social share images (needs Node and Playwright)
```

## What to edit

| File | Controls |
| --- | --- |
| `content/site.json` | Site name, domain, contact email, benchmark sections |
| `content/benchmarks.json` | One entry per review: section, verdict, counts, summary |
| `content/reviews/<slug>.html` | Each benchmark's review page |
| `content/pages/*.html` | Methodology, About, Submit a review |
| `content/style.css` | All styling |
| `assets/` | Logo, favicons, artwork |

To add a review, add its page to `content/reviews/` and its entry to `content/benchmarks.json`, then rebuild.

## Publishing

GitHub Pages serves `docs/` from the `main` branch. The custom domain is set in `docs/CNAME`.

<details>
<summary>DNS records for the domain</summary>

| Type | Host | Value |
| --- | --- | --- |
| A | @ | 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 |
| AAAA | @ | 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153 |
| CNAME | www | `open-benchmark-review.github.io.` |

Once DNS has propagated, tick **Enforce HTTPS** in the Pages settings.
</details>
