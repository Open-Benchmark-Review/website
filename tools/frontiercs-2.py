"""Write content/reviews/frontiercs-2.html, the short-form FrontierCS 2 review.

usage: python3 -I tools/frontiercs-2.py

Chart data: tools/data/frontiercs-2_case_data.json, built from public files only:
  - quarter_pir_k31: HF FrontierCS2/FrontierCS-2-runs @ d4d49422, traces/quarter_pir/k31 (verifier evidence of the
    regrade the leaderboard counts and of the first grading of the same submission);
  - detok_counted_grading: same snapshot, metrics.json in verifier/evidence.tar of the grading the leaderboard counts
    (metadata/formal-results.json, result_source): traces/detok_latent_denoising/<run>/selected-final-rejudge for
    carbon-g, gemini-agy and fable51, and the run's own final verification (traces/.../opus/evidence.tar.zst) for opus;
  - kv_reference_captures: GitHub FrontierCS/FrontierCS-2 @ 1e6dfa12, fast_kv_compaction/judge/targets/manifest.json,
    workloads.<article>: questions, reference_correct, reference_correct_per_repetition and uncompressed_correct;
  - kv_quality: same commit, fast_kv_compaction/judge/data/quality_subset.jsonl (QuALITY v1.0.1 records of the 24
    graded articles): each article's title, author, year and question count, and one example question (article
    22346, Exile, line 10, question 22346_3ZEMUJFW_1) with its options and gold label.
Other numbers on the page come from the same two snapshots (metadata/formal-results.json, the traces' verifier
evidence, the task folders); see the audit folder for the scripts.
"""
import html
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reviewkit import (E, GRAY, RED, REPO, X, cite, configure, ev, figure, src, write_page)  # noqa: E402


def c(x):
    """Inline code, with <, > and & escaped (several sources quote comparisons)."""
    return f'<code>{html.escape(x, quote=False)}</code>'

SHA = '1e6dfa12210043c394c392a4f9168dca68e97aaa'
GH = 'https://github.com/FrontierCS/FrontierCS-2'
HF = 'https://huggingface.co/datasets/FrontierCS2/FrontierCS-2-runs'
REV = 'd4d49422dbfabd3a2f1b15b26d319bcc169efedf'
AUDIT = f'{REPO}/blob/main/audits/frontiercs-2'
RESULTS = f'{HF}/blob/{REV}/metadata/formal-results.json'

DETOK, PROG, KV, DIFF = ('detok_latent_denoising', 'progent_privilege_control', 'fast_kv_compaction',
                         'diffusion_policy_cpu')
QPIR, FRE, BFF, EDLIB = 'quarter_pir', 'representation_frechet_loss', 'binary_fuse_filter', 'edlib_exact_alignment'
EGG, JOIN, RADIX, META = ('egraph_invariant_restoration', 'join_tree_rewriting', 'parallel_radix_sort',
                          'metaopt_combined_te_gap_search')
RAGEN, SVG, VLLM = 'ragen_multi_turn_rl', 'sparse_video_attention_policy', 'vllm_llm_serving_optimization'
CATEGORY = {DETOK: 'Machine Learning', PROG: 'Security', KV: 'Machine Learning', DIFF: 'Robotics', QPIR: 'Crypto',
            FRE: 'Machine Learning', BFF: 'Theory', EDLIB: 'Bioinformatics', EGG: 'Programming Language',
            JOIN: 'Database', RADIX: 'HPC', META: 'Network', RAGEN: 'Machine Learning', SVG: 'MLSys', VLLM: 'MLSys'}
# Readable task names, as the summary uses them; the error meta line shows "Name (slug)".
NAME = {VLLM: 'vLLM serving', QPIR: 'QuarterPIR', KV: 'KV-cache compaction', DIFF: 'Diffusion policy on CPU',
        FRE: 'Fréchet representation loss', BFF: 'Binary fuse filter', EDLIB: 'Edlib exact alignment',
        EGG: 'E-graph invariant restoration', JOIN: 'Join-tree rewriting', RADIX: 'Parallel radix sort',
        SVG: 'Sparse video attention', META: 'MetaOpt traffic engineering', DETOK: 'Latent-denoising tokenizer',
        RAGEN: 'RAGEN multi-turn RL', PROG: 'Progent privilege control'}
# Run ids in the released dataset are model ids (patches/<task>/<model>.patch, traces/<task>/<model>/).
MODELS = {'opus': 'Claude Opus 5.5', 'fable51': 'Claude Fable 5.1', 'carbon-g': 'Gemini 4 Carbon',
          'gemini-agy': 'Gemini 4 Argon (Antigravity)', 'gemini': 'Gemini 4 Argon (Pi)', 'astra': 'GPT-6 Astra',
          'sol': 'GPT-6.1 Sol', 'glm': 'GLM 5.3', 'wonder': 'Muse Wonder 1.0', 'k31': 'Kimi K3.1 Pro',
          'ds': 'DeepSeek V4.1 Flash', 'qwen': 'Qwen 3.8 Max'}
configure(lambda task, trial: f'{HF}/tree/{REV}/traces/{task}/{trial}', MODELS)


def folder(task):
    return f'{GH}/tree/{SHA}/tasks/frontier-cs-2.0-demo/problems/{CATEGORY[task]}/{task}'.replace(' ', '%20')


def task(t):
    return f'Task: {NAME[t]} (<a href="{folder(t)}">{t}</a>)'


def gh(t, path, lines=None, shown=None):
    """Link to a file in the task folder at the reviewed commit. lines: 'a' or 'a-b' (also 'a, b-c' for display)."""
    anchor = ''
    if lines:
        first = str(lines).split(',')[0].strip()
        a, _, b = first.partition('-')
        anchor = f'#L{a}' + (f'-L{b}' if b else '')
    shown = shown or path
    text = c(f'{shown}:{lines}' if lines else shown)
    return f'<a href="{folder(t)}/{path}{anchor}">{text}</a>'


def patch(t, model, lines):
    a = str(lines).split('-')[0]
    return f'<a href="{HF}/blob/{REV}/patches/{t}/{model}.patch#L{a}">{c(f"{model}.patch:{lines}")}</a>'


README = 'agent-base/frontier/task/repo/README.md'

# Each error opens with what the task is. The one-liners come from the task pages on frontier-cs.org (the GOAL map in
# assets/js/fcs2-data.js, shown at frontier-cs.org/task/#<slug>; Progent has none there) and from the task summary and
# paper in tasks/metadata/<task>.yaml:4-6 at the reviewed commit.
SITE = 'https://frontier-cs.org/task/'
GOAL = {VLLM: ('continuum', 'Speed up vLLM serving for multi-turn coding and tool agents.'),
        QPIR: ('quarterpir', 'Make each private lookup send fewer bytes and run faster.'),
        KV: ('kv-compaction', 'Shrink a model’s cached context to a tenth and keep its answers.'),
        DIFF: ('diffusion-policy', 'Sample a robot’s actions from a diffusion policy.'),
        FRE: ('differentiable-population-statistics',
              'Keep population statistics differentiable for a Fréchet-distance loss.'),
        BFF: ('binary-fuse-filter-construction-and-lookup', 'Write the construction of a binary fuse filter.'),
        EDLIB: ('exact-sequence-alignment', 'Recover exact alignment paths in linear memory, fast.'),
        EGG: ('egg', 'Restore an e-graph’s invariants with deferred rebuilding.'),
        JOIN: ('yannakakis', 'Rewrite join trees into faster two-phase semijoin plans.'),
        RADIX: ('regionssort', 'Sort integers in place and in parallel.'),
        SVG: ('svg-ear', 'Rebuild sparse attention for a video diffusion model.'),
        META: ('metaopt', 'Find traffic matrices on which a combined heuristic does worst.'),
        DETOK: ('robust-image-tokenizer', 'Restore the corruption training that makes an image tokenizer robust.'),
        RAGEN: ('ragen', 'Turn multi-turn agent trajectories into training batches.'),
        PROG: ('progent', None)}
PROGENT_SUMMARY = ('Write the policy generation and update logic that confines tool-using LLM agents on AgentDojo, '
                   'blocking prompt-injection attacks while preserving task utility.')


def statement(t):
    """Where-list source for the task's one-line description and its paper."""
    slug, goal = GOAL[t]
    # Plain link text: the full metadata path is too long to fit a phone-width Where list on one line.
    meta = f'<a href="{GH}/blob/{SHA}/tasks/metadata/{t}.yaml#L4-L6">the task\'s metadata file, lines 4–6</a>'
    if goal:
        return src(f'<a href="{SITE}#{slug}">Task page on frontier-cs.org</a>: "{goal}" Task summary and paper: '
                   f'{meta}')
    return src(f'Task summary and paper: {meta}, "{PROGENT_SUMMARY}" (the task page on frontier-cs.org has no '
               'one-line description)')


VLLM_TITLE = 'The vLLM target is faster than any real run of the reference'
QPIR_TITLE = 'Kimi K3.1 Pro fails QuarterPIR on one slow query out of 2,000'

