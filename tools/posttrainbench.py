"""Write content/reviews/posttrainbench.html, the short-form PostTrainBench review.

usage: python3 -I tools/posttrainbench.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reviewkit import BLUE, DARK, GRAY, RED, X, c, cite, configure, ev, figure, src, write_page  # noqa: E402

GH = 'https://github.com/aisa-group/PostTrainBench/blob/62c69d36a7cd1a3fb4f50e9e6352c2df13e85ccf/'
HF = 'https://huggingface.co/datasets/aisa-group/PostTrainBench-Trajectories/tree/main/'
RUNS = {  # short id -> (experiment, run name, model)
    '17415833': ('claude_non_api_claude-opus-5_10h_run1', 'humaneval_Qwen_Qwen3-4B-Base_17415833', 'Opus 5'),
    '17419570': ('claude_non_api_claude-opus-5_10h_run2', 'humaneval_Qwen_Qwen3-4B-Base_17419570', 'Opus 5'),
    '17415251': ('claude_non_api_max_claude-fable-5_1m__10h_run2',
                 'humaneval_HuggingFaceTB_SmolLM3-3B-Base_17415251', 'Fable 5'),
}
configure(lambda task, trial: HF + '/'.join(RUNS[trial][:2]), {k: v[2] for k, v in RUNS.items()})
LB = 'https://posttrainbench.com/#leaderboard'
V12 = 'https://posttrainbench.com/blog/posttrainbench-1-2/'


def gh(path, lines=None):
    """A link to a file (and lines) in the repo at the reviewed commit, shown as path:lines."""
    anchor = ''
    if lines:
        a, _, b = str(lines).partition('-')
        anchor = f'#L{a}' + (f'-L{b}' if b else '')
    label = path + (f':{lines}' if lines else '')
    return f'<a href="{GH}{path}{anchor}">{c(label)}</a>'


def task(name):
    return f'Task: {name}'


ERRORS = [
    dict(id='err-base-score',
         title='Clean HumanEval runs are scored as if they did nothing, with no reason given',
         desc='The task is to post-train a base model to write Python functions that pass HumanEval\'s unit tests. '
              'Version 1.2 gives four HumanEval cells the base model\'s score, although their runs were judged clean. '
              'Opus 5\'s two Qwen3-4B runs scored 81.7% and 83.5% in version 1.1, and Epoch AI also found them clean; '
              'in version 1.2 the cell is 36.6%, the base score. The scoring code gives the base score for a cheating '
              'flag, a missing run or a model that fails to evaluate, and the leaderboard doesn\'t say which. Our '
              'code review rules out the new HumanEval sandbox. The most likely cause is an unpublished version 1.2 '
              'judge verdict. Unconfirmed, so not counted.',
         meta=task('HumanEval: Opus 5 / Qwen3-4B, Fable 5 / SmolLM3, Grok 4.5 / SmolLM3, GLM 5.3 Flash / SmolLM3'),
         sources=[ev('humaneval', '17415833', 'scored 81.7% in version 1.1, all checks clean'),
                  ev('humaneval', '17419570', 'scored 83.5% in version 1.1, all checks clean'),
                  ev('humaneval', '17415251', 'scored 65.9% in version 1.1, all checks clean; cell now 6.1%'),
                  src(gh('scripts/collect.py', '187-210') + ': one base score for three different reasons',
                      'collect.py'),
                  src('<a href="' + LB + '">Leaderboard data</a>: ' + c('fallbackType: false') + ' in all 504 cells',
                      'leaderboard')]),
    dict(id='err-gpqa-letter',
         title='On GPQA, always answering "B" earns most of every agent\'s credit',
         desc='The task is to post-train a base model to answer graduate-level science multiple-choice questions. '
              'Base models score 2–14% because they rarely give an answer in the required format. A model that '
              'always answers "ANSWER: B" scores 26.0% across the three scoring seeds, which is worth 4.2 '
              'leaderboard points. That is 70–100% of every agent\'s GPQA credit, and GPQA carries 24% of the '
              'score. The scorer is correct, and learning the answer format is part of post-training, so this is '
              'not counted. But the most heavily weighted target barely separates the agents on the science.',
         meta=task('GPQA Main, all four base models'),
         sources=[src(gh('src/eval/tasks/gpqamain/evaluate_final_eval.py') + ': letter extraction and per-seed '
                      'shuffling', 'GPQA scorer'),
                  src('Our re-implementation: ' + c('scripts/reviewers/scorers/gpqa_letters.py') + ' in the audit '
                      'folder', 'reproduction')]),
    dict(id='err-identity',
         title='The check that the right model was submitted passes the forbidden instruct models',
         desc='Agents must post-train the base model they are given, not submit the official instruct version. '
              'The programmatic check compares only architecture fields in the model\'s config, not its weights. '
              'Our re-implementation passes the unmodified official instruct config of all four base models. The '
              'instruct versions of two of them sit in the task\'s own model cache. The LLM judge still reads every '
              'trace, and we found no swap it missed.',
         meta=task('every run'),
         sources=[src(gh('src/judges/judge_tools/model_identity_check.py', '25-35') + ': architecture fields only',
                      'identity check'),
                  src(gh('containers/download_hf_cache/resources.json') + ': Qwen3-4B and gemma-3-4b-it cached',
                      'cache list')]),
    dict(id='err-decon',
         title='The shared contamination checker skips the most common training-data format',
         desc='Agents and judges get the same tool for checking training data against the test set. It reads '
              'plain text fields, so chat-format records (' + c('messages') + ' or ' + c('conversations') + '), the '
              'usual format for fine-tuning data, produce nothing to check and come back clean. It also misses '
              'paraphrased, translated and answer-only overlap. The judge\'s instructions say a clean check does not '
              'clear a run, so the effect is small.',
         meta=task('every run'),
         sources=[src(gh('src/judges/judge_tools/contamination_check.py', '642-672') + ': reads input documents',
                      'checker'),
                  src('Our re-implementation: ' + c('scripts/reviewers/setup/decon_input_reimpl.py'),
                      'reproduction')]),
    dict(id='err-numbers',
         title='The math scorers misread a few answer formats',
         desc='The task is to post-train a base model to solve AIME and GSM8K problems; the scorer takes the last '
              'number in the answer. A number after the answer line, "(70)", "70%" or "x=70" is scored wrong, and '
              '"70.0001" or "7*10" can be scored right. The agent\'s own copy of the scorer is more lenient than '
              'the final one, and the prompt doesn\'t say so. Each case is worth well under one point.',
         meta=task('AIME 2025 and GSM8K'),
         sources=[src(gh('src/eval/exact_numeric_match.py', '30-86') + ': last-number extraction', 'scorer'),
                  src('Our tests: ' + c('scripts/reviewers/scorers/test_numeric.py'), 'tests')]),
]


def gpqa_chart():
    rows = [('Official instruct models', 36.2, DARK), ('GPT-6 Astra', 33.5, RED), ('Locus', 33.1, RED),
            ('Opus 5.5', 29.5, RED), ('Fable 5.1', 29.2, RED), ('Always answers "B"', 26.0, BLUE),
            ('Kimi K3', 25.5, RED), ('Opus 4.8', 20.9, RED), ('Gemini 3.1 Pro', 17.8, RED), ('Base models', 8.5, GRAY)]
    W, L, R, top, rh = 720, 190, 60, 26, 26
    H = top + rh * len(rows) + 26
    x = lambda v: L + (W - L - R) * v / 40
    bars = ''
    for i, (m, v, col) in enumerate(rows):
        y = top + i * rh
        bars += (f'<g><title>{m}: {v}% on GPQA, mean over the four base models</title>'
                 f'<text x="{L - 10}" y="{y + 14}" class="ylab" text-anchor="end">{m}</text>'
                 f'<rect x="{L}" y="{y + 3}" width="{x(v) - L:.1f}" height="17" rx="3" fill="{col}"/>'
                 f'<text x="{x(v) + 6:.1f}" y="{y + 16}" class="val">{v}</text></g>')
    ticks = ''.join(f'<text x="{x(v):.1f}" y="{H - 6}" class="ax" text-anchor="middle">{v}%</text>'
                    f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{top}" y2="{H - 22}" class="g"/>'
                    for v in (0, 10, 20, 30, 40))
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Bar chart of GPQA scores. Always answering B scores '
           f'26.0%. The official instruct models score 36.2%, the best agent 33.5%, and several agents score below 26%.">'
           f'{ticks}{bars}</svg>')
    return figure('GPQA Main score, mean over the four base models', svg,
                  'The blue bar is a model that always answers "B". Most of what agents earn on GPQA comes from '
                  'getting the answer format right. Source: the version 1.2 '
                  + cite('leaderboard data', X('posttrainbench.com leaderboard', LB)) + ' and our '
                  + cite('constant-answer test', X('gpqa_letters.py in the audit folder')) + '.',
                  narrow=gpqa_narrow(rows))


def gpqa_narrow(rows):
    W, L, R, rh = 380, 14, 50, 44
    top = 30
    H = top + rh * len(rows) + 24
    x = lambda v: L + (W - L - R) * v / 40
    out = ''
    for i, (m, v, col) in enumerate(rows):
        y = top + i * rh
        out += (f'<g><title>{m}: {v}%</title><text x="{L}" y="{y + 12}" class="ylab">{m}</text>'
                f'<rect x="{L}" y="{y + 18}" width="{max(x(v) - L, 2):.1f}" height="16" rx="3" fill="{col}"/>'
                f'<text x="{x(v) + 6:.1f}" y="{y + 31}" class="val">{v}</text></g>')
    ticks = ''.join(f'<text x="{x(v):.1f}" y="{H - 6}" class="ax" text-anchor="middle">{v}%</text>' for v in (0, 20, 40))
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="GPQA scores: instruct models 36.2, best agent 33.5, '
            f'always answering B 26.0, base models 8.5.">{ticks}{out}</svg>')


def cases():
    gpqa = f'''
<p>The task is to post-train a base model so it answers GPQA Main, 448 graduate-level multiple-choice questions in biology, chemistry and physics. The answer must end with a line like "ANSWER: B", and the four choices are shuffled for each of three scoring seeds.</p>
<p>Base models score between 2% and 14%, mostly because they don't answer in that format. So the first thing any agent gains is the format, and the format alone is worth a lot: a model that {cite('answers "B" to every question scores 26.0%', X('gpqa_letters.py in the audit folder'))}. The official instruct models, built by the model developers with far more compute, score 36.2%. The best agent, GPT-6 Astra, reaches 33.5%, and Kimi K3, Opus 4.8 and Gemini 3.1 Pro end up below the constant answer.</p>
<p>GPQA carries {cite('24% of the leaderboard score', X('Version 1.2 release notes', V12))}, more than any target except AIME. Nothing here is a scoring error: the scorer is correct and learning the format is a real part of post-training. But on this target, even the best agents finish only a few points above a model that always answers "B".</p>
{gpqa_chart()}'''
    return [('case-gpqa', 'GPQA Main', gpqa)]


def main():
    print(write_page(
        'posttrainbench', 'PostTrainBench', 'Nov. 4, 2026',
        'Ben Rank, Hardik Bhatnagar, Ameya Prabhu, Shira Eisenberg, Karina Nguyen, Matthias Bethge, Maksym '
        'Andriushchenko (aisa-group)',
        'v1.2, repository commit <code>62c69d36</code>; 6 target benchmarks × 4 base models; leaderboard of Nov. 4, 2026',
        lede='PostTrainBench tests whether AI agents can post-train a language model. Each agent gets 10 hours on one '
             'H100 GPU to make a small base model (Qwen3-1.7B, Qwen3-4B, SmolLM3-3B or Gemma-3-4B) score as high as '
             'possible on one target benchmark, such as AIME 2025, GPQA or HumanEval. That makes 24 tasks, and each '
             'agent runs each one two or three times. LLM judges read every run for cheating.'
             '<sup><a href="#na">a</a></sup>',
        found=['We reviewed all 24 tasks and found that <strong>none</strong> had grading errors that affect the '
               'score. A benchmark is rated Flawed when errors affect at least 20% of its score.',
               'We found no reward hacks. In each of the 24 tasks we read the highest-scoring run that the '
               'benchmark\'s cheating checks did not flag, and every one is legitimate: no test data in training, '
               'no swapped-in model, no tampering with the evaluation.',
               'Seven of the 19 entries, including the top five, have no public runs, so their results can\'t be '
               'checked.'],
        errors=ERRORS, cases=cases(),
        disclaimer='This is a full review of the code and a targeted review of runs: we read the top unflagged run in '
                   'every task, not every run. We used AI reviewers to find every issue, which we then hand-checked. '
                   'We reviewed version 1.2; Epoch AI reviewed version 1.1 and rated it Verified.'
                   '<sup><a href="#nb">b</a></sup>',
        notes=[('na', 'Leaderboard: <a href="https://posttrainbench.com">posttrainbench.com</a>. Code: '
                      '<a href="https://github.com/aisa-group/PostTrainBench">aisa-group/PostTrainBench</a> at '
                      '<code>62c69d36</code>. Paper: <a href="https://arxiv.org/abs/2603.08640">arXiv 2603.08640</a>.'),
               ('nb', 'Epoch AI\'s review of version 1.1: '
                      '<a href="https://epoch.ai/benchmarks/post-train-bench/review">epoch.ai</a>, Sep. 9, 2026.')],
        verdict='Verified', errors_heading='All issues'))


if __name__ == '__main__':
    main()
