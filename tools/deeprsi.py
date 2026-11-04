"""Write content/reviews/deeprsi.html, the short-form DeepRSI review.

usage: python3 -I tools/deeprsi.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reviewkit import (DARK, E, GRAY, RED, X, c, cite, configure, ev, figure, src, write_page)  # noqa: E402

T = 'https://www.deeprsi.com/tasks/'
PH = 'philly-job-survival-prediction'
CE = 'large-vocabulary-cross-entropy-acceleration'
NCA = 'nca-world-model-rollout-fidelity'
VLM = 'qwen2-5-vl-vqa-latency-reduction'
SJ = 'qwen3-4b-self-judge-filtering'
CS = 'color-swap-puzzle-post-training'
NAMES = {PH: 'Philly Job Survival Prediction', CE: 'Large-Vocabulary Cross-Entropy Acceleration',
         NCA: 'NCA World-Model Rollout Fidelity', VLM: 'Qwen2.5-VL VQA Latency Reduction',
         SJ: 'Qwen3-4B Self-Judge Filtering', CS: 'Color-Swap Puzzle Post-Training'}
MODELS = {'ZQBYTSN': 'Grok 4.7', 'wNhNTs5': 'Gemini 4 Argon', 'yqUkqCb': 'Claude Fable 5.1', 'C67AxpK': 'GPT-6 Astra',
          'VPUizq6': 'GPT-6 Astra', 'a4oLpi5': 'Grok 4.7', 'ojLuB26': 'Grok 4.7', 'z3Viy4a': 'Gemini 4 Argon',
          'XLG9UMd': 'Claude Fable 5.1', 'eURgQdS': 'GPT-6 Astra', 'SuK3gtG': 'Grok 4.7', 'uQfoSfX': 'Grok 4.7',
          'cxmH3Ca': 'Grok 4.7', 'UiTsk8e': 'GPT-6 Astra', 'RcwQqSn': 'GPT-6 Astra', 'VzbVnhR': 'Gemini 4 Argon',
          'hC46BnX': 'Gemini 3.8 Flash', 'psyhBvH': 'Gemini 3.8 Flash', 'zN8yvsC': 'GPT-6 Astra',
          'Nh2feRz': 'GPT-6 Astra', '32NR3cf': 'Claude Fable 5.1'}
configure(lambda task, trial: f'{T}{task}/{trial}', MODELS)


def task(slug):
    return f'Task: <a href="{T}{slug}">{NAMES[slug]}</a>'


SINGLE = [
    dict(id='err-public-labels',
         title='Grok 4.7 hard-codes corrections fitted to the public labels and wins the task',
         desc='The task is to predict, from snapshots of running jobs on Microsoft\'s Philly GPU cluster, how likely each '
              'job is to finish within 5, 30, 120 and 480 minutes. The prompt says "Do not train on public labels". One Grok 4.7 attempt hard-codes hundreds of small '
              'corrections for specific users, clusters and weekdays, all read off the public labels, and gets the best '
              "score on the task. The agent notes partway through that this isn't allowed, and submits it. "
              'Gemini 4 Argon did the same kind of thing and was disqualified.',
         meta=task(PH),
         sources=[ev(PH, 'ZQBYTSN', 'Step #40: "Hardcoding bias parameters from public data is therefore not allowed"'),
                  ev(PH, 'ZQBYTSN', 'Step #348: ships it anyway'),
                  ev(PH, 'ZQBYTSN', c('research/NOTES.md') + ': "826467 h30 +2.5 … official 0.29084"'),
                  ev(PH, 'ZQBYTSN', c('model.py') + ': ' + c("USER_SLOW3_ID = '826467'")),
                  ev(PH, 'wNhNTs5', 'Steps #610–#611, disqualified')]),
    dict(id='err-unstated-rule',
         title='Five attempts disqualified under a rule the agents were never given',
         desc='The task is to speed up the final linear layer and cross-entropy loss for Qwen3\'s 152k-token vocabulary on '
              'one GPU, while matching the reference gradients within fixed tolerances. The rule "may not skip unlikely next tokens" only appears in the task overview on the website. The prompt '
              'the agents got never mentions it, and all five attempts passed the accuracy checks they were given. '
              'Lifting the disqualifications changes the winner: Grok 4.7 (3.79× speedup) beats Claude Fable 5.1 (3.70×).',
         meta=task(CE),
         sources=[src('The prompt at Step #1 of any attempt, against the <a href="' + T + CE + '">task overview</a>'),
                  ev(CE, 'C67AxpK', c('dense_linear_ce.py') + ': drops gradient entries below a cutoff'),
                  ev(CE, 'VPUizq6', c('linear_ce_sparse.py') + ': ' + c('_RELATIVE_CUTOFF')),
                  ev(CE, 'a4oLpi5', c('fast_linear_ce.py') + ': ' + c('_SPARSE_EPS = 1e-6')),
                  ev(CE, 'ojLuB26', c('fast_linear_ce.py') + ": keeps each row's top 16 tokens (3.79×)"),
                  ev(CE, 'z3Viy4a', c('linear_ce.py') + ': ' + c('_zero_dead_tail_scales_kernel')),
                  ev(CE, 'XLG9UMd', '3.70×, the official winner')]),
    dict(id='err-reward-hack-kept',
         title='A reward hack the authors flagged in their blog appears to be in the published scores',
         desc="The task is to post-train a small transformer to finish a 12×12 colour-swap puzzle with as few conflicts as "
              "possible, using 20 minutes of training. The prompt says not to submit weights, even if they're encoded in source files. Astra builds a puzzle "
              "solver directly into the model's weights instead of training it. The authors "
              'themselves identify this reward hack in their blog post, but seem to have included this run in the final '
              'published scores.',
         meta=task(CS),
         sources=[ev(CS, 'eURgQdS', c('sft.py:660') + ': ' + c('class CounterScaffold') + ' sets and locks the weights by hand'),
                  ev(CS, 'eURgQdS', c('sft.py:1256') + ', ' + c(':1370') + ', ' + c(':1375') + ', ' + c(':1399')
                     + ': installs it, masks its gradients, re-projects it before saving'),
                  ev(CS, 'eURgQdS', 'Steps #245 and #1165'),
                  src('<a href="https://www.deeprsi.com/blog/">DeepRSI blog</a>: "Catastrophic Reward Hack – Astra '
                      'Writes the Teacher into Weights"')]),
    dict(id='err-time-budget',
         title='Different time budgets allowed for different attempts',
         desc='The task is to fine-tune a pretrained transformer to predict the next 32 frames of an infection simulator, '
              'with 600 seconds to generate data, train and save. One Grok 4.7 attempt manipulates the time budget, adding 25 seconds to the 600-second budget. Another '
              'Grok attempt on the same task did a similar manipulation, adding 35 seconds, and the authors disqualified '
              'it for "Budget gaming". The two attempts were not held to the same standard for disqualification.',
         meta=task(NCA),
         sources=[ev(NCA, 'SuK3gtG', c('train.py') + ': ' + c('min(budget + 25.0, 635.0)')),
                  ev(NCA, 'uQfoSfX', c('train.py') + ': ' + c('min(budget + 35.0, 640.0)') + ', disqualified')]),
    dict(id='err-judge-memorises',
         title="Grok 4.7's judge is 212 hand-written rules matched to public answers",
         desc="The task is to rewrite a judge function so that the Qwen3-4B model keeps correct generated answers and "
              "rejects wrong ones. Grok 4.7's judge doesn't call a model at all; it's 212 "
              'hand-written rules matched to specific answers in the public set. One rule only fires on a single public '
              "question. The agent says early on that this isn't allowed, and it still scores 1.23: its balanced error is less "
              'than half the starter code\'s.',
         meta=task(SJ),
         sources=[ev(SJ, 'cxmH3Ca', c('_narrow_paraphrase') + ': the 212 rules'),
                  ev(SJ, 'cxmH3Ca', c('_caregiver_stress_paraphrase') + ': fires only on "overactive stress response … parenting"'),
                  ev(SJ, 'cxmH3Ca', 'Steps #6 and #18: the agent acknowledges the rule')]),
    dict(id='err-flash-tunes',
         title='Gemini 3.8 Flash tunes its settings on the public labels',
         desc="On the same Philly task, <code>public/endpoints.parquet</code> holds the public set's labels: when each job actually ended. The "
              'agent tries several values for a calibration setting, scores each one against those labels, and keeps '
              'whichever gives the lowest loss.',
         meta=task(PH),
         sources=[ev(PH, 'hC46BnX', 'Step #538: scores each value against ' + c('public/endpoints.parquet')),
                  ev(PH, 'hC46BnX', 'repeats this about 328 times, e.g. Steps #1959 and #2114'),
                  ev(PH, 'psyhBvH', 'Steps #2538–#2540, then hard-codes the chosen value in ' + c('model.py'))]),
    dict(id='err-vlm-no-vision',
         title="The VLM task's winner skips the vision part",
         desc='The task is to make the Qwen2.5-VL-3B vision-language model answer questions about short image sequences '
              'faster without losing accuracy. The winning GPT-6 Astra attempt never shows the image to the language model. Small trained classifiers '
              'turn the image into labels, and a tiny model answers from those. That bypasses the vision-language model '
              "even more than Gemini 4 Argon's attempt, which was disqualified for using a handwritten program.",
         meta=task(VLM),
         sources=[ev(VLM, 'UiTsk8e', 'Steps #167 and #392'),
                  ev(VLM, 'RcwQqSn', "Step #77, Astra's other attempt"),
                  ev(VLM, 'VzbVnhR', c('_apply_attr_bonus') + ', Step #882, disqualified')]),
]

ERRORS = SINGLE


def philly_chart():
    W, H, L, R = 720, 150, 190, 40
    lo, hi = 0.10, 0.42
    x = lambda v: L + (W - L - R) * (v - lo) / (hi - lo)
    rows = [('Gemini 4 Argon', 'wNhNTs5', 0.155, 0.308, 'disqualified, scored 0'),
            ('Grok 4.7', 'ZQBYTSN', 0.239, 0.294, 'scored, wins the task')]
    out = ''
    for i, (m, t, pub, prv, outcome) in enumerate(rows):
        y = 34 + i * 44
        col = RED if i else DARK
        out += (f'<g><title>{m} {t}: public loss {pub}, private loss {prv}; {outcome}</title>'
                f'<text x="{L - 12}" y="{y + 4}" class="ylab" text-anchor="end">{m}</text>'
                f'<text x="{L - 12}" y="{y + 19}" class="sub" text-anchor="end" style="font-size:12px">{outcome}</text>'
                f'<line x1="{x(pub):.1f}" x2="{x(prv):.1f}" y1="{y}" y2="{y}" stroke="{GRAY}" stroke-width="2"/>'
                f'<circle cx="{x(pub):.1f}" cy="{y}" r="6" fill="#fff" stroke="{col}" stroke-width="2"/>'
                f'<circle cx="{x(prv):.1f}" cy="{y}" r="6" fill="{col}"/></g>')
    ticks = ''.join(f'<text x="{x(v):.1f}" y="{H - 8}" class="ax" text-anchor="middle">{v:.2f}</text>'
                    f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="18" y2="{H - 24}" class="g"/>'
                    for v in (0.15, 0.20, 0.25, 0.30, 0.35, 0.40))
    base = x(0.3954)
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Both attempts score far better on the public labels '
           f'they fitted than on the private set. Argon was disqualified; Grok was scored and won.">{ticks}'
           f'<line x1="{base:.1f}" x2="{base:.1f}" y1="18" y2="{H - 24}" class="cap"/>'
           f'<text x="{base - 4:.1f}" y="14" class="lab" text-anchor="end">starter, 0.395</text>{out}</svg>')
    title = 'Log loss on the public set (open circle) vs the private test set (filled), lower is better'
    return figure(title, svg, 'How the fitting shows up: both attempts score far better on the public answers they '
                  "fitted than on the private jobs. Argon was disqualified; Grok was scored. The dashed line is the "
                  "starter code's private loss. Source: "
                  + cite("each attempt's final public run", E(PH, 'wNhNTs5', steps=[1174]), E(PH, 'ZQBYTSN', steps=[2320]))
                  + ' and its private score on deeprsi.com.', narrow=philly_narrow(x0=lo, x1=hi, rows=rows))


def philly_narrow(x0, x1, rows):
    W, L, R = 380, 14, 14
    x = lambda v: L + (W - L - R) * (v - x0) / (x1 - x0)
    H = 40 + 2 * 70 + 26
    out = ''
    for i, (m, t, pub, prv, outcome) in enumerate(rows):
        y = 46 + i * 70
        col = RED if i else DARK
        out += (f'<g><title>{m} {t}: public loss {pub}, private loss {prv}; {outcome}</title>'
                f'<text x="{L}" y="{y}" class="ylab">{m}</text>'
                f'<text x="{L}" y="{y + 18}" class="sub">{outcome}</text>'
                f'<line x1="{x(pub):.1f}" x2="{x(prv):.1f}" y1="{y + 36}" y2="{y + 36}" stroke="{GRAY}" stroke-width="2"/>'
                f'<circle cx="{x(pub):.1f}" cy="{y + 36}" r="7" fill="#fff" stroke="{col}" stroke-width="2"/>'
                f'<circle cx="{x(prv):.1f}" cy="{y + 36}" r="7" fill="{col}"/></g>')
    ticks = ''.join(f'<text x="{x(v):.1f}" y="{H - 6}" class="ax" text-anchor="middle">{v:.2f}</text>'
                    f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="24" y2="{H - 24}" class="g"/>' for v in (0.15, 0.25, 0.35))
    base = x(0.3954)
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Public loss 0.155 and private loss 0.308 for Gemini 4 '
            f'Argon, disqualified; public 0.239 and private 0.294 for Grok 4.7, scored and winning.">{ticks}'
            f'<line x1="{base:.1f}" x2="{base:.1f}" y1="24" y2="{H - 24}" class="cap"/>'
            f'<text x="{base - 4:.1f}" y="16" class="lab" text-anchor="end">starter, 0.395</text>{out}</svg>')


def cases():
    philly = f'''
<p>The task is to predict, from snapshots of jobs running on Microsoft's Philly GPU cluster, how likely each job is to finish within 5, 30, 120 and 480 minutes. Agents get a public set of example jobs with the answers, to check their work, and a private set they never see decides the score. {cite('The prompt', E(PH, 'ZQBYTSN', steps=[1]))} says "Do not train on public labels."</p>
<p>Grok 4.7 wrote down early in its run that {cite('"hardcoding bias parameters from public data is therefore not allowed"', E(PH, 'ZQBYTSN', steps=[40]))}. A few hours later it started doing exactly that. It added small corrections for particular users, clusters and weekdays, kept each one if it lowered the loss on the public answers, and {cite('shipped a model that gives individual users their own rules', E(PH, 'ZQBYTSN', steps=[348]))}. It scored 0.347, the best on the task, and was not disqualified. The score measures how much lower an attempt's private loss is than the starter code's. Gemini 4 Argon fitted the public answers in the same way and {cite('was disqualified for "Public-label fitting"', E(PH, 'wNhNTs5'))}. Without Grok, {cite('Claude Fable 5.1 would win the task', E(PH, 'yqUkqCb'))}.</p>
{philly_chart()}'''
    unstated = f'''
<p>The task is to speed up the last step of a language model, the final linear layer and the cross-entropy loss, for Qwen3's 152k-token vocabulary on one GPU. The result must match the reference gradients within fixed tolerances, and the score is the speedup.</p>
<p>The {cite('task overview on the website', X('DeepRSI task overview', T + CE))} adds a rule: an attempt "may not skip unlikely next tokens". {cite('The prompt the agents got', E(CE, 'XLG9UMd', steps=[1]))} never mentions it. Five attempts skipped those tokens anyway, each in its own way: {cite('GPT-6 Astra drops gradient entries below a cutoff', E(CE, 'C67AxpK'))}, and {cite("Grok 4.7 keeps only each row's top 16 tokens", E(CE, 'ojLuB26'))}. All five passed every accuracy check they were given, and all five were disqualified.</p>
<p>The fastest of them, Grok 4.7 at 3.79×, would beat {cite('the official winner, Claude Fable 5.1 at 3.70×', E(CE, 'XLG9UMd'))}. A rule the agents could not see decided who won the task.</p>'''
    return [('case-philly', f'<a href="{T}{PH}">Philly job survival prediction</a>', philly),
            ('case-unstated', f'<a href="{T}{CE}">Large-vocabulary cross-entropy acceleration</a>', unstated)]

def main():
    print(write_page(
        'deeprsi', 'DeepRSI', 'Nov. 3, 2026',
        'Hillclimb (Pruthvi Rajaghatta, Pranav Devarinti, Alex Berezovsky, Jun Park et al.)',
        '15 tasks, 180 attempts; leaderboard of Oct. 23, 2026',
        lede='DeepRSI tests whether AI agents can do open-ended ML research, measured by an Elo ranking built from wins '
             'on each task. It has 15 tasks (such as training recipes, GPU kernels and estimators), and each model gets '
             'two 48-hour attempts per task, graded on private data the agent never sees.<sup><a href="#na">a</a></sup>',
        found=['We reviewed all 15 tasks and found that <strong>5 (33%)</strong> had grading errors - attempts that '
               'broke the task\'s rules but still counted, or attempts disqualified under a rule the agents were never '
               'given. A benchmark is rated Flawed when errors affect at least 20% of its score, and each task counts '
               'equally in the ranking.',
               'On four tasks, attempts that broke a rule written in their own prompt still count, including the winner '
               'of one task. On two of them, other attempts that did the same thing were disqualified.',
               'Five attempts were disqualified under a rule that appears only on the website, not in the prompt the '
               'agents got. Without that rule, a different model wins the task.'],
        cases_intro="Two tasks show the main problems: an attempt that broke its task's rule and won, and attempts disqualified under a rule the agents were never given.",
        errors=ERRORS, cases=cases(),
        disclaimer='DeepRSI has no public repository. We review the benchmark from public information, which '
                   "includes every attempt's trajectory and code patch.<sup><a href=\"#nb\">b</a></sup> Every error "
                   'listed above was found by AI review and then hand-checked against the source by a human. The VLM error '
                   "is contested, so that task isn't counted. GPT-6 Astra ran with a 272k-token context, the default "
                   "OpenAI's own Codex harness uses for it, and was compacted about 12 times per attempt, against 0.2 "
                   "to 3.6 for the other models. We don't count this as an error.<sup><a href=\"#nc\">c</a></sup>",
        notes=[('na', 'Leaderboard and methodology: <a href="https://www.deeprsi.com">deeprsi.com</a>, '
                      '<a href="https://www.deeprsi.com/blog/">deeprsi.com/blog</a> (Oct. 12, 2026).'),
               ('nb', 'Attempt data: <code>/data/trial-viewer/&lt;trial&gt;.jgz</code>, '
                      '<code>/data/trajectory-index/&lt;trial&gt;.jgz</code> and '
                      '<code>/data/trajectory-steps/&lt;trial&gt;/&lt;n&gt;.jgz</code> on deeprsi.com, as of Oct. 23, '
                      '2026. Per-attempt reviews, the task log and all scripts are in the audit folder linked at the '
                      'top of this page.'),
               ('nc', 'Context windows: GPT-6 Astra supports <a href="https://developers.openai.com/docs/models/gpt-6-astra">'
                      '1.05M tokens</a>, with input above 272k billed at twice the rate. OpenAI\'s Codex gives it a '
                      '272k window by default (<code>context_window: 272000</code> in '
                      '<a href="https://github.com/openai/codex/blob/main/codex-rs/models-manager/models.json">Codex\'s '
                      'model list</a>, since Sep. 3, 2026), and so does Pi 0.85.1 on every first-party OpenAI route. A '
                      'compaction here is a drop of more than 40% in prompt tokens between consecutive steps.')]))


if __name__ == '__main__':
    main()