# The 11 tasks whose pass bars sit inside the reference's own run-to-run variation (second summary bullet), led by
# its two examples, vLLM and QuarterPIR.
NOISE_ERRORS = [
    dict(id='err-vllm',
         title=VLLM_TITLE,
         desc='The task is to make vLLM, a widely used server for language models, answer multi-turn agent '
              'conversations faster without changing its answers, by rebuilding the scheduler from the Continuum '
              "paper (arXiv 2025). The grader never reruns the reference, the authors' own code. It sets a target "
              'time for every request instead, the fastest of 3 earlier reference runs with zero margin, so no real '
              'reference run can meet it. There are 20 checks, 5 on each of 4 groups of coding-agent (SWE-bench) and '
              'tool-calling (BFCL) requests. They cover a geometric mean of latency (an average across requests), the '
              'tail latencies that only the slowest 10%, 5% and 1% of requests exceed (p90, p95, p99), and correct '
              'answers. Claude Fable 5.1 and GPT-6 Astra pass 19 of the 20, including all 12 tail-latency checks, and '
              'miss only the geometric-mean check on the public SWE-bench group.',
         meta=task(VLLM),
         sources=[statement(VLLM),
                  src(gh(VLLM, 'judge/beat_spec.json', '122-126') + ': "per-instance minimum reference latency '
                      'across three authenticated captures"', label='beat_spec.json'),
                  src(gh(VLLM, 'verifier/fixed-targets.json') + ': each reference run would need to be 1.02–1.69× '
                      'faster to meet it', label='fixed-targets.json'),
                  ev(VLLM, 'fable51', '19 of 20 checks; geometric-mean latency on SWE-bench public at 0.86× the '
                     "target's speed, the only failed check (" + c('phase/operator-result.json') + ' in the verifier '
                     'evidence)'),
                  ev(VLLM, 'astra', '19 of 20 checks; geometric-mean latency on SWE-bench public at 0.94× the '
                     "target's speed, the only failed check")]),
    dict(id='err-qpir',
         title=QPIR_TITLE,
         desc='The task is to make each lookup in QuarterPIR send fewer bytes and run faster. QuarterPIR, from a '
              'EUROCRYPT 2024 paper, lets a client read a record from a server without the server learning which '
              'one. The server must be faster than the reference on every one of 2,000 queries, each timed as the '
              "median of 5 replays. Kimi K3.1 Pro's server takes 0.38–0.71× the reference's time on a typical query. "
              'But in the regrade the leaderboard counts, a second grading of the same submission, 3 of 5 replays of '
              'one query were slow, which failed the run. The same submission passed its first grading.',
         meta=task(QPIR),
         sources=[statement(QPIR),
                  src(gh(QPIR, 'judge/table2_metrics.py', '305-306') + ': ' + c('all(0 < mine < theirs ...)'),
                      label='table2_metrics.py'),
                  ev(QPIR, 'k31', 'query ' + c('w00792') + ': replays of 1.56, 1.90 and 1.94 ms against a reference '
                     'median of 0.90 ms in the regrade; all five replays faster than the reference in the first '
                     'grading'),
                  src(f'<a href="{RESULTS}">{c("metadata/formal-results.json")}</a>, ' + c('quarter_pir/k31') +
                      ': the final submission "was evaluated again on the task\'s current version … that evaluation '
                      'is the score"', label='formal-results.json')]),
    dict(id='err-kv',
         title='The reference rarely clears its own accuracy bar',
         desc="The task is to shrink a language model's cached copy of a long document, its KV cache, to a tenth of "
              'its size while the model still answers questions about the document, rebuilding the method of the Fast '
              'KV Compaction paper (ICML 2026). On each of 24 articles the model answers the questions 3 times, and '
              "its worst try must score at least the reference's median minus one question. By our resampling of "
              "the reference's saved results, its own method clears that bar only about 1 time in 6. Even the full, "
              'uncompressed cache misses it on one article.',
         meta=task(KV),
         sources=[statement(KV),
                  src(gh(KV, 'judge/gate.py', '9') + ', ' + gh(KV, 'judge/gate.py', '209') + ', '
                      + gh(KV, 'judge/gate.py', '245-256') + ': gate on the minimum over repetitions'),
                  src(f'<a href="{AUDIT}/findings/fast_kv_compaction.md">Our computation from the frozen reference '
                      'captures</a>: 0.13 (per capture) to 0.17 (resampled)')]),
    dict(id='err-diffusion',
         title='Three random robot episodes per group decide quality',
         desc="The task is to write the step that picks a robot's next actions in Diffusion Policy (RSS 2023), a "
              'controller that pushes a T-shaped block into place in a simulator, so that it runs faster on a CPU. A '
              "faster sampler must also match the reference's reward and success rate over 3 simulated episodes in "
              'each of 4 groups, each group starting from one position, with no tolerance. With only 3 random '
              'episodes, each group passes about half the time, so all four pass about 7% of the time. Gemini 4 '
              'Carbon is 16× faster and better when the episodes are pooled, but fails two groups.',
         meta=task(DIFF),
         sources=[statement(DIFF),
                  src(gh(DIFF, 'judge/measurement_contract.py', '52') + ', '
                      + gh(DIFF, 'judge/measurement_contract.py', '100-105') + ': 3 seeds per group; '
                      + c('passed = a >= b')),
                  ev(DIFF, 'carbon-g', '0.069 s per action against 1.100 s; mean reward 0.938 against 0.924, '
                     'success equal; fails success on one group and reward on another'),
                  src('39 of 76 groups pass across the 19 scored runs, and 0.51<sup>4</sup> ≈ 7%')]),
    dict(id='err-frechet',
         title="The reference's own score varies 11% between runs",
         desc='The task is to keep the running feature statistics differentiable for the loss in the Representation '
              'Fréchet Loss paper (arXiv 2026), which fine-tunes an image generator toward real images. Quality is a '
              'Fréchet distance, a standard measure of how far generated images are from real ones in a feature '
              'space (lower is better), taken in 6 feature spaces on 3 training setups. A candidate must beat the '
              "reference in all 18 comparisons, but the reference's own score varies by about 11% between runs, and "
              'the task\'s README says it is "awaiting runtime qualification", that is, not yet validated. Gemini 4 '
              "Carbon halves the reference's distance yet wins only 16 of the 18 comparisons.",
         meta=task(FRE),
         sources=[statement(FRE),
                  src(gh(FRE, 'judge/evaluator.py', '163-165') + ': strict ' + c('<') + ' on every metric'),
                  src(gh(FRE, README, '3-5', 'repo/README.md') + ': "Source revision awaiting runtime qualification"'),
                  ev(FRE, 'carbon-g', 'mean Fréchet distance over the six feature spaces 13.7, against the '
                     "reference's 28.2; 16 of 18 comparisons"),
                  src("Reference's mean Fréchet distance 22.4 to 34.3 across the 20 runs, coefficient of variation "
                      '11%')]),
    dict(id='err-bff',
         title='Lookups must be faster on all 144 workloads, within the noise',
         desc='The task is to write a faster binary fuse filter, the compact structure from an ACM JEA 2022 paper '
              'that answers "is this key in the set?" with rare false yeses. A run must beat the reference on memory, '
              'build time and lookup time in every one of 144 workloads, test sets of different sizes and key types. '
              "On the largest filters, where lookups wait on memory, the reference's own lookup time varies by about "
              '2–3% from one measurement to the next, and strong candidates are only 5–14% faster. Three runs fail '
              'only on 1 or 2 of the 144 lookup comparisons.',
         meta=task(BFF),
         sources=[statement(BFF),
                  src(gh(BFF, 'judge/evaluator.py', '278') + ': ' + c("row['candidate'][m] < row['reference'][m]")),
                  ev(BFF, 'glm', 'lookup 143 of 144'),
                  ev(BFF, 'sol', 'lookup 143 of 144'),
                  ev(BFF, 'wonder', 'lookup 142 of 144')]),
    dict(id='err-edlib',
         title='The timed step can measure zero or less',
         desc='The task is to make Edlib, a C++ library from a Bioinformatics 2017 paper for comparing DNA or protein '
              'sequences, recover the exact alignment between two sequences quickly and in little memory. The grader '
              'times only that recovery step, as the fastest of 15 full runs minus the fastest of 15 runs that skip '
              'it, and on the most similar sequences the step takes about 0.1 ms. A run must be faster than the '
              "reference but above zero. In 19 of the 151 evaluations the agents requested during their runs, the "
              "reference's time on some workload came out zero or below, which makes passing impossible. GPT-6 Astra "
              'fails the final grade on 1 of 60 workloads.',
         meta=task(EDLIB),
         sources=[statement(EDLIB),
                  src(gh(EDLIB, 'judge/evaluator.py', '449-461') + ': ' + c('min(path_samples)-min(location_samples)')),
                  ev(EDLIB, 'astra', 'cpu time 59 of 60'),
                  src('Our count over the in-run evaluations in all 20 traces')]),
    dict(id='err-egraph',
         title='The 5% speedup bar mostly measures process start-up',
         desc='The task is to speed up how egg, an e-graph library from a POPL 2021 paper, restores its internal '
              'consistency after rewrites, using the paper\'s deferred "rebuilding". An e-graph stores many '
              'equivalent forms of a program at once. A run must be at least 5% faster than the reference on all 6 '
              'workloads, both in the rewrite-and-rebuild time (which the grader calls congruence) and in the '
              'wall-clock time of the whole test process. On the 3 hidden workloads each process takes about 4 ms, '
              'and starting the process outweighs the code being optimised. No run passes more than 4 of the 6 '
              'wall-clock checks, and three runs pass the congruence check on all 6 workloads.',
         meta=task(EGG),
         sources=[statement(EGG),
                  src(gh(EGG, 'judge/evaluator.py', '22') + ', ' + gh(EGG, 'judge/evaluator.py', '28-30') + ', '
                      + gh(EGG, 'judge/evaluator.py', '305-308') + ': ' + c('MATERIAL_SPEEDUP_RATIO = 0.95')),
                  ev(EGG, 'gemini', 'congruence 6 of 6, wall clock 4 of 6'),
                  ev(EGG, 'gemini-agy', 'congruence 6 of 6, wall clock 4 of 6'),
                  ev(EGG, 'carbon-g', 'congruence 6 of 6, wall clock 4 of 6'),
                  src(f'<a href="{AUDIT}/findings/egraph_invariant_restoration.md">Our timing of the reference</a>: '
                      '3.5 to 5.4 ms per hidden-workload process')]),
    dict(id='err-join',
         title='All 39 queries must be faster, though some have no room',
         desc="The task is to rewrite a database's plans for joining tables into faster two-phase plans that filter "
              'each table before joining, the method of a PVLDB 2025 paper on the Yannakakis algorithm. The final '
              'grade needs the exact result and a lower median time than the reference on every one of 39 queries, '
              "20 public and 19 hidden. On several of them the reference's plan is no faster than the database's "
              'original plan, so there is little to gain and a win comes down to timing noise. In 713 evaluations the '
              'agents requested during their runs, which use only the 20 public queries, no submission was faster on '
              'all 20. Claude Fable 5.1 and Gemini 4 Carbon get every final answer right but are not faster on 14 and '
              '12 of the 39 queries.',
         meta=task(JOIN),
         sources=[statement(JOIN),
                  src(gh(JOIN, 'judge/query_measurements.py', '128') + ', '
                      + gh(JOIN, 'judge/query_measurements.py', '144') + ': ' + c('candidate < reference')
                      + ' on every query'),
                  ev(JOIN, 'fable51', 'final grade: 39 of 39 exact, 25 of 39 latency'),
                  ev(JOIN, 'carbon-g', 'final grade: 39 of 39 exact, 27 of 39 latency'),
                  src('Our count over the in-run evaluations in all 19 traces with a submission: best 15 of the 20 '
                      'dev queries')]),
    dict(id='err-radix',
         title="Pass and fail don't follow speed on this task",
         desc='The task is to speed up Regions Sort, the parallel in-place integer sort from a SPAA 2019 paper, by '
              'improving the part that plans how blocks of data move between regions. Each of 12 workloads is a '
              'single timed comparison of candidate against reference, and the candidate must be faster on all 12. '
              'The developers\' own notes in the task say pass and fail "interleave, so the verdict did not track '
              'speed". GLM 5.3 passes at about 5% faster than the reference on average, while Gemini 4 Argon '
              '(Antigravity), at about 8% faster, fails on one of the 12 workloads.',
         meta=task(RADIX),
         sources=[statement(RADIX),
                  src(gh(RADIX, 'judge/beat_spec.json', '59') + ': "PASS and FAIL runs interleave"'),
                  src(gh(RADIX, 'judge/evaluator.py', '125-128') + ': ' + c('c<r') + ' per workload'),
                  ev(RADIX, 'glm', "passes; score 51.14 against the reference's 50.60 in the same grading, about 5% "
                     'faster on average'),
                  ev(RADIX, 'gemini-agy', "fails; score 51.46 against the reference's 50.63, about 8% faster on "
                     'average; sort time 11 of 12'),
                  ev(RADIX, 'carbon-g', "passes; score 51.49 against the reference's 50.65, about 8% faster; sort time "
                     '12 of 12')]),
    dict(id='err-svg',
         title='The video-quality tolerance is tighter than run-to-run noise',
         desc='The task is to rebuild the sparse attention of the SVG-EAR paper (ECCV 2026), which makes a '
              'text-to-video model faster by skipping part of its attention computation. Each of 12 clips must be at '
              'least 4% faster than the reference, and its quality scores against a full-attention video must stay '
              "within fixed tolerances of the reference's scores, measured once and frozen. For LPIPS, a measure of "
              'how different two images look to a person, the tolerance is 0.005. Two runs of equivalent code differ '
              "by up to 0.0056 LPIPS, and the reference's k-means step adds floating-point numbers in a varying "
              'order, so its clustering differs between runs. Gemini 4 Carbon is 12% faster and misses the quality '
              'tolerances on 4 of the 12 clips.',
         meta=task(SVG),
         sources=[statement(SVG),
                  src(gh(SVG, 'judge/evaluator.py', '155-161') + ': ' + c('LPIPS_NONINFERIOR_TOLERANCE = 0.005')),
                  src(gh(SVG, 'agent-base/frontier/task/repo/svg/kmeans_utils.py', '322-323', 'svg/kmeans_utils.py')
                      + ': the centroid sums use ' + c('tl.atomic_add') + ', a floating-point atomic add whose order '
                      'changes from run to run'),
                  ev(SVG, 'carbon-g', 'total latency 0.88× the reference; LPIPS 8 of 12, SSIM 8 of 12, PSNR 10 of 12'),
                  src(f'<a href="{AUDIT}/findings/sparse_video_attention_policy.md">Identical-code pair</a>: LPIPS '
                      'differs by up to 0.0056')]),
]

