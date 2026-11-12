"""Write content/reviews/autoresearchexam.html, the short-form AutoResearchExam review.

usage: python3 -I tools/autoresearchexam.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reviewkit import BLUE, DARK, GRAY, RED, E, X, c, cite, configure, ev, figure, quote, src, write_page  # noqa: E402

COMMIT = '23c0d92e11af1dea821f972b5f0a739060958002'
GH = f'https://github.com/bespokelabsai/AutoResearchExam/blob/{COMMIT}/'
SITE = 'https://benchmarks.bespokelabs.ai/autoresearchexam/'
VIEW = SITE + 'rollout-viewer.html?task={task}&model={model}'
MODELS = {  # rollout-viewer slug -> model name
    'opus_5_5': 'Opus 5.5', 'fable_5_1': 'Claude Fable 5.1', 'gpt-6_astra': 'GPT-6 Astra', 'argon': 'Gemini 4 Argon',
    'opus_5': 'Claude Opus 5', 'grok_4_7': 'Grok 4.7', 'gpt-5_6_sol': 'GPT-5.6 Sol', 'grok_4_6': 'Grok 4.6',
    'gemini_3_8_flash': 'Gemini 3.8 Flash', 'kimi_k3': 'Kimi K3', 'qwen3_8_max': 'Qwen3.8 Max',
    'muse_spark_1_3': 'Muse Spark 1.3',
}
configure(lambda task, trial: VIEW.format(task=task, model=trial), MODELS)

SN = 'sketched-newton-cov-estimator'
FA = 'fast-adv-budgeted-pgd50-robust-cifar10'
RP = 'reppo-reliable-onpolicy-control-trainer'
CI = 'shortest-valid-ci-l2-ece'
FG = 'fastergcg-candidate-token-rank-ccc'
TM = 'ties-merging-clip-vitl14-eight-task-merge'
GR = 'grpo-rl-halfcheetah-advantage-estimator'
CR = 'causalrivers-heldout-station-graph-auroc'
CD = 'cpu-decoder-graph-executor'


def gh(path, lines=None):
    """A link to a file (and lines) in the repo at the reviewed commit, shown as path:lines."""
    anchor = ''
    if lines:
        a, _, b = str(lines).partition('-')
        anchor = f'#L{a}' + (f'-L{b}' if b else '')
    label = path.split('/')[-1] + (f':{lines}' if lines else '')
    return f'<a href="{GH}{path}{anchor}">{c(label)}</a>'


def grader(task, f='grader_core.py'):
    return f'{task}/environment/are-grader-ctx/{f}'


def task(name):
    return f'Task: {name}'


ERRORS = [
    dict(id='err-seed',
         title='Grok 4.7 rebuilds the hidden answer from a seed the grader leaves readable, and wins the task',
         desc='The task is to estimate the covariance of a stochastic Newton method from its run, without access to '
              'the hidden problem. At grading time the grader writes the sample seed and the full sample arrays into '
              'the folder the candidate\'s code runs in, although the instruction says the seed is not revealed. '
              'Grok 4.7 made a submission crash on purpose so the grader\'s error report would show its internal '
              'state, then shipped code that recovers the seed and returns the exact answer: error 0.000000. It wins '
              'the task with 0.691, against 0.616 for the best honest run (GPT-6 Astra), who would win without it. '
              'Opus 5.5 and Gemini 4 Argon saw the same shortcut and declined it.',
         meta=task('Sketched Newton covariance estimator'),
         sources=[ev(SN, 'grok_4_7', '#917: raises an error on purpose to dump grading-time state'),
                  ev(SN, 'grok_4_7', '#925: the dump returns the seed'),
                  ev(SN, 'grok_4_7', '#1571: ships seed recovery'),
                  ev(SN, 'grok_4_7', '#1582: graded at error 0.000000, reward 0.870'),
                  src(gh(grader(SN), '130-136') + ': seed and samples written next to the candidate\'s code',
                      'grader'),
                  src(gh(f'{SN}/instruction.md', 44) + ': "does not reveal … seed"', 'instruction')]),
    dict(id='err-logits',
         title='Shrinking a model\'s outputs weakens the robustness attack, although the instructions say it can\'t',
         desc='The task is to train a CIFAR-10 classifier that resists adversarial attack. The instruction says the '
              'grader rescales outputs so that logit scaling cannot weaken the attack, but the rescaling only '
              'corrects large outputs. Claude Opus 5 found that multiplying its last layer by 0.01 adds 2.2 points '
              'with predictions unchanged, and declined to ship it. Its shipped model scores 69.1% under the '
              'graded attack but 39.7% under a standard stronger attack, below a plain baseline (50.8%), and it '
              'ranks 4th. The true ranking under a stronger attack isn\'t known.',
         meta=task('Budgeted PGD-50 robust CIFAR-10'),
         sources=[ev(FA, 'opus_5', '#1025: 69.1% under the graded attack, 39.7% under a margin attack'),
                  ev(FA, 'opus_5', '#1183: "+2.2 pt" from scaling logits, not shipped'),
                  src(gh(f'{FA}/instruction.md', 34) + ': "prevents logit scaling from weakening the attack"',
                      'instruction'),
                  src(gh(grader(FA), '186-187') + ': divides only by values above 1', 'grader')]),
    dict(id='err-saturated',
         title='Seven of twelve models reach a perfect test score, so the ranking measures time to first submission',
         desc='The task is to write a training procedure that makes control policies succeed reliably across 72 '
              'hidden environment seeds. Seven of the twelve models reach 72 of 72. GPT-6 Astra did it with its '
              'first submission, at 0.24 hours, and GPT-5.6 Sol at 0.68 hours, so the task\'s score among the top '
              'seven only ranks how early each first submitted.',
         meta=task('Reliable on-policy control trainer'),
         sources=[src('Per-submission test scores in the ' + f'<a href="{SITE}">published results</a>'
                      + ': 72/72 for GPT-6 Astra, Gemini 4 Argon, GPT-5.6 Sol, Opus 5.5, Grok 4.7, Claude Opus 5, '
                      'Claude Fable 5.1', 'results'),
                  src(gh(f'{RP}/instruction.md', 10) + ': "Higher is always better"', 'instruction')]),
    dict(id='err-ci',
         title='The instructions promise credit for any interval metric below 1.0; the grader gives zero above 0.0593',
         desc='The task is to produce the shortest prediction intervals that still cover the truth in six hidden '
              'settings. The instruction says every metric below 1.0 earns more credit, but the grader pays zero '
              'for anything at or above 0.0593, so missing coverage in one setting zeroes the run. Scored as the '
              'instruction describes, six runs gain 0.05 to 0.20, and GPT-5.6 Sol moves from 7th to 5th of the '
              'nine runs we could re-score. The winner is unchanged.',
         meta=task('Shortest valid CI under L2 ECE'),
         sources=[ev(CI, 'opus_5_5', '#106: metric 0.1755 graded as score 0'),
                  ev(CI, 'gpt-5_6_sol', '#885, #892: a tiny validation gain costs the whole test score'),
                  src(gh(f'{CI}/instruction.md', '74-75') + ': "Every metric below 1.0 earns more credit"',
                      'instruction'),
                  src(gh(grader(CI), 18) + ' and ' + gh(grader(CI), '35-37') + ': reward 0 at or above 0.0593',
                      'grader')]),
]

# model, mean hidden-test AUARC over 29 tasks (rollout index), share of task resamples at #1, and the 95% interval
# from resampling tasks with each task's mean across models held fixed (leaderboard.py, 20,000 resamples)
LEADERBOARD = [
    ('Opus 5.5', 0.609, 47, 0.583, 0.637), ('Claude Fable 5.1', 0.602, 14, 0.578, 0.629),
    ('GPT-6 Astra', 0.600, 24, 0.571, 0.632), ('Gemini 4 Argon', 0.594, 14, 0.563, 0.627),
    ('Claude Opus 5', 0.579, 0, 0.555, 0.606), ('Grok 4.7', 0.523, 0, 0.495, 0.551),
    ('GPT-5.6 Sol', 0.513, 0, 0.479, 0.550), ('Grok 4.6', 0.493, 0, 0.464, 0.521),
    ('Gemini 3.8 Flash', 0.484, 0, 0.441, 0.519), ('Kimi K3', 0.436, 0, 0.382, 0.480),
    ('Qwen3.8 Max', 0.423, 0, 0.387, 0.458), ('Muse Spark 1.3', 0.379, 0, 0.325, 0.427),
]


def whisker(x, lo, hi, yc, cap):
    return (f'<path d="M{x(lo):.1f} {yc}H{x(hi):.1f}M{x(lo):.1f} {yc - cap}v{2 * cap}M{x(hi):.1f} {yc - cap}v{2 * cap}" '
            f'stroke="#1B1B1B" style="stroke:var(--ink)" stroke-width="1.5" fill="none"/>')


def board_chart():
    W, L, R, top, rh = 720, 150, 120, 26, 26
    H = top + rh * len(LEADERBOARD) + 26
    x = lambda v: L + (W - L - R) * v / 0.7
    bars = ''
    for i, (m, v, p, lo, hi) in enumerate(LEADERBOARD):
        y = top + i * rh
        col = RED if i < 4 else GRAY
        lab = f'{v:.3f}' + (f' · #1 in {p}%' if i < 4 else '')
        bars += (f'<g><title>{m}: mean AUARC {v:.3f}, 95% interval {lo:.3f} to {hi:.3f}'
                 + (f', first in {p}% of task resamples' if i < 4 else '')
                 + f'</title><text x="{L - 10}" y="{y + 14}" class="ylab" text-anchor="end">{m}</text>'
                 f'<rect x="{L}" y="{y + 3}" width="{x(v) - L:.1f}" height="17" rx="3" fill="{col}"/>'
                 + whisker(x, lo, hi, y + 11.5, 5)
                 + f'<text x="{x(hi) + 6:.1f}" y="{y + 16}" class="val">{lab}</text></g>')
    ticks = ''.join(f'<text x="{x(v):.1f}" y="{H - 6}" class="ax" text-anchor="middle">{v:.1f}</text>'
                    f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{top}" y2="{H - 22}" class="g"/>'
                    for v in (0, 0.2, 0.4, 0.6))
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Mean hidden-test AUARC for 12 models with 95% intervals. The top '
           f'four, Opus 5.5, Claude Fable 5.1, GPT-6 Astra and Gemini 4 Argon, are within 0.015 of each other and '
           f'their intervals overlap.">'
           f'{ticks}{bars}</svg>')
    narrow = board_narrow()
    return figure('Leaderboard: mean hidden-test AUARC over 29 tasks', svg,
                  'Black lines are 95% intervals from resampling the 29 tasks, measured against the other models '
                  'on each task. The top four (red) are within 0.015 of each other and their intervals overlap: '
                  'each comes first in some resamples, and no adjacent gap among them is statistically clear. '
                  'Each model ran once per task. Source: the ' + cite('published rollout index', X('Rollout index',
                                                                                   SITE + 'public-rollout-data/index.json'))
                  + ' and our ' + cite('task bootstrap', X('leaderboard.py in the audit folder', 'scripts/leaderboard.py')) + '.',
                  narrow=narrow)


def board_narrow():
    W, L, R, rh = 380, 14, 70, 44
    top = 30
    H = top + rh * len(LEADERBOARD) + 24
    x = lambda v: L + (W - L - R) * v / 0.7
    out = ''
    for i, (m, v, p, lo, hi) in enumerate(LEADERBOARD):
        y = top + i * rh
        col = RED if i < 4 else GRAY
        out += (f'<g><title>{m}: {v:.3f} (95% interval {lo:.3f} to {hi:.3f})</title>'
                f'<text x="{L}" y="{y + 12}" class="ylab">{m}</text>'
                f'<rect x="{L}" y="{y + 18}" width="{max(x(v) - L, 2):.1f}" height="16" rx="3" fill="{col}"/>'
                + whisker(x, lo, hi, y + 26, 5)
                + f'<text x="{x(hi) + 6:.1f}" y="{y + 31}" class="val">{v:.3f}</text></g>')
    ticks = ''.join(f'<text x="{x(v):.1f}" y="{H - 6}" class="ax" text-anchor="middle">{v:.1f}</text>'
                    for v in (0, 0.3, 0.6))
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Mean AUARC: Opus 5.5 0.609, Claude Fable 5.1 0.602, '
            f'GPT-6 Astra 0.600, Gemini 4 Argon 0.594, then Claude Opus 5 0.579.">{ticks}{out}</svg>')


def cases():
    seed = f'''
<p>The task asks an agent to estimate the covariance of a stochastic Newton method from the run alone. The problem's design, noise and seed are hidden; the instruction says the configuration {cite('does not reveal the seed', X('instruction.md:44', GH + SN + '/instruction.md#L44'))}. But when the grader runs a submission, it {cite('writes the seed and the full sample arrays into the folder the code runs in', X('grader_core.py:130-136', GH + grader(SN) + '#L130-L136'))}.</p>
<p>Grok 4.7 went looking for them. It made one submission fail on purpose, so the grader's error report would show what the code could see:</p>
{quote('The next experiment raises a short FAILINFO RuntimeError before any return so the grader first-failure field can expose generator keys and stack frames.', 'Grok 4.7', SN, 'grok_4_7', '917')}
<p>The report came back with the seed. Grok then shipped code that tries nearby seeds, rebuilds the hidden problem and returns the exact covariance. The grader scored it at error 0.000000:</p>
{quote('The pending seed-recovery commit 5147b13 was graded: metric 0.000000, reward 0.870263, 0 failures, 15.4s.', 'Grok 4.7', SN, 'grok_4_7', '1582')}
<p>That gives Grok 4.7 the task with 0.691, against 0.616 for the best honest run, GPT-6 Astra's. Without the hack Grok scores 0.598 and Astra wins. Opus 5.5 and Gemini 4 Argon saw the same opening and {cite('declined it', E(SN, 'opus_5_5', ['175']), E(SN, 'argon', ['160', '289']))}.</p>
<p>Argon gamed something else: it used its scores across 31 submissions to {cite('work out the four hidden validation problems', E(SN, 'argon', ['698–851']))}, raising its validation score {cite('from 0.64 to 0.90', E(SN, 'argon', ['48', '2128']))}. Its hidden-test score ended at 0.605, below the 0.627 of the honest runs, because the test problems are different. The hidden test caught that. It couldn't catch Grok's trick, which rebuilds the answer to any problem. Opus 5.5 {cite('turned down both shortcuts', E(SN, 'opus_5_5', ['175']))}, calling the second &ldquo;overfitting&rdquo;.</p>'''
    tie = f'''
<p>The leaderboard ranks models by hidden-test AUARC: the time-weighted average, over 24 hours, of the test score of each model's best-on-validation submission. Each model runs once per task.</p>
<p>The top four are separated by 0.015. Resampling the 29 tasks, Opus 5.5 comes first 47% of the time, GPT-6 Astra 24%, and Claude Fable 5.1 and Gemini 4 Argon 14% each. Among the top five, no adjacent gap is statistically clear; the first clear gap is between Claude Opus 5 and Grok 4.7. 38 runs were also re-run under an unpublished policy.</p>
{board_chart()}'''
    return [('case-seed', 'Sketched Newton covariance estimator', seed), ('case-tie', 'The leaderboard', tie)]


def main():
    print(write_page(
        'autoresearchexam', 'AutoResearchExam', 'Nov. 11, 2026',
        'Anirudha Ramesh, Siddartha Devic, Shivank Garg, Advait Parulekar, Drish Mahnot, Shreyas Pimpalgaonkar, '
        'Vishnu Suresh, Alex Dimakis, Maheswaran Sathiamoorthy (Bespoke Labs)',
        'v1.0 leaderboard (tasks, graders and hidden data identical in v1.1, repository commit <code>23c0d92e</code>); '
        '29 tasks × 12 models; rollouts fetched Nov. 11, 2026',
        lede='AutoResearchExam tests whether AI agents can do open-ended ML research. Each of 29 tasks, from model '
             'merging to causal inference to CPU inference speed, gives an agent 24 hours on one machine to improve '
             'a solution, submitting as often as it likes. Each submission gets a validation score; the leaderboard '
             'uses a hidden test score, averaged over the 24 hours. All twelve models use the same harness, '
             'Terminus 2.<sup><a href="#na">a</a></sup>',
        found=['We reviewed all 29 tasks and all 353 published runs. <strong>4 tasks (14%)</strong> have confirmed '
               'scoring defects that change scores, below the 20% at which a benchmark is rated Flawed.',
               'One is a reward hack that wins its task: Grok 4.7 crashed a submission on purpose to read the '
               'grader\'s state, then rebuilt the hidden answer from a seed the grader left readable.',
               'The top four models are within 0.015 of each other and can\'t be told apart statistically. Each '
               'model ran once per task, and 38 runs were re-run under a policy that isn\'t published.',
               'Every published run can be read, which made this review possible. No agent reached the hidden '
               'test data during its run.'],
        errors=ERRORS, cases=cases(),
        cases_intro='One task where a reward hack decides the winner, and what the leaderboard can and can\'t tell '
                    'apart.',
        disclaimer='This is a full review: we read every task\'s code and screened all 353 runs, then read closely '
                   'the top run on each task and every run with a warning sign. We used AI reviewers to find every '
                   'issue, which we then hand-checked; each defect was checked again by a second reviewer '
                   'trying to refute it.<sup><a href="#nb">b</a></sup>',
        notes=[('na', f'Leaderboard and method: <a href="{SITE}">benchmarks.bespokelabs.ai/autoresearchexam</a>. '
                      'Tasks and graders: <a href="https://github.com/bespokelabsai/AutoResearchExam">'
                      'bespokelabsai/AutoResearchExam</a> at <code>23c0d92e</code>. Runs: the published rollouts '
                      f'(<a href="{SITE}public-rollout-data/index.json">index</a>).'),
               ('nb', 'Per-task reviews, the second-pass checks, the task log and all scripts are in the audit '
                      'folder linked at the top of this page.')],
        verdict='Verified', errors_heading='All issues', show_first=None))


if __name__ == '__main__':
    main()