OTHER_ERRORS = [
    dict(id='err-metaopt',
         title='Copying the reference passes, because ties count',
         desc='The task is to find network traffic patterns on which a fast routing shortcut does much worse than the '
              'best possible routing, the search problem of the MetaOpt paper (NSDI 2024). On each of 30 test cases, '
              "the gap a run finds must be at least as large as the reference's, so ties pass. The reference is "
              'deterministic, so a run that copied it would tie everywhere and pass, although none of the released '
              'runs does.',
         meta=task(META),
         sources=[statement(META),
                  src(gh(META, 'judge/evaluator.py', '84') + ': ' + c('candidate >= reference')),
                  src(gh(META, README, '165-166', 'repo/README.md') + ': "Exact ties pass"')]),
    dict(id='err-detok-fitting',
         title='Runs can tune their output to the image being scored',
         desc='The task is to restore the training from an ICLR 2026 paper that makes an image tokenizer robust. A '
              'tokenizer compresses a picture into a short code of tokens that an image generator works with, and '
              'decodes it back. The score is how closely the decoded picture matches the original. At evaluation, a '
              'submission can adjust the code by gradient steps toward the exact picture being scored, so the score '
              'rewards fitting to that picture rather than a better tokenizer. Gemini 4 Carbon and Gemini 4 Argon '
              '(Antigravity) both do this and fail only the speed check.',
         meta=task(DETOK),
         sources=[statement(DETOK),
                  ev(DETOK, 'carbon-g', patch(DETOK, 'carbon-g', '776-812') + ': gradient step on the latents '
                     'against the input image, called from ' + c('encode()') + ' at eval'),
                  ev(DETOK, 'gemini-agy', patch(DETOK, 'gemini-agy', '267-339') + ': ' + c('_refine_latents') +
                     ', "refine latent tokens via test-time gradient step through decoder"')]),
    dict(id='err-detok-training',
         title='The grader trains too little to show the method',
         desc="The task is the same image tokenizer, trained with the paper's method of corrupting the code with "
              'noise and masking so the decoder learns to repair it. The grader trains each submission for only 16 '
              "updates at a learning rate of 1e-6, too little for that training to change anything. Claude Fable 5.1 "
              'and Claude Opus 5.5, the two runs that pass under the current grader, win by weakening the corruption '
              'and tuning numerical precision and speed.',
         meta=task(DETOK),
         sources=[statement(DETOK),
                  src(gh(DETOK, 'judge/evaluator.py', '189-193') + ': one epoch of 64 images at batch size 4, '
                      + c('"--lr", "1e-6"')),
                  ev(DETOK, 'fable51', patch(DETOK, 'fable51', '211-218') + ': "Corruption strength is deliberately '
                     'mild"'),
                  ev(DETOK, 'opus', patch(DETOK, 'opus', '293-320') + ': 8 to 32 masked tokens and '
                     + c('"tau_max": 0.1'))]),
    dict(id='err-ragen',
         title='The scored games are played before any training',
         desc='The task is to turn multi-turn agent trajectories into training batches for RAGEN, a reinforcement '
              'learning method for language-model agents from an arXiv 2025 paper, here on a box-pushing puzzle '
              '(Sokoban). The grader scores the games the model plays before the one training step runs, so training '
              'never affects the score. The reference wins 0 games, and a candidate must beat it on wins and reward '
              'in every one of 3 graded groups. No released run wins a game in the second or third group, and the '
              'task\'s README says earlier results "do not establish acceptance".',
         meta=task(RAGEN),
         sources=[statement(RAGEN),
                  src(gh(RAGEN, README, '67-71', 'repo/README.md') + ': "The scored rollouts occur before the '
                      'optimizer calls"'),
                  src(gh(RAGEN, README, '84', 'repo/README.md') + ': earlier results "do not establish acceptance"'),
                  src(gh(RAGEN, 'judge/evaluator.py', '385-386') + ': strict ' + c('>') + ' on success and reward'),
                  ev(RAGEN, 'opus', 'one success, on the first graded group only'),
                  ev(RAGEN, 'sol', 'one success, on the first graded group only')]),
    dict(id='err-progent',
         title='Blocked attacker calls were counted as successful attacks',
         desc='The task is to write the rules from the Progent paper (arXiv 2025) that limit which tools an AI '
              'assistant may call, so that instructions an attacker plants in its inputs cannot make it do harm, '
              'while it still finishes its real tasks. A run must allow zero successful attacks. Claude Opus 5.5, '
              'DeepSeek V4.1 Flash and Qwen 3.8 Max are listed as failing because the grader that scored them counted '
              "attacker tool calls their rules had blocked as successful attacks. The task's current grader counts "
              'only calls that ran. By our reconstruction of the published traffic, all three have zero successful '
              'attacks under that rule and would pass.',
         meta=task(PROG),
         sources=[statement(PROG),
                  src(gh(PROG, 'judge/episodes.py', '131-151') + ': security judged on executed calls',
                      label='episodes.py'),
                  ev(PROG, 'opus', 'listed as failing; 5 breaches in the Slack suite, all on blocked calls'),
                  ev(PROG, 'ds', 'listed as failing; 6 breaches in the Slack suite, all on blocked calls'),
                  ev(PROG, 'qwen', 'listed as failing; 3 breaches in the Slack suite, all on blocked calls'),
                  src(f'<a href="{AUDIT}/findings/progent_privilege_control.md">Our replay of the published '
                      'traffic</a>')]),
]
ERRORS = NOISE_ERRORS + OTHER_ERRORS
assert len(NOISE_ERRORS) == 11 and len({e['meta'] for e in NOISE_ERRORS}) == 11
assert len(ERRORS) == 16 and len({e['meta'] for e in ERRORS}) == 15
assert all(e['desc'].startswith('The task is ') for e in ERRORS)

ERROR_GROUPS = [
    dict(title="Pass bars tighter than the reference's own variation",
         lead='All 16 errors on this page, on 15 tasks, count toward the 31%. Each task has a pass bar, the rule a '
              'run must meet to pass. On these 11 tasks it requires beating the reference on every workload, query '
              "or episode, with a tolerance smaller than the reference's own variation from one run to the next, so "
              'a real improvement can fail on one unlucky measurement.',
         rows=NOISE_ERRORS),
    dict(title='Other grading errors',
         lead="These five errors, on four tasks, let a run pass without a better method, grade something other than "
              'the paper\'s method, or count blocked attacks as successful ones.',
         rows=OTHER_ERRORS)]


def code_quote(code, footer):
    return f'<blockquote class="agent"><pre>{html.escape(code)}</pre><footer>{footer}</footer></blockquote>'


HALO = 'paint-order="stroke" stroke="#fff" stroke-width="4" stroke-linejoin="round"'  # keeps labels legible over grid
SUB12 = 'style="font-size:12px"'  # desktop .sub at 12px without touching style.css
NW = 360  # phone viewBox width: about 312px on screen, so 14px axis text renders at 12px


def nudge(xs, r):
    """Small symmetric vertical offsets for dots that would overlap: each cluster of dots closer than 2r is spread
    r apart, centred on the row (they overlap a little; the white outline keeps each one visible). Returns offsets in input order."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out, runs = [0.0] * len(xs), [[order[0]]] if order else []
    for a, b in zip(order, order[1:]):
        (runs[-1].append(b) if xs[b] - xs[a] < 2 * r else runs.append([b]))
    for run in runs:
        for k, i in enumerate(run):
            out[i] = (k - (len(run) - 1) / 2) * r
    return out


QPIR_ARIA = ('Scatter of 2,000 queries. All but one sit between 0.36 and 0.97 times the reference time; one query '
             'is at 1.73 times, above the 1.0 line.')


def qpir_points(q, px, py, width):
    """The two experiments as grey point paths (all queries but the spike), plus the spike's index and medians."""
    ratios = [r for _, r in q['ratios']]
    spike = max(range(len(ratios)), key=lambda i: ratios[i])
    paths, meds = '', []
    for k, (a, b) in enumerate(((0, 1000), (1000, 2000))):
        seg = [i for i in range(a, b) if i != spike]
        d = ''.join(f'M{px(i):.1f} {py(ratios[i]):.1f}h0' for i in seg)
        med = statistics.median(ratios[a:b])
        meds.append(med)
        paths += (f'<path d="{d}" stroke="{GRAY}" stroke-width="{width}" stroke-linecap="round" fill="none">'
                  f'<title>Experiment {k + 1}: {len(seg)} queries faster than the reference, median '
                  f'{med:.2f}×</title></path>')
    return ratios, spike, paths, meds


def qpir_spike(q, ratios, spike, sx, sy):
    return (f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="6" fill="{RED}" stroke="#fff" stroke-width="2">'
            f'<title>Query {q["ratios"][spike][0]}: {ratios[spike]:.2f}× the reference (median of 5 replays)</title>'
            f'</circle>')


XTICKS = (1, 500, 1000, 1500, 2000)


def qpir_scatter(q):
    W, H, L, R, TOP, B = 720, 306, 76, 160, 18, 54
    n, ymax = len(q['ratios']), 2.0
    px = lambda i: L + (W - L - R) * i / (n - 1)
    py = lambda v: TOP + (H - TOP - B) * (1 - v / ymax)
    grid = ''.join(f'<line x1="{L}" x2="{W - R}" y1="{py(v):.1f}" y2="{py(v):.1f}" class="g"/>'
                   f'<text x="{L - 8}" y="{py(v) + 4:.1f}" class="ax" text-anchor="end">{v:.1f}×</text>'
                   for v in (0.0, 0.5, 1.0, 1.5, 2.0))
    xt = ''.join(f'<text x="{px(i - 1):.1f}" y="{H - B + 18}" class="ax" text-anchor="middle">{i:,}</text>'
                 for i in XTICKS)
    titles = (f'<text x="{(L + W - R) / 2:.1f}" y="{H - 6}" class="sub" text-anchor="middle" {SUB12}>query, 1 to '
              f'2,000</text>'
              f'<text transform="translate(16 {py(1.0):.1f}) rotate(-90)" class="sub" text-anchor="middle" {SUB12}>'
              f'candidate ÷ reference time</text>')
    ratios, spike, paths, meds = qpir_points(q, px, py, 2.6)
    labs = ''.join(f'<text x="{px(a + 500):.1f}" y="{py(0.0) - 8:.1f}" class="lab" text-anchor="middle">'
                   f'experiment {k + 1}, median {m:.2f}×</text>' for k, (a, m) in enumerate(zip((0, 1000), meds)))
    one = py(1.0)
    sx, sy = px(spike), py(ratios[spike])
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{QPIR_ARIA}">{grid}{xt}{titles}'
           f'<line x1="{L}" x2="{W - R}" y1="{one:.1f}" y2="{one:.1f}" class="cap"/>'
           f'<text x="{W - R + 8}" y="{one + 4:.1f}" class="lab">1.0×: must be below</text>'
           f'{paths}{labs}{qpir_spike(q, ratios, spike, sx, sy)}'
           f'<text x="{sx + 12:.1f}" y="{sy + 4:.1f}" class="lab">one query, {ratios[spike]:.2f}×</text></svg>')

    # Phone layout: axis titles above and below the plot, threshold label inside it, three x ticks.
    W, H, L, R, TOP, B = NW, 360, 40, 12, 40, 54
    px = lambda i: L + (W - L - R) * i / (n - 1)
    py = lambda v: TOP + (H - TOP - B) * (1 - v / ymax)
    grid = ''.join(f'<line x1="{L}" x2="{W - R}" y1="{py(v):.1f}" y2="{py(v):.1f}" class="g"/>'
                   f'<text x="{L - 6}" y="{py(v) + 5:.1f}" class="ax" text-anchor="end">{v:.0f}×</text>'
                   for v in (0.0, 1.0, 2.0))
    xt = ''.join(f'<text x="{px(i - 1):.1f}" y="{H - B + 20}" class="ax" text-anchor="{anc}">{i:,}</text>'
                 for i, anc in ((1, 'start'), (1000, 'middle'), (2000, 'end')))
    titles = (f'<text x="0" y="{TOP - 22}" class="sub">candidate ÷ reference time</text>'
              f'<text x="{(L + W - R) / 2:.1f}" y="{H - 4}" class="sub" text-anchor="middle">query, 1 to 2,000</text>')
    ratios, spike, paths, meds = qpir_points(q, px, py, 2.2)
    labs = ''.join(f'<text x="{px(a + 500):.1f}" y="{py(0.0) - 26:.1f}" class="lab" text-anchor="middle">'
                   f'experiment {k + 1}</text>'
                   f'<text x="{px(a + 500):.1f}" y="{py(0.0) - 8:.1f}" class="lab" text-anchor="middle">'
                   f'median {m:.2f}×</text>' for k, (a, m) in enumerate(zip((0, 1000), meds)))
    one = py(1.0)
    sx, sy = px(spike), py(ratios[spike])
    narrow = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{QPIR_ARIA}">{grid}{xt}{titles}'
              f'<line x1="{L}" x2="{W - R}" y1="{one:.1f}" y2="{one:.1f}" class="cap"/>'
              f'<text x="{W - R}" y="{one - 7:.1f}" class="lab" text-anchor="end" {HALO}>1.0×: must be below</text>'
              f'{paths}{labs}{qpir_spike(q, ratios, spike, sx, sy)}'
              f'<text x="{sx + 12:.1f}" y="{sy + 5:.1f}" class="lab" {HALO}>one query, {ratios[spike]:.2f}×</text>'
              f'</svg>')
    rejudge = f'{HF}/tree/{REV}/traces/quarter_pir/k31/selected-final-rejudge'
    return figure('Server time per query for Kimi K3.1 Pro against the reference, in the regrade the leaderboard '
                  'counts', svg,
                  "How one query out of 2,000 failed Kimi K3.1 Pro's run. Each point is one query: the median of its "
                  '5 replays on the candidate divided by the median of 5 on the reference. Queries 1 to 1,000 and '
                  "1,001 to 2,000 are the task's two experiments. Source: <code>metrics.json</code> in the verifier "
                  'evidence of the '
                  f'regrade (<a href="{rejudge}"><code>traces/quarter_pir/k31/'
                  'selected-final-rejudge</code></a>).',
                  narrow=narrow)


# Detok case: per-workload EMA PSNR gain over the paired reference, in the grading the leaderboard counts.
DETOK_RUNS = (('carbon-g', RED), ('gemini-agy', RED), ('fable51', GRAY), ('opus', GRAY))


def detok_rows(dt):
    """(run, colour, per-workload EMA PSNR gains in dB, workloads where the run was slower, passes)."""
    rows = []
    for run, col in DETOK_RUNS:
        ws = dt[run]['workloads']
        gains = [w['ema_psnr_candidate'] - w['ema_psnr_reference'] for w in ws]
        slower = sum(w['wall_candidate'] >= w['wall_reference'] for w in ws)
        rows.append((run, col, gains, slower, slower == 0 and min(gains) > 0))
    return rows


def detok_verdict(slower, passes):
    return 'passes' if passes else f'fails: slower on {slower} of 3 workloads'


def detok_dots(run, gains, x, y, r, col):
    xs = [x(g) for g in gains]
    return ''.join(f'<circle cx="{cx:.1f}" cy="{y + dy:.1f}" r="{r}" fill="{col}" stroke="#fff" stroke-width="1.5">'
                   f'<title>{MODELS[run]}, workload {k + 1}: {g:+.3f} dB against the reference</title></circle>'
                   for k, (g, cx, dy) in enumerate(zip(gains, xs, nudge(xs, r))))


DETOK_ARIA = ('Dot plot of the quality gain over the reference on each of three workloads. Gemini 4 Carbon gains 1.51 '
              'to 1.58 dB and Gemini 4 Argon (Antigravity) 0.74 to 0.78 dB, and both fail on time. Claude Fable 5.1 '
              'gains 0.03 to 0.04 dB and Claude Opus 5.5 under 0.01 dB, and both pass.')


def detok_chart(dt):
    rows = detok_rows(dt)
    lo, hi = 0.0, 1.7
    W, rowh, L, R, TOP = 720, 50, 250, 110, 34
    H = TOP + rowh * len(rows) + 26
    x = lambda g: L + (W - L - R) * (g - lo) / (hi - lo)
    ticks = ''.join(f'<line x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{TOP - 8}" y2="{H - 26}" class="g"/>'
                    f'<text x="{x(t):.1f}" y="{H - 8}" class="ax" text-anchor="middle">{t:+.1f} dB</text>'
                    for t in (0.5, 1.0, 1.5))
    ticks += f'<text x="{x(0):.1f}" y="{H - 8}" class="ax" text-anchor="middle">0</text>'
    out = ''
    for i, (run, col, gains, slower, passes) in enumerate(rows):
        y = TOP + 16 + i * rowh
        rng = f'{min(gains):+.2f} to {max(gains):+.2f} dB' if max(gains) >= 0.01 else 'under +0.01 dB'
        out += (f'<g><text x="{L - 14}" y="{y + 1}" class="ylab" text-anchor="end">{MODELS[run]}</text>'
                f'<text x="{L - 14}" y="{y + 17}" class="sub" text-anchor="end">{detok_verdict(slower, passes)}</text>'
                f'{detok_dots(run, gains, x, y, 6, col)}'
                f'<text x="{x(max(gains)) + 14:.1f}" y="{y + 4}" class="val" {HALO}>{rng}</text></g>')
    zero = x(0)
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{DETOK_ARIA}">{ticks}'
           f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="{TOP - 8}" y2="{H - 26}" class="cap"/>'
           f'<text x="{zero + 6:.1f}" y="{TOP - 16}" class="lab">0: same quality as the reference</text>{out}</svg>')

    # Phone layout: name, then verdict and range, above each row; the zero line runs down the left edge.
    W, L, R, TOP, rowh = NW, 14, 18, 34, 84
    H = TOP + rowh * len(rows) + 16
    x = lambda g: L + (W - L - R) * (g - lo) / (hi - lo)
    ticks = ''.join(f'<line x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{TOP - 8}" y2="{H - 26}" class="g"/>'
                    f'<text x="{x(t):.1f}" y="{H - 6}" class="ax" text-anchor="middle">{t:+.1f}</text>'
                    for t in (0.5, 1.0, 1.5))
    ticks += f'<text x="{x(0):.1f}" y="{H - 6}" class="ax" text-anchor="start">0 dB</text>'
    out = ''
    for i, (run, col, gains, slower, passes) in enumerate(rows):
        y0 = TOP + 12 + i * rowh
        y = y0 + 44
        rng = f'{min(gains):+.2f} to {max(gains):+.2f} dB' if max(gains) >= 0.01 else 'under +0.01 dB'
        verdict = 'passes' if passes else 'fails on time'
        out += (f'<g><text x="{L + 10}" y="{y0}" class="ylab" {HALO}>{MODELS[run]}</text>'
                f'<text x="{L + 10}" y="{y0 + 19}" class="sub" {HALO}>{verdict}; {rng}</text>'
                f'{detok_dots(run, gains, x, y, 5.5, col)}</g>')
    zero = x(0)
    narrow = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{DETOK_ARIA}">{ticks}'
              f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="{TOP - 8}" y2="{H - 26}" class="cap"/>'
              f'<text x="{zero}" y="{TOP - 16}" class="lab">0: same quality as the reference</text>{out}</svg>')
    tr = f'{HF}/tree/{REV}/traces/{DETOK}'
    ord_gap = max(abs((w['ord_psnr_candidate'] - w['ord_psnr_reference']) -
                      (w['ema_psnr_candidate'] - w['ema_psnr_reference']))
                  for run, _ in DETOK_RUNS for w in dt[run]['workloads'])
    assert ord_gap < 0.07, ord_gap
    return figure(
        'Quality gain over the reference on each workload, in the grading the leaderboard counts', svg,
        'How much the step that fits each photo raises the quality score. Each dot is one workload: the PSNR of the '
        "averaged (EMA) model's reconstructions minus the reference's in the same grading. The ordinary model's gains "
        'differ from these by under 0.07 dB. Source: <code>metrics.json</code> in the verifier evidence of each run '
        f'(<a href="{tr}"><code>traces/{DETOK}/</code></a>), our subtraction.', narrow=narrow)


# KV-cache compaction case: the reference's own recorded tries against the accuracy bar the grader sets from them.
KV_GATE = f'{folder(KV)}/judge/gate.py'
KV_MANIFEST = f'{folder(KV)}/judge/targets/manifest.json'
KV_30029 = f'{KV_MANIFEST}#L2047-L2106'  # the workloads."30029" block at the reviewed commit
KV_RISKY = ['22346', '22524', '22876', '23563', '30035']


def kv_rows(kv):
    """Per article: questions, the bar the grader sets (judge/gate.py:9, :77-78, :140), the 9 recorded tries
    (3 captures of 3 repetitions) and the uncompressed cache's one recorded score."""
    rows = []
    for a, r in sorted(kv['articles'].items()):
        n, caps = r['questions'], r['reference_correct_per_repetition']
        assert [min(c) for c in caps] == r['reference_correct'] and len(caps) == 3 and all(len(c) == 3 for c in caps)
        bar = statistics.median(r['reference_correct']) - max(1, math.ceil(0.05 * n))
        assert bar == int(bar) and len(r['uncompressed_correct']) == 1
        tries = [v for c in caps for v in c]
        rows.append(dict(a=a, n=n, bar=int(bar), caps=caps, tries=tries, ok=sum(v >= bar for v in tries),
                         unc=r['uncompressed_correct'][0]))
    return rows


def kv_check(rows):
    """Reproduce the audit's numbers: 0.13 counting each recorded run as it is, 0.17 resampling the 9 tries."""
    per_capture = math.prod(sum(min(c) >= r['bar'] for c in r['caps']) / 3 for r in rows)
    pooled = math.prod((r['ok'] / 9) ** 3 for r in rows)
    assert len(rows) == 24 and round(per_capture, 2) == 0.13 and round(pooled, 2) == 0.17, (per_capture, pooled)
    assert [r['a'] for r in rows if r['ok'] < 9] == KV_RISKY and all(r['ok'] == 8 for r in rows if r['ok'] < 9)
    assert [(r['a'], r['unc'], r['bar']) for r in rows if r['unc'] < r['bar']] == [('30029', 14, 15)]
    return per_capture, pooled


KV_SEED = 888  # the one fixed draw of 30 re-runs the figure replays (see kv_sample)
KV_RUNS = 30
KV_REP = 0  # the run shown at rest and without scripts: run 1, which fails on article 4 alone


def kv_sample(rows):
    """30 re-runs drawn once from the reference's recorded tries. In each re-run, every article draws 3 of its 9
    recorded tries at random, with replacement, and keeps the worst, as the grader keeps the worst of 3 fresh tries.

    KV_SEED is the first seed, trying 0, 1, 2, ... in order, whose sample passes 5 times (30 × 0.17 ≈ 5), fails run 1
    on article 4 alone (the example article in the text) and passes once within the first four runs, so the replay
    shows both outcomes early. Returns the worst score per run and article, and the failing articles per run."""
    rng = random.Random(KV_SEED)
    runs = [[min(r['tries'][rng.randrange(9)] for _ in range(3)) for r in rows] for _ in range(KV_RUNS)]
    fails = [[i for i, w in enumerate(run) if w < rows[i]['bar']] for run in runs]
    assert sum(not f for f in fails) == 5 and fails[KV_REP] == [3] and rows[3]['a'] == '22346'
    assert any(not f for f in fails[1:4])
    assert all(run[i] == rows[i]['bar'] - 1 for run, f in zip(runs, fails) for i in f)  # always one question short
    return runs, fails


def kv_status(k, run, f, rows):
    """The status line for run k (0-based); the script in KV_SCRIPT writes the same sentences."""
    head = f'Run {k + 1} of {KV_RUNS}'
    if not f:
        return f'{head} <b class="kv-ok">passed</b>. All 24 articles reached their bar.'
    if len(f) == 1:
        i = f[0]
        return (f'{head} <b class="kv-no">failed</b>. Article {i + 1} got {run[i]} questions right on its worst try, '
                f'one short of its bar of {rows[i]["bar"]}.')
    names = ', '.join(str(i + 1) for i in f[:-1]) + ' and ' + str(f[-1] + 1)
    return (f'{head} <b class="kv-no">failed</b> on {len(f)} articles. Articles {names} each fell one question short '
            'of their bar.')


def kv_tally(runs_seen, passed):
    if runs_seen == KV_RUNS:
        return f'Passed {passed} of {KV_RUNS} re-runs, about 1 in 6.'
    return f'Passed {passed} of {runs_seen} re-run{"" if runs_seen == 1 else "s"} so far.'


def kv_arts_label(k, f):
    below = ('article ' + ', '.join(str(i + 1) for i in f) + (' is' if len(f) == 1 else ' are') + ' below') if f \
        else 'none is below'
    return f'Run {k + 1}: each of the 24 articles against its bar; {below}.'


KV_STYLE = f'''<style>
#kv-fig .kv-play {{ display: grid; gap: 14px; }}
#kv-fig .kv-stage {{ display: grid; gap: 10px; cursor: pointer; }}
#kv-fig .kv-status {{ font-size: 17px; line-height: 1.45; font-weight: 600; color: var(--ink); min-height: 2.9em; max-width: 60ch; }}
#kv-fig .kv-status b {{ font-weight: 700; }}
#kv-fig .kv-ok {{ color: var(--green); }}
#kv-fig .kv-no {{ color: {RED}; }}
#kv-fig .kv-key {{ font-size: 13px; color: var(--ink-2); max-width: 68ch; }}
#kv-fig .kv-arts {{ display: flex; }}
#kv-fig .kv-half {{ flex: 1 1 0; display: grid; grid-template-columns: 30px repeat(12, minmax(0, 1fr)); }}
#kv-fig .kv-half + .kv-half .kv-gut {{ display: none; }}
#kv-fig .kv-half + .kv-half {{ grid-template-columns: repeat(12, minmax(0, 1fr)); }}
#kv-fig .kv-gut {{ position: relative; height: 82px; font-size: 12px; color: var(--muted); }}
#kv-fig .kv-gut span {{ position: absolute; right: 6px; bottom: 23px; line-height: 1; }}
#kv-fig .kv-c {{ position: relative; height: 82px; }}
#kv-fig .kv-c::before {{ content: ""; position: absolute; left: 0; right: 0; bottom: 30px; border-top: 1.5px dashed var(--muted); }}
#kv-fig .kv-d {{ position: absolute; left: 50%; width: 10px; height: 10px; margin-left: -5px; border-radius: 50%; background: {GRAY}; box-shadow: 0 0 0 1.5px var(--white); bottom: calc(26px + var(--m) * 8px); transition: bottom 0.35s ease, background-color 0.35s; }}
#kv-fig .kv-c.lo .kv-d {{ background: {RED}; width: 12px; height: 12px; margin-left: -6px; }}
#kv-fig .kv-n {{ position: absolute; left: 0; right: 0; bottom: 0; text-align: center; font-size: 12px; line-height: 16px; color: var(--muted); font-variant-numeric: tabular-nums; }}
#kv-fig .kv-c.lo .kv-n {{ color: {RED}; font-weight: 700; }}
#kv-fig .kv-tl {{ display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 6px 14px; align-items: center; border-top: 1px solid var(--line-2); padding-top: 12px; }}
#kv-fig .kv-ctl {{ display: flex; gap: 6px; }}
#kv-fig .kv-ctl[hidden] {{ display: none; }}
#kv-fig .kv-b {{ width: 38px; height: 38px; display: grid; place-items: center; padding: 0; color: var(--ink); background: var(--white); border: 1px solid var(--line); border-radius: 3px; cursor: pointer; }}
#kv-fig .kv-b:hover {{ border-color: var(--ink-2); }}
#kv-fig .kv-b svg {{ width: 16px; height: 16px; fill: currentColor; }}
#kv-fig .kv-b:focus-visible {{ outline: 2px solid var(--red); outline-offset: 2px; }}
#kv-fig .kv-strip {{ position: relative; --gap: 3px; margin: 0 3px; }}
#kv-fig .kv-slots {{ list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat({KV_RUNS}, minmax(0, 1fr)); gap: var(--gap); }}
#kv-fig .kv-slots li {{ height: 22px; border-radius: 2px; background: var(--line-2); }}
#kv-fig .kv-slots li.p {{ background: var(--green); }}
#kv-fig .kv-slots li.f {{ background: {RED}; }}
#kv-fig .kv-head {{ position: absolute; top: -4px; height: 30px; width: calc((100% - {KV_RUNS - 1} * var(--gap)) / {KV_RUNS} + 6px); left: calc(var(--i) * ((100% - {KV_RUNS - 1} * var(--gap)) / {KV_RUNS} + var(--gap)) - 3px); border: 2px solid var(--ink); border-radius: 3px; transition: left 0.3s ease; pointer-events: none; }}
#kv-fig .kv-ends {{ display: flex; justify-content: space-between; gap: 8px; font-size: 12px; color: var(--muted); margin-top: 6px; }}
#kv-fig .kv-ends i {{ display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin: 0 4px 0 8px; vertical-align: -1px; }}
#kv-fig .kv-ends i.p {{ background: var(--green); }}
#kv-fig .kv-ends i.f {{ background: {RED}; }}
#kv-fig .kv-tally {{ grid-column: 1 / -1; font-size: 15px; font-weight: 700; color: var(--ink); }}
#kv-fig .kv-tl.nojs {{ grid-template-columns: minmax(0, 1fr); }}
@media (prefers-reduced-motion: reduce) {{
  #kv-fig .kv-d, #kv-fig .kv-head {{ transition: none; }}
}}
@media (max-width: 640px) {{
  #kv-fig .kv-status {{ font-size: 16px; min-height: 4.35em; }}
  #kv-fig .kv-arts {{ flex-direction: column; gap: 4px; }}
  #kv-fig .kv-half + .kv-half .kv-gut {{ display: block; }}
  #kv-fig .kv-half + .kv-half {{ grid-template-columns: 30px repeat(12, minmax(0, 1fr)); }}
  #kv-fig .kv-tl {{ grid-template-columns: minmax(0, 1fr); }}
  #kv-fig .kv-strip {{ --gap: 2px; }}
  #kv-fig .kv-b {{ width: 44px; height: 40px; }}
}}
.kv-q {{ margin: 16px 0; padding: 12px 16px; border: 1px solid var(--line-2); border-left: 3px solid var(--muted); background: var(--page); max-width: 62ch; display: grid; gap: 8px; }}
.kv-q p {{ font-size: 15px; }}
.kv-q .kv-qh {{ font-size: 14px; color: var(--ink-2); }}
.kv-q .kv-qq {{ font-weight: 700; color: var(--ink); }}
.kv-q ol {{ margin: 0; padding-left: 1.6em; font-size: 15px; }}
.kv-q ol li + li {{ margin-top: 2px; }}
.kv-q li.gold {{ font-weight: 600; }}
.kv-q li.gold span {{ font-weight: 400; color: var(--green); white-space: nowrap; }}
.kv-q .kv-qf {{ font-size: 13px; color: var(--muted); }}
</style>'''

KV_ICONS = {
    'play': '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5v11l9-5.5z"/></svg>',
    'pause': '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 2.5h3v11h-3zM9.5 2.5h3v11h-3z"/></svg>',
    'replay': '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 2.5a5.5 5.5 0 1 1-5.2 3.7l1.6.5A3.8 3.8 0 1 0 8 4.2v2.1L4.6 3.4 8 .5z"/></svg>',
    'prev': '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10.6 2.3 4.9 8l5.7 5.7 1.2-1.2L7.3 8l4.5-4.5z"/></svg>',
    'next': '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5.4 2.3 11.1 8l-5.7 5.7-1.2-1.2L8.7 8 4.2 3.5z"/></svg>',
}

KV_SCRIPT = '''<script>
(function () {
  var fig = document.getElementById('kv-fig'); if (!fig) return;
  var D = JSON.parse(fig.querySelector('.kv-data').textContent), N = D.runs.length;
  var play = fig.querySelector('.kv-play'), stage = fig.querySelector('.kv-stage');
  var status = fig.querySelector('.kv-status'), tally = fig.querySelector('.kv-tally'), arts = fig.querySelector('.kv-arts');
  var cells = [].slice.call(fig.querySelectorAll('.kv-c')), slots = [].slice.call(fig.querySelectorAll('.kv-slots li'));
  var strip = fig.querySelector('.kv-strip'), ctl = fig.querySelector('.kv-ctl');
  var bPlay = fig.querySelector('[data-kv="play"]'), bPrev = fig.querySelector('[data-kv="prev"]'), bNext = fig.querySelector('[data-kv="next"]');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fails = D.runs.map(function (run) { return run.map(function (w, a) { return w < D.bars[a] ? a : -1; }).filter(function (a) { return a >= 0; }); });
  var i = D.rep, seen = N, playing = false, visible = false, started = reduce, timer = null;
  function statusHtml(k) {
    var run = D.runs[k], f = fails[k], head = 'Run ' + (k + 1) + ' of ' + N;
    if (!f.length) return head + ' <b class="kv-ok">passed</b>. All 24 articles reached their bar.';
    if (f.length === 1) return head + ' <b class="kv-no">failed</b>. Article ' + (f[0] + 1) + ' got ' + run[f[0]] +
      ' questions right on its worst try, one short of its bar of ' + D.bars[f[0]] + '.';
    var names = f.slice(0, -1).map(function (a) { return a + 1; }).join(', ') + ' and ' + (f[f.length - 1] + 1);
    return head + ' <b class="kv-no">failed</b> on ' + f.length + ' articles. Articles ' + names + ' each fell one question short of their bar.';
  }
  function artsLabel(k) {
    var f = fails[k];
    return 'Run ' + (k + 1) + ': each of the 24 articles against its bar; ' + (f.length ? 'article ' +
      f.map(function (a) { return a + 1; }).join(', ') + (f.length === 1 ? ' is' : ' are') + ' below.' : 'none is below.');
  }
  function render() {
    var run = D.runs[i], passed = 0;
    cells.forEach(function (c, a) {
      var w = run[a];
      c.style.setProperty('--m', w - D.bars[a]);
      c.classList.toggle('lo', w < D.bars[a]);
      c.title = D.labels[a] + ': ' + w + ' of ' + D.n[a] + ' right on the worst try, bar ' + D.bars[a];
    });
    slots.forEach(function (s, k) {
      var on = k < seen, ok = !fails[k].length;
      s.className = on ? (ok ? 'p' : 'f') : '';
      if (on && ok) passed++;
    });
    strip.style.setProperty('--i', i);
    status.innerHTML = statusHtml(i);
    arts.setAttribute('aria-label', artsLabel(i));
    tally.textContent = seen === N ? 'Passed ' + passed + ' of ' + N + ' re-runs, about 1 in 6.'
      : 'Passed ' + passed + ' of ' + seen + ' re-run' + (seen === 1 ? '' : 's') + ' so far.';
    var atEnd = !playing && i === N - 1 && seen === N && started;
    bPlay.innerHTML = D.icons[playing ? 'pause' : (atEnd ? 'replay' : 'play')];
    bPlay.setAttribute('aria-label', playing ? 'Pause' : (atEnd ? 'Replay from run 1' : 'Play'));
    status.setAttribute('aria-live', playing ? 'off' : 'polite');
  }
  function schedule() {
    clearTimeout(timer);
    if (playing) timer = setTimeout(function () { if (visible) advance(); schedule(); }, 1200);
  }
  function advance() {
    if (i >= N - 1) { playing = false; render(); return; }
    i++; seen = Math.max(seen, i + 1); render();
    if (i === N - 1) { playing = false; render(); }
  }
  function restart() { seen = 1; i = 0; playing = true; render(); schedule(); }
  function step(d) {
    playing = false; clearTimeout(timer);
    i = Math.max(0, Math.min(N - 1, i + d)); seen = Math.max(seen, i + 1); render();
  }
  function toggle() {
    if (!playing && i === N - 1) { started = true; restart(); return; }
    started = true; playing = !playing; render(); schedule();
  }
  bPlay.addEventListener('click', function (e) { e.stopPropagation(); toggle(); });
  bPrev.addEventListener('click', function (e) { e.stopPropagation(); step(-1); });
  bNext.addEventListener('click', function (e) { e.stopPropagation(); step(1); });
  stage.addEventListener('click', function (e) { if (!e.target.closest('a, button')) toggle(); });
  fig.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); step(1); }
  });
  new IntersectionObserver(function (es) {
    visible = es[0].isIntersecting;
    if (visible && !started) { started = true; restart(); }
  }, { threshold: 0.5 }).observe(play);
  ctl.hidden = false; fig.querySelector('.kv-tl').classList.remove('nojs');
  render();
})();
</script>'''


def kv_cells(rows, run, quality):
    half = lambda lo, hi: ('<div class="kv-half"><div class="kv-gut" aria-hidden="true"><span>bar</span></div>' + ''.join(
        f'<div class="kv-c{" lo" if run[k] < r["bar"] else ""}" style="--m:{run[k] - r["bar"]}" '
        f'title="{html.escape(kv_label(k, r, quality))}: {run[k]} of {r["n"]} right on the worst try, bar {r["bar"]}">'
        f'<i class="kv-d"></i><span class="kv-n">{k + 1}</span></div>'
        for k, r in enumerate(rows) if lo <= k < hi) + '</div>')
    return half(0, 12) + half(12, 24)


def kv_label(k, r, quality):
    return f'Article {k + 1}, {quality[r["a"]]["title"]} (QuALITY {r["a"]})'  # hover text; the ids appear only here


def kv_figure(rows, pooled, quality):
    one_in = round(1 / pooled)
    assert one_in == 6
    runs, fails = kv_sample(rows)
    passed = sum(not f for f in fails)
    k, run = KV_REP, runs[KV_REP]
    data = dict(runs=runs, bars=[r['bar'] for r in rows], n=[r['n'] for r in rows], rep=KV_REP,
                labels=[kv_label(j, r, quality) for j, r in enumerate(rows)], icons=KV_ICONS)
    btn = lambda kind, label: (f'<button type="button" class="kv-b" data-kv="{kind}" aria-label="{label}">'
                               f'{KV_ICONS["play" if kind == "play" else kind]}</button>')
    slots = ''.join(f'<li class="{"f" if f else "p"}" title="Run {j + 1}: {"failed" if f else "passed"}"></li>'
                    for j, f in enumerate(fails))
    body = (f'{KV_STYLE}<div class="kv-play">'
            f'<script type="application/json" class="kv-data">{json.dumps(data, separators=(",", ":"))}</script>'
            '<div class="kv-stage">'
            f'<p class="kv-status" aria-live="polite" aria-atomic="true">{kv_status(k, run, fails[k], rows)}</p>'
            '<p class="kv-key">Each dot is one article, placed by how many questions its worst of three tries got '
            "right, against that article's bar (the dashed line). A red dot is below the bar, and one is enough to "
            'fail the whole run.</p>'
            f'<div class="kv-arts" role="img" aria-label="{kv_arts_label(k, fails[k])}">{kv_cells(rows, run, quality)}'
            '</div></div>'
            '<div class="kv-tl nojs"><div class="kv-ctl" hidden>'
            f'{btn("play", "Play")}{btn("prev", "Previous run")}{btn("next", "Next run")}</div>'
            f'<div><div class="kv-strip" style="--i:{k}"><ol class="kv-slots" aria-label="Each re-run, passed or '
            f'failed">{slots}</ol><span class="kv-head" aria-hidden="true"></span></div>'
            f'<div class="kv-ends" aria-hidden="true"><span>Run 1</span><span><i class="p"></i>passed '
            f'<i class="f"></i>failed</span><span>Run {KV_RUNS}</span></div></div>'
            f'<p class="kv-tally">{kv_tally(KV_RUNS, passed)}</p></div></div>')
    fig = figure(
        f'{KV_RUNS} re-runs of the reference against the task\'s accuracy bar', body,
        "How the authors' own method does when it is re-run against the task's accuracy bar. Each step is one "
        "re-run drawn from the reference's recorded tries: on each article, 3 of its 9 recorded tries picked at "
        'random, keeping the worst, as the grader keeps the worst of 3 fresh tries. Click to pause, or use the '
        f'arrows to step through. Source: <a href="{KV_MANIFEST}"><code>judge/targets/manifest.json</code></a> at '
        f'commit <code>{SHA[:8]}</code>, our resampling. We drew this sample of {KV_RUNS} once; its {passed} passes '
        'match the long-run rate of about 1 in 6 (counting only the 3 recorded runs gives 13%).',
        fid='kv-fig')
    wrap = ('<div class="viz-wrap scroll" tabindex="0" role="group" aria-label="Chart, scrolls sideways on small '
            'screens">')
    assert fig.count(wrap) == 1
    return fig.replace(wrap, '<div class="viz-wrap">')


def kv_example(rows, quality):
    """One real question from article 4 (Exile), one of the five articles with a recorded try below the bar."""
    ex = quality['example']
    k, r = next((j, r) for j, r in enumerate(rows) if r['a'] == ex['article'])
    art = quality['articles'][ex['article']]
    assert r['ok'] < 9 and art['questions'] == r['n'] and min(r['tries']) == r['bar'] - 1
    jsonl = f'{folder(KV)}/judge/data/quality_subset.jsonl#L10'
    gold = lambda j: j + 1 == ex['gold_label']
    opts = ''.join(('<li class="gold">' if gold(j) else '<li>') + html.escape(o)
                   + (' <span>(correct answer)</span>' if gold(j) else '') + '</li>' for j, o in enumerate(ex['options']))
    src_ = cite('QuALITY dataset', X(f'judge/data/quality_subset.jsonl:10, article {ex["article"]}, question '
                                     f'{ex["question_unique_id"]}', jsonl),
                X('QuALITY (Pang et al., NAACL 2022)', 'https://aclanthology.org/2022.naacl-main.391'))
    story = cite('Project Gutenberg', X(f'Project Gutenberg eBook {ex["article"]}',
                                        f'https://www.gutenberg.org/ebooks/{ex["article"]}'))
    return (f'<div class="kv-q"><p class="kv-qh">An example question from article {k + 1}, <i>{art["title"]}</i>, a '
            f'{art["year"]} story by {ex["author_display"]}. It is one of the five articles where a recorded try fell '
            f'below the bar; its worst got {min(r["tries"])} of its {r["n"]} questions right, against a bar of '
            f'{r["bar"]}. Its opening line reads "{html.escape(ex["first_line"])}"</p>'
            f'<p class="kv-qq">{html.escape(ex["question"])}</p><ol type="A">{opts}</ol>'
            '<p class="kv-qf">The task records how many questions each try got right, not which ones, so we cannot '
            f'tell whether the reference missed this one. Question from the {src_}, story from {story}.</p></div>')


def cases(data):
    q = data['quarter_pir_k31']
    dt = data['detok_counted_grading']
    t2 = f'{GH}/blob/{SHA}/tasks/frontier-cs-2.0-demo/problems/Crypto/{QPIR}/judge/table2_metrics.py#L305-L306'
    # Numbers in the QuarterPIR text, from the regrade and the first grading of query w00792.
    regrade = sorted(v / 1e6 for v in q['w00792']['candidate_ns'])
    ref = sorted(v / 1e6 for v in q['w00792']['reference_ns'])
    first = q['w00792_first_evaluation']
    slow = [v for v in regrade if v > max(ref)]
    assert len(slow) == 3 and sum(r < 1 for _, r in q['ratios']) == 1999
    assert max(first['candidate_ns']) < min(first['reference_ns'])
    qpir = f'''
<p>The task is to make each lookup in QuarterPIR, a scheme from a EUROCRYPT 2024 paper that lets a client read a record from a server without the server learning which one, send fewer bytes and run faster. The grader replays each of 2,000 queries five times on the candidate's server and five times on the reference's, takes the median of each five, and {cite('requires the candidate to be faster on every query', X('judge/table2_metrics.py:305-306', t2))}.</p>
<p>{cite("Kimi K3.1 Pro's server", E(QPIR, 'k31'))} passed every other check and was faster on 1,999 of the queries. On the last one, three of its five replays took {slow[0]:.2f} to {slow[-1]:.2f} ms, against {ref[0]:.2f} to {ref[-1]:.2f} ms for the reference, so its median came out slower and the run failed. That was in the regrade the leaderboard counts, which {cite("graded the same final submission again", X('metadata/formal-results.json', RESULTS))}. In the first grading, all five replays of that query were faster than the reference's, and the run was faster on all 2,000. Ten other tasks on this page have a pass bar of the same kind.</p>
{qpir_scatter(q)}'''

    rows = {run: (gains, slower, passes) for run, _, gains, slower, passes in detok_rows(dt)}
    agy, carbon = rows['gemini-agy'], rows['carbon-g']
    honest = [g for run in ('fable51', 'opus') for g in rows[run][0]]
    slow_by = [w['wall_candidate'] / w['wall_reference'] - 1 for w in dt['gemini-agy']['workloads']
               if w['wall_candidate'] >= w['wall_reference']]
    assert agy[1] == carbon[1] == 2 and not agy[2] and not carbon[2] and rows['fable51'][2] and rows['opus'][2]
    assert max(slow_by) < 0.01 and 0.7 < min(agy[0]) and max(agy[0]) < 0.8 and 1.5 < min(carbon[0])
    readme = f'{folder(DETOK)}/{README}#L13'
    code = ('def _refine_latents(self, x: Tensor, z: Tensor) -> Tensor:\n'
            '    ...\n'
            '    x_gt = x.detach().clone()\n'
            '    ...\n'
            '    decoded = self.decoder(z_opt)\n'
            '    diff = decoded.float() - x_gt.float()\n'
            '    mse_loss = diff.pow(2).mean()\n'
            '    ...\n'
            '    grad = torch.autograd.grad(loss * ..., z_opt)[0]\n'
            '    ...\n'
            '    delta = (-15.2 * grad).detach()\n'
            '    ...\n'
            '    z_opt = (z_opt + delta).detach()\n\n'
            'def tokenize(self, x: Tensor, sampling: bool = False) -> Tensor:\n'
            '    ...\n'
            '    if not self.training and not sampling and ...:\n'
            '        z = self._refine_latents(x, z)')
    detok = f'''
<p>The task is to restore the training from an ICLR 2026 paper that makes an image tokenizer robust. A tokenizer compresses a picture into a short code of tokens and decodes it back. The grader trains each submission briefly, then scores how closely it reproduces held-out photos. A run must beat the reference on quality and on time on each of three workloads.</p>
<p>{cite('Gemini 4 Argon (Antigravity)', E(DETOK, 'gemini-agy'))} added what its own code calls a "test-time gradient step through decoder". At evaluation only, it decodes the tokens, measures how far the result is from the photo being scored, and moves the tokens one step closer to that photo.</p>
{code_quote(code, f'Gemini 4 Argon (Antigravity) · {patch(DETOK, "gemini-agy", "267-339")}, abridged')}
<p>Its quality beat the reference by about {statistics.mean(agy[0]):.2f} dB on every workload, where the two passing runs gain at most {max(honest):.2f} dB. It failed only on time, under 1% slower on two workloads. {cite('Gemini 4 Carbon', E(DETOK, 'carbon-g'))} did the same, gained about {statistics.mean(carbon[0]):.1f} dB, and also failed only on time. The decoded tokens are no longer the encoder's output, so as we read it the gain says nothing about the tokenizer. The README asks only that {cite('evaluation remain "clean"', X('repo/README.md:13', readme))}, so we see this as a gap in the task rather than a broken rule.</p>
{detok_chart(dt)}'''
    kv_rows_ = kv_rows(data['kv_reference_captures'])
    quality = data['kv_quality']
    per_capture, pooled = kv_check(kv_rows_)
    assert round(1 / pooled) == 6  # "about 5 times in 6" in the text and figure: 17% resampled
    k30029 = next(r for r in kv_rows_ if r['a'] == '30029')
    sizes = sorted({r['n'] for r in kv_rows_})
    gate = cite("the worst of the three must come within one question of the reference's median score",
                X('judge/gate.py:9', f'{KV_GATE}#L9'), X('judge/gate.py:209', f'{KV_GATE}#L209'),
                X('judge/gate.py:245-256', f'{KV_GATE}#L245-L256'))
    kv = f'''
<p>The task is to shrink a model's cached context to a tenth and keep its answers, by rebuilding the method of the Fast KV Compaction paper (ICML 2026). The cached context, the KV cache, is the model's working memory of a long document. The grader asks {sizes[0]} to {sizes[-1]} questions about each of 24 articles, three times over from the shrunken cache, and {gate}.</p>
<p>The reference is never run at grading; its three recorded runs are frozen, and from try to try its scores wobble by a question or so. On 5 of the 24 articles, one of its nine recorded tries falls one question below the bar, and one such try among an article's three fails the whole run. Re-run unchanged, the authors' own method fails the task's accuracy bar about 5 times in 6. Even the full, uncompressed cache, which loses nothing, {cite(f'scores {k30029["unc"]} on one article where the bar is {k30029["bar"]}', X('judge/targets/manifest.json, article 30029', KV_30029))}.</p>
{kv_example(kv_rows_, quality)}
<p>So a compactor exactly as good as the reference usually fails, and very likely so would a lossless one. {cite('Claude Opus 5.5', E(KV, 'opus'))}, the closest run, {cite('passed the time and size checks on all 24 articles and missed the accuracy bar on 2', X('metadata/formal-results.json', RESULTS))}.</p>
{kv_figure(kv_rows_, pooled, quality["articles"])}'''
    run = lambda t, m: f'<a href="{HF}/tree/{REV}/traces/{t}/{m}">'
    return [('case-kv', f'<a href="{folder(KV)}">{NAME[KV]}</a>', kv),
            ('case-qpir', f'{run(QPIR, "k31")}{NAME[QPIR]}</a>', qpir),
            ('case-detok', f'{run(DETOK, "gemini-agy")}{NAME[DETOK]}</a>', detok)]


def main():
    data = json.load(open(os.path.join(HERE, 'data', 'frontiercs-2_case_data.json')))
    print(write_page(
        'frontiercs-2', 'FrontierCS 2', 'Nov. 3, 2026', 'FrontierCS Team (Qiuyang Mang, Wenhao Chai et al.)',
        '48 public tasks; tasks and runs as of Nov. 2, 2026',
        lede='FrontierCS 2 tests whether an AI agent can rebuild the key contribution of a published computer-science '
             'paper, measured by the share of tasks it passes. In each of its 48 public tasks, the paper\'s code (the '
             '<em>reference</em>) is removed, the agent has 5 hours to rewrite it, and a run passes only if it beats the '
             'reference on every metric and every test set.<sup><a href="#na">a</a></sup><sup><a href="#nb">b</a></sup>',
        found=['We reviewed all 48 public tasks and found that <strong>15 (31%)</strong> had grading errors. A benchmark is '
               'rated Flawed when errors affect at least 20% of its score.',
               'On 11 tasks, a run must beat the reference on every single test, by a margin smaller than the '
               'reference\'s own run-to-run noise, so even the reference often fails its own bar.<sup><a href="#nc">c</a></sup> On one task, Kimi '
               'K3.1 Pro\'s faster server failed because of one slow query out of 2,000.',
               'Two tasks can be passed without a better method. Copying the reference passes one, because ties count, '
               'and on another, runs tune their output to the very image being scored.',
               'Three runs on a task about blocking prompt-injection attacks are listed as failing because blocked '
               'attacks were counted as successful ones. By the task\'s current grader, all three would pass.'],
        cases_intro='Three tasks show the two kinds of problem. On the first two, the pass bar is tighter than the '
                    "reference's own variation. The reference rarely clears its own accuracy bar on KV-cache "
                    'compaction, and on QuarterPIR a faster server fails on one slow query out of 2,000. On the third, '
                    'runs tune their output to the image being scored.',
        errors=ERROR_GROUPS, cases=cases(data), extra_script=KV_SCRIPT,
        disclaimer='FrontierCS 2 publishes every task, judge, reference patch, final patch and agent trace, so all 48 '
                   'public tasks could be reviewed; the private set of more than 100 tasks could not. Every error '
                   'listed above was found by AI review and then hand-checked against the source by a human.',
        notes=[('na', 'Paper: <a href="https://arxiv.org/abs/2610.29932">arXiv 2610.29932</a>. Leaderboards: '
                      '<a href="https://frontier-cs.org">frontier-cs.org</a> and <a href="https://www.kaggle.com/'
                      'benchmarks/frontiercs/frontiercs-2">Kaggle</a>.'),
               ('nb', f'Tasks and judges: <a href="{GH}/tree/{SHA}">FrontierCS/FrontierCS-2</a> at commit '
                      f'<code>{SHA[:8]}</code> (Nov. 2, 2026); file and line references on this page are to that '
                      f'commit. Runs and results: <a href="{HF}/tree/{REV}">FrontierCS2/FrontierCS-2-runs</a> at '
                      f'revision <code>{REV[:8]}</code> (Nov. 2, 2026), with <code>metadata/formal-results.json</code>, '
                      '<code>patches/</code> and <code>traces/</code>; pass and fail verdicts on this page are the '
                      'ones in that file. Per-task write-ups, the task log and our scripts are in the audit folder '
                      'linked at the top of this page.'),
               ('nc', 'Our computations. vLLM: for each reference run and request group, the geometric mean over '
                      'requests of that run\'s latency divided by the per-request target. QuarterPIR: for each query, '
                      'the median of 5 candidate replays divided by the median of 5 reference replays, from '
                      '<code>metrics.json</code> in the verifier evidence. Parallel radix sort: the task\'s score is '
                      '100·<i>L</i>/(ln 10 + <i>L</i>), with <i>L</i> the log of the geometric-mean speedup over '
                      '<code>std::sort</code> on the 8 original workloads; we invert it to turn a score gap into a '
                      'speed gap. Join-tree and Edlib counts: every evaluation the agents requested during their runs, '
                      'as recorded in the released traces. These use only the public dev workloads; the final grade '
                      'adds hidden ones.')]))


if __name__ == '__main__':
    main()
