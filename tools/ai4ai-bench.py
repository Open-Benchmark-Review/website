"""Write content/reviews/ai4ai-bench.html, the short-form AI4AI-Bench review.

usage: python3 -I tools/ai4ai-bench.py

Chart data comes from audits/ai4ai-bench/data/cells.json (σ recomputed from the 290 case pages with the paper's
Table 2 anchors) and tools/data/ai4ai-bench_ddpo.json (each DDPO cell's alignment and diversity table, from its case
page).
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reviewkit import (BLUE, DARK, E, GRAY, RED, REPO, X, c, cite, configure, figure, write_page)  # noqa: E402

CASES = 'https://lab.einsia.ai/ai4ai/trajectories/'
SHA = '5ced1e2eb1882baf52e6d928f9257006aa71968c'
GH = f'https://github.com/Einsia/AI4AI-Bench/blob/{SHA}/'
TREE = f'https://github.com/Einsia/AI4AI-Bench/tree/{SHA}/tasks/'
RAGEN_GH = 'https://github.com/RAGEN-AI/RAGEN/blob/20daedc4/'
UPSTREAM = RAGEN_GH + 'config/base.yaml#L8-L10'
PAPER = 'https://arxiv.org/abs/2608.20318'
AUDIT = f'{REPO}/blob/main/audits/ai4ai-bench/'
DATA = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'audits', 'ai4ai-bench', 'data')
# Each DDPO cell's per-checkpoint aesthetic score, CLIP alignment and pairwise distance, copied from its case page.
DDPO_DATA = os.path.join(HERE, 'data', 'ai4ai-bench_ddpo.json')

RAGEN = 'ragen_sokoban_grpo'
DDPO = 'ddpo_sd15_aesthetic'
NPO = 'openunlearning_tofu_npo_llama3p2_1b'
BTRM = 'ultrafeedback_bt_rm_rewardbench'
# One name per task, used everywhere on the page. "RAGEN" is kept for the upstream repository only.
TNAME = {RAGEN: 'Sokoban task', DDPO: 'DDPO image task', NPO: 'NPO unlearning task', BTRM: 'BTRM reward-model task'}

# A "cell" is one model at one effort on one task. Its case page is the closest thing to an attempt page;
# the cell is named by its configuration with the model's full name, e.g. "Claude Opus 5 high".
SYS = {'claude-opus-5': ('claude', 'Opus 5'), 'claude-sonnet-5': ('claude', 'Sonnet 5'), 'kimi-k3': ('claude', 'Kimi K3'),
       'gpt-5.6-sol': ('codex', 'Sol'), 'gpt-5.6-terra': ('codex', 'Terra'), 'gpt-5.6-luna': ('codex', 'Luna')}
FULL = {'Opus 5': 'Claude Opus 5', 'Sonnet 5': 'Claude Sonnet 5', 'Kimi K3': 'Kimi K3', 'Sol': 'GPT-5.6 Sol',
        'Terra': 'GPT-5.6 Terra', 'Luna': 'GPT-5.6 Luna'}
FULL2ID = {FULL[v[1]]: k for k, v in SYS.items()}


def case_url(task, cell):
    """cell is "Claude Opus 5 high", optionally with its task: "Sokoban task, Claude Opus 5 high" in hover
    citations, "Claude Opus 5 high in the Sokoban task" in Where lists that span tasks."""
    cell = cell.split(', ', 1)[-1].split(' in the ', 1)[0]
    name, effort = cell.rsplit(' ', 1)
    mid = FULL2ID[name]
    return f'{CASES}{SYS[mid][0]}__{task}__{mid}__{effort}/'


configure(case_url, {})


def EC(task, cell):
    """A hover-citation entry for one cell. The surrounding text names the task, so the popup gives the cell only."""
    return E(task, cell)


def gh(path, line=None, text=None):
    """Link to a file in the repo at the reviewed commit. The link text is the file name and lines only; the task
    is named on the Task line and the href keeps the full path."""
    frag = ''
    if line:
        a, _, b = str(line).partition('-')
        frag = f'#L{a}' + (f'-L{b}' if b else '')
    name = os.path.basename(path) + (':' + str(line) if line else '')
    return f'<a href="{GH}{path}{frag}">{html.escape(text or name)}</a>'


def task(slug):
    return f'Task: <a href="{TREE}{slug}">{TNAME[slug]}</a> ({c(slug)})'


T = 'tasks/'
OPENR1 = 'openr1_code_livecodebench'
TNAME[OPENR1] = 'OpenR1 code-generation task'
# Short task names, shown beside a cell in Where lists that span tasks.
SHORT = {RAGEN: 'Sokoban', DDPO: 'DDPO', NPO: 'NPO', BTRM: 'BTRM', OPENR1: 'OpenR1'}
# The benchmark's own one-line description of each task, from its task gallery.
GALLERY = 'https://lab.einsia.ai/ai4ai/tasks/'
ONELINE = {RAGEN: 'Improve a fixed 3B policy on multi-turn Sokoban',
           DDPO: 'Improve Stable Diffusion v1.5 under a fixed aesthetic evaluator',
           NPO: 'Improve Llama-3.2-1B unlearning on fixed TOFU assets',
           BTRM: 'Improve a scalar reward model scored on RewardBench v1',
           OPENR1: 'Improve a fixed 1.5B code model, scored by LiveCodeBench'}
# A second paragraph inside an error description.
P2 = '</p><p class="ed" style="margin-top: 8px">'

# Where lists. Each source has a kind; the folded summary counts them by kind ("4 repo files, 6 cells · 11 sources")
# instead of listing every cell by name. reviewkit's _where() shows a source's label once, so tally() puts the count
# for each kind on the first source of that kind.
KINDS = {'file': ('repo file', 'repo files'), 'cell': ('cell', 'cells'), 'audit': ('audit file', 'audit files'),
         'paper': ('paper', 'paper'), 'upstream': ('upstream RAGEN file', 'upstream RAGEN files'),
         'site': ('task gallery', 'task gallery')}


def S(kind, text):
    return dict(trial=None, label=None, kind=kind, html=text)


def site(tk):
    """The task's page in the benchmark's own task gallery, with its one-line description."""
    return S('site', f'<a href="{GALLERY}{tk}/">Task gallery</a>: "{ONELINE[tk]}"')


def cell(tk, name, detail, show_task=False):
    """One cell in a Where list: its case-page link, then what to look at. show_task adds the task's short name, for
    lists that span tasks."""
    t = f' <span class="mdl">{SHORT[tk]}</span>' if show_task else ''
    return S('cell', f'<a class="att" href="{case_url(tk, name)}">{name}</a>{t} · {detail}')


def tally(sources):
    n, seen = {}, set()
    for s in sources:
        n[s['kind']] = n.get(s['kind'], 0) + 1
    for s in sources:
        if s['kind'] not in seen:
            seen.add(s['kind'])
            one, many = KINDS[s['kind']]
            k = n[s['kind']]
            s['label'] = (f'{k} ' if one != many else '') + (one if k == 1 else many)
    return sources


def upstream(path, lines, text):
    a, _, b = lines.partition('-')
    return f'<a href="{RAGEN_GH}{path}#L{a}-L{b}">{os.path.basename(path)}:{lines}</a>, RAGEN at {c("20daedc4")}: {text}'


TASK_ERRORS = [
    dict(id='err-ragen-seed',
         title="The Sokoban test boards can be rebuilt inside the agent's workspace",
         desc='The task is to “improve a fixed 3B policy on multi-turn Sokoban”: train the Qwen2.5-3B model, by '
              'reinforcement learning, to solve small box-pushing puzzles. The score is the share of 512 test boards it '
              'solves. The boards are generated from one number, the seed 123, and the task treats that seed as the '
              'only thing kept from the agent. But 123 is also the default seed in the upstream RAGEN code that the task '
              "copies into the agent's workspace, so RAGEN's stock evaluation, run there, plays the first 32 test "
              'boards, and the full set can be rebuilt. On 17 of the 19 case pages that confirm this exposure, the '
              'field for whether the agent used it is marked not adjudicated, and the other two record no use.'
              + P2 + 'The board space is also small. Training sets that the task\'s built-in solver generated from other '
              'seeds each covered 243 to 454 of the 512 test boards, and five cells solve all 512. Two of the top '
              'scorers, GPT-5.6 Sol max (512/512) and GPT-5.6 Terra max (511/512), are why Claude Opus 5 falls from '
              'first to third when systems are compared at maximum effort.',
         meta=task(RAGEN),
         sources=tally([
             site(RAGEN),
             S('file', gh(T + RAGEN + '/declaration.py', '49-50') + ': "The final seed stays host-side so '
                       'exploration cannot reconstruct the held-out boards", ' + c('FINAL_ENVIRONMENT_SEED = 123')),
             S('upstream', upstream('config/base.yaml', '8-10', c('seed: train: 10000, val: 123'))),
             S('upstream', upstream('config/eval.yaml', '12-14', c('val: 123') + ', with 32 board groups of the same '
                                    '6×6 one-box Sokoban; each group gets the seed plus its index')),
             S('file', gh(T + RAGEN + '/environment/Dockerfile', 95) + ': '
                       + c('cp -a /opt/build/src/ragen /workspace/ragen')),
             S('file', gh(T + RAGEN + '/harness/grade.py', '485-500') + ': the final run uses RAGEN\'s ' + c('eval')
                       + ' config with ' + c('seed.val') + ' set to the final seed; "' + c('seed.val') + ' is what the '
                       'board generator consumes"'),
             S('file', gh(T + RAGEN + '/harness/grade.py', 879) + ': "the seed is the entire withheld quantity"'),
             S('file', gh(T + RAGEN + '/environment/check_image.py', '160-176') + ': the build check meant to keep the '
                       'final seed out of the image skips every path containing ' + c('/ragen/') + ' and searches only '
                       + c('.py') + ' files, while the seed sits in YAML'),
             S('file', gh(T + RAGEN + '/harness/fast_eval.py', 236) + ': hard-codes '
                       + c('"proxy_final_overlap_fraction": 0.0') + ', though the case pages report that 7 of the '
                       'exploration boards are among the 512 test boards'),
             S('audit', f'<a href="{AUDIT}data/cases.csv">cases.csv</a>: the Sokoban case pages\' audit fields; '
                        'exposure confirmed on 19 of 29, and "Observed use" is "Not Adjudicated" on 17 of those 19'),
             cell(RAGEN, 'Claude Opus 5 high', '512/512; its training set covers 454 of the 512 test boards'),
             cell(RAGEN, 'Claude Opus 5 medium', 'pure supervised checkpoint scores 512/512; "GRPO tied it and '
                                                 'showed no measurable benefit"; at least 422 of 512 covered'),
             cell(RAGEN, 'Claude Opus 5 low', '512/512'),
             cell(RAGEN, 'GPT-5.6 Sol high', '512/512'),
             cell(RAGEN, 'GPT-5.6 Sol max', '512/512; its three training sets cover 442, 451 and 448 of 512 (490 '
                                            'combined); seed literal in tool-result records #19, #29, #76, #84, #98, '
                                            '#104, #259'),
             cell(RAGEN, 'GPT-5.6 Terra max', '511/512; its three training sets cover 243, 396 and 399 of 512'),
             cell(RAGEN, 'Claude Opus 5 max', '120/512 with a GRPO variant (σ 0.170)'),
             S('audit', f'<a href="{AUDIT}data/ranking.md">ranking.md</a>: max-effort means with and without the '
                        'Sokoban task')])),
    dict(id='err-ddpo-collapse',
         title='The DDPO image score rewards pictures that ignore their prompts',
         desc='The task is to “improve Stable Diffusion v1.5 under a fixed aesthetic evaluator”: fine-tune the image '
              'model so that a fixed rating model judges its pictures of animals better-looking. The score is that '
              'model\'s average rating over 256 pictures, and the same rating model is available during training. The '
              'task also reports whether the pictures still match their prompts (CLIP alignment) and still differ from '
              'each other (pairwise distance), but its instruction says these are "not validity gates or terms in the '
              'headline score".'
              + P2 + 'Eight cells trained against the rating model directly, or over-trained the shipped method, and '
              'raised the rating from the shipped 5.53 to between 6.8 and 17.7. On their best checkpoints alignment '
              'fell to 0.10–0.19 and pairwise distance to 0.05–0.23, against about 0.234 and 0.365 for the unchanged '
              "recipe. These eight cells supply 94% of the task's σ above the baseline. We picked them by one rule: the "
              "best checkpoint beats the paper's 5.84 baseline and its alignment is below 0.19, while every other cell "
              'above the baseline stays above 0.23.',
         meta=task(DDPO),
         sources=tally([
             site(DDPO),
             S('file', gh(T + DDPO + '/instruction.md', 23) + ': "CLIP alignment and pairwise image distance are '
                       'reported as auxiliary diagnostics, not validity gates or terms in the headline score"'),
             S('file', gh(T + DDPO + '/harness/final_eval.py', 233) + ': "the original DDPO benchmark has no '
                       'alignment/diversity guard", so the task follows the method it is built on'),
             S('file', gh('tasks/README.md', 9, 'tasks/README.md:9') + ': the one place that calls them gates, '
                       '"mean aesthetic score with alignment/diversity gates"'),
             cell(DDPO, 'Claude Opus 5 max', '17.67 (σ 0.712); "Every checkpoint triggered both alerts: alignment was '
                                             '0.1043–0.1136 and pairwise distance 0.0414–0.0478"'),
             cell(DDPO, 'Claude Opus 5 xhigh', '14.45; alignment 0.113, distance 0.071'),
             cell(DDPO, 'Claude Opus 5 low', '12.13; alignment 0.096, distance 0.067'),
             cell(DDPO, 'Kimi K3 max', '9.04; alignment 0.147, distance 0.151'),
             cell(DDPO, 'GPT-5.6 Sol max', '8.98; alignment 0.187, distance 0.225'),
             cell(DDPO, 'Claude Opus 5 high', '8.42; alignment 0.151, distance 0.084'),
             cell(DDPO, 'GPT-5.6 Sol medium', '6.83, long PPO; alignment 0.181, distance 0.232; borderline'),
             cell(DDPO, 'Claude Opus 5 medium', '8.98; alignment 0.182, distance 0.185; the weakest of the eight, and '
                                                'its page does not call it an alert'),
             cell(DDPO, 'GPT-5.6 Terra high', '6.62, not counted; alignment 0.237 but distance 0.265, a diversity '
                                              'alert; GPT-5.6 Luna max (distance 0.260) is similar'),
             cell(DDPO, 'GPT-5.6 Terra low', 'the unchanged recipe re-run: 5.54, alignment 0.234, distance 0.365'),
             S('file', 'A second, smaller issue: the test seed, which the task keeps in a score-only file, is also '
                       'hard-coded in harness code the agent can read. ' + gh(T + DDPO + '/declaration.py', '16-20')
                       + ': "a seed written there would be published"; '
                       + gh(T + DDPO + '/environment/assets.lock.yaml', 138) + ': ' + c('generation_seed: 20269702')
                       + '; the same value in ' + gh(T + DDPO + '/harness/final_eval.py', 261) + ', '
                       + gh(T + DDPO + '/harness/final_eval.py', 285, ':285') + ' and '
                       + gh(T + DDPO + '/harness/grade.py', 308))])),
    dict(id='err-npo-optimum',
         title="The NPO task's perfect mark is above its highest possible score",
         desc='The task is to “improve Llama-3.2-1B unlearning on fixed TOFU assets”: make a small language model '
              'forget a set of facts about fictional authors while keeping the rest of what it knows. The task\'s code '
              'scores a run by combining how much was forgotten and how much ability was kept, each capped at 1, so the '
              'score cannot exceed 1.0. The paper sets the perfect mark at 2.08, so a perfect 1.0 maps to σ 0.185, '
              "against 0.1 for the shipped recipe's 0.887. Any gain over the shipped recipe counts for about a tenth of "
              'what it would if the perfect mark were 1.0.'
              + P2 + '24 of the 29 cells beat 0.887, and 22 of them also beat 0.923, the score of a cell whose only '
              'change was skipped, so that it re-ran the unchanged recipe. Five cells reach the cap of 1.0. The '
              "paper's own table is not on the code's scale: it prints 1.01 to 1.03 for those five, and an uncapped "
              'version of the formula reproduces its values in the cells we checked. Under that version the best '
              'possible score is about 1.3, still well below 2.08.',
         meta=task(NPO),
         sources=tally([
             site(NPO),
             S('file', gh(T + NPO + '/harness/final_eval.py', '192-221') + ': ' + c('clip01') + ' on both terms, '
                       'then their harmonic mean'),
             S('paper', f'<a href="{PAPER}">Paper, Table 2</a>: NPO baseline 0.887, optimum 2.08; the NPO column '
                        'prints 1.01, 1.01, 1.02, 1.03 and 1.03 for the five cells below'),
             cell(NPO, 'Claude Opus 5 max', '1.0, σ 0.185; "both normalized components of the balanced score clip to '
                                            'one"'),
             cell(NPO, 'Claude Opus 5 medium', '1.0, σ 0.185'),
             cell(NPO, 'Claude Opus 5 high', '1.0, σ 0.185'),
             cell(NPO, 'Claude Opus 5 xhigh', '1.0, σ 0.185'),
             cell(NPO, 'GPT-5.6 Sol xhigh', '1.0, σ 0.185; "the official balanced_unlearning_score ceiling of 1.0"'),
             cell(NPO, 'GPT-5.6 Terra xhigh', '0.923; its only patch hunk was skipped, so the run replayed the '
                                              'shipped recipe'),
             cell(NPO, 'GPT-5.6 Luna max', '0.9275 on the page, 0.945 in the paper; uncapped, the page\'s components '
                                           'give 0.945'),
             S('audit', f'<a href="{AUDIT}tasks/{NPO}.md">Audit task note</a>: the count of improved cells and the '
                        'uncapped recomputation')])),
    dict(id='err-btrm-noise',
         title="The BTRM reward-model task's baseline sits inside its own seed noise",
         desc='The task is to “improve a scalar reward model scored on RewardBench v1”: train a 7B model to judge '
              'which of two answers is better, scored on a public test set of answer pairs. The task calls its 74.57 '
              'reference "seed-sensitive" and "a single-run reference", and the paper sets the baseline at 74.9. '
              'Replays of the unchanged recipe with different random seeds score 65.41 to 73.95, a spread of about 8.5 '
              'points against a reported standard error of about 0.8. Seven of the eight cells above the baseline '
              'clear it by less than a point, and all but two of the cells below it fall short by less than that '
              '8.5-point spread.',
         meta=task(BTRM),
         sources=tally([
             site(BTRM),
             S('file', gh(T + BTRM + '/instruction.md', 31) + ': "RewardBench is seed-sensitive, so treat it as a '
                       'single-run reference"; ' + gh(T + BTRM + '/instruction.md', 37, ':37') + ': '
                       + c('74.568936')),
             S('paper', f'<a href="{PAPER}">Paper, Table 2</a>: BTRM baseline 74.9'),
             cell(BTRM, 'GPT-5.6 Sol low', 'unchanged recipe at seeds 42, 7 and 1729: 73.95, 66.31, 65.41'),
             cell(BTRM, 'GPT-5.6 Sol xhigh', 'unchanged recipe at seed 42: 73.835'),
             cell(BTRM, 'Claude Opus 5 medium', '77.09 (σ 0.179), the only cell more than 2 standard errors above '
                                                'the baseline'),
             S('file', 'A second issue: the official score includes the 512 proxy pairs the agent saw while '
                       'exploring. ' + gh(T + BTRM + '/harness/final_eval.py', '339-340') + ': the reported score is '
                       + c('score_final') + ', over all 2,985 pairs including the 512 proxy pairs')])),
    dict(id='err-openr1-baseline',
         title="The OpenR1 task's baseline is above every replay of its recipe",
         desc='The task is to “improve a fixed 1.5B code model, scored by LiveCodeBench”, a set of programming '
              "problems. The paper sets the baseline at 0.127, the case pages' single run of the shipped recipe "
              "(0.12743). The task's own instruction reports six replays of that recipe, with a mean of 0.1229 and a "
              'range of 0.1200 to 0.1257. Using the replay mean as the baseline flips 11 cells between beating and '
              "missing it, but moves each cell's σ by less than 0.005.",
         meta=task(OPENR1),
         sources=tally([
             site(OPENR1),
             S('file', gh(T + OPENR1 + '/instruction.md', 41) + ': six replays of the shipped recipe, mean 0.12286, '
                       'SD 0.00188, range 0.1200 to 0.1257'),
             S('paper', f'<a href="{PAPER}">Paper, Table 2</a>: OpenR1 baseline 0.127, the case pages\' single-run '
                        'shipped reference of 0.12743'),
             S('audit', f'<a href="{AUDIT}tasks/{OPENR1}.md">Audit task note</a>: with the replay mean as baseline, '
                        'cells below it drop from 25 to 14 and the task mean σ moves from 0.091 to 0.095; logged as '
                        'minor because the change is under 0.006 σ per cell')])),
]
WIDE_ERRORS = [
    dict(id='err-checkpoint',
         title="Each run's best of three checkpoints is picked on the test set",
         desc="In every task, the agent's code is re-run in a fresh training run of up to 12 hours that keeps up to "
              'three checkpoints, saved copies of the model, and each one is scored on the held-out test. The '
              "cell's result is the best of them. The paper and every task's instruction say so, but neither explains "
              'why the test set, rather than a rule fixed in advance, should do the choosing, and the choice biases '
              'scores upward.'
              + P2 + 'Best and last checkpoint score differently in 148 of the 271 cells that produced a checkpoint. '
              'Reporting the last one instead lowers the mean σ from 0.165 to 0.158 and flips 21 cells between '
              'beating and missing the baseline. "Last" is only a rough comparison, because at least 18 case pages say '
              'their three checkpoints are separate seeds or branches, not points along one training run.',
         meta='Affects: all 10 tasks',
         sources=tally([
             S('paper', f'<a href="{PAPER}">Paper, §2.3</a>: "the cell takes the best of them under the task\'s '
                        'direction"'),
             S('file', gh(T + RAGEN + '/instruction.md', 17, f'{RAGEN}/instruction.md:17') + ', the same line in all '
                       'ten tasks: "the run\'s official result is the best valid final score among them"'),
             S('file', gh('orchestrator/final_score.py', 148, 'orchestrator/final_score.py:148') + ': '
                       + c('selected = max(valid, ...)') + ' over the final-metric scores, with ties going to the later '
                       'checkpoint. The case pages label 163 cells "Best is an earlier checkpoint", but 16 of those '
                       'are exact ties'),
             S('audit', f'<a href="{AUDIT}data/cases.csv">cases.csv</a>: the status and checkpoint columns of the 290 '
                        'case pages; 271 completed with a checkpoint, and the rest ended without one (10 terminal, 8 '
                        'source unavailable, 1 recipe failure)'),
             cell(RAGEN, 'Kimi K3 max', 'checkpoints solve 95, 44 and 2 of 512 boards; reports 95, above the '
                                        'shipped 87', show_task=True),
             cell(RAGEN, 'Claude Opus 5 xhigh', 'checkpoints solve 108, 84 and 22 of 512 boards; reports 108',
                  show_task=True),
             cell(BTRM, 'GPT-5.6 Sol max', 'three different setups as checkpoints (a seed-42 run, a label-smoothed '
                                           'variant and a seed-1009 run), scoring 65.30 to 73.89', show_task=True),
             cell(BTRM, 'Kimi K3 max', 'seeds 42, 7 and 1234 as checkpoints: 74.12, 65.62, 71.81; "Slots are '
                                       'publication order, not progress"', show_task=True),
             S('audit', f'<a href="{AUDIT}data/rescoring.md">Rescoring of all 290 cells</a> under best-of-3 and '
                        'last checkpoint')])),
]
ERRORS = [
    dict(title='In single tasks',
         lead='The first four errors are the ones behind the 4 of 10 tasks in the summary. The OpenR1 one is not '
              'counted because it changes σ by less than 0.005 per cell.',
         rows=TASK_ERRORS),
    dict(title='Across all tasks',
         lead='This error affects every task, so it is not in the 4-task count.',
         rows=WIDE_ERRORS),
]


# --- Data ------------------------------------------------------------------------------------

def load_cells():
    return json.load(open(os.path.join(DATA, 'cells.json'), encoding='utf-8'))


def load_ddpo():
    """Each DDPO cell's checkpoint with the highest aesthetic score (the reported one), with its CLIP alignment and
    pairwise distance, from the diagnostics table on its case page."""
    out = []
    for r in json.load(open(DDPO_DATA, encoding='utf-8'))['cells']:
        if r['checkpoints']:
            best = max(r['checkpoints'], key=lambda k: k['aesthetic'])
            out.append(dict(model=r['model'], effort=r['effort'], **best))
    return out


def label(cell):
    return f'{SYS[cell["model"]][1]} {cell["effort"]}'


def collapsed(d):
    """The rule for the eight DDPO cells: beats the paper's 5.84 baseline with CLIP alignment below 0.19."""
    return d['aesthetic'] > 5.84 and d['alignment'] < 0.19


# --- Charts ----------------------------------------------------------------------------------

# A white outline behind narrow-chart labels, so the gridlines that cross them do not run through the text.
HALO = ' stroke="#fff" stroke-width="5" stroke-linejoin="round" paint-order="stroke" '

SOLVER = {'Opus 5 high', 'Opus 5 low', 'Opus 5 medium', 'Sonnet 5 high', 'Sol high', 'Sol low', 'Sol max',
          'Sol xhigh', 'Terra max'}
ORDER = ['Opus 5', 'Sol', 'Terra', 'Sonnet 5', 'Kimi K3', 'Luna']
# Annotations for the rows with perfect or near-perfect cells.
TOPNOTE = {'Opus 5': '512/512: low, medium, high', 'Sol': '512/512: high, max', 'Terra': '511/512: max'}


def dot(col, hollow=False):
    """A legend swatch drawn as a dot, to match the chart marks (figure() draws a bar by default)."""
    base = 'width:10px;height:10px;border-radius:50%;box-sizing:border-box'
    return (f'#fff;{base};box-shadow:inset 0 0 0 1.5px {col}' if hollow else f'{col};{base}')


def ragen_marks(rows, x, y_of, r, stack):
    """Dots for each system's Sokoban cells. stack(cluster_size) gives the vertical offsets within a cluster."""
    out = ''
    for i, s in enumerate(ORDER):
        y = y_of(i)
        pts = sorted(rows[s], key=lambda cl: (cl['best'] or 0))
        clusters = []
        for cl in pts:
            v = cl['best'] or 0.0
            if clusters and abs((clusters[-1][0]['best'] or 0.0) - v) < 0.03:
                clusters[-1].append(cl)
            else:
                clusters.append([cl])
        for group in clusters:
            for dy, cl in zip(stack(len(group)), group):
                v = cl['best'] or 0.0
                lab = label(cl)
                col = RED if v == 1.0 else BLUE if lab in SOLVER else GRAY
                what = f'{round(v * 512)}/512 boards solved' if cl['n'] else 'no checkpoint, scored 0'
                kind = 'solver imitation' if lab in SOLVER else 'GRPO variant' if cl['n'] else 'failed run'
                fill = col if cl['n'] else '#fff'
                out += (f'<circle cx="{x(v):.1f}" cy="{y + dy:.1f}" r="{r}" fill="{fill}" '
                        f'stroke="{col if cl["n"] else DARK}" stroke-width="1.5"><title>Sokoban task, {FULL[s]} '
                        f'{cl["effort"]}: {what} ({kind})</title></circle>')
    return out


RAGEN_ARIA = ('Dot plot of the 29 Sokoban task cells by system. Five cells, Claude Opus 5 low, medium and high and '
              'GPT-5.6 Sol high and max, solve all 512 test boards, and GPT-5.6 Terra max solves 511. Three other '
              'solver-imitation cells score between 281 and 458. The GRPO variants sit near the shipped recipe at '
              '87 of 512, and six runs with no checkpoint score 0.')


def ragen_chart(cells):
    rows = {s: [] for s in ORDER}
    for cell in cells:
        if cell['task'] == RAGEN:
            rows[SYS[cell['model']][1]].append(cell)

    # Wide layout: names in a left gutter, notes for the top cells on the right.
    W, L, R, TOP, rowh = 720, 140, 120, 26, 40
    H = TOP + rowh * len(ORDER) + 28
    x = lambda v: L + (W - L - R) * v
    grid = ''.join(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{TOP - 6}" y2="{H - 26}" class="g"/>'
                   f'<text x="{x(v):.1f}" y="{H - 8}" class="ax" text-anchor="middle">{int(v * 512)}</text>'
                   for v in (0, 0.25, 0.5, 0.75, 1.0))
    base = x(87 / 512)
    y_of = lambda i: TOP + i * rowh + rowh / 2
    marks = ''
    for i, s in enumerate(ORDER):
        y = y_of(i)
        marks += f'<text x="{L - 14}" y="{y + 4:.1f}" class="ylab" text-anchor="end">{FULL[s]}</text>'
        marks += f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" class="g" stroke-dasharray="2 3"/>'
        if s in TOPNOTE:
            marks += (f'<text x="{x(1) + 14:.1f}" y="{y + 4:.1f}" class="lab">'
                      f'{TOPNOTE[s].split(": ")[1] if s != "Terra" else "max, 511/512"}</text>')
    marks += ragen_marks(rows, x, y_of, 6, lambda n: [0, -9, 9, -18, 18][:n])
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{RAGEN_ARIA}">{grid}'
           f'<line x1="{base:.1f}" x2="{base:.1f}" y1="{TOP - 10}" y2="{H - 26}" class="cap"/>'
           f'<text x="{base + 5:.1f}" y="{TOP - 12}" class="lab">shipped recipe, 87</text>'
           f'<text x="{x(1) - 5:.1f}" y="{TOP - 12}" class="lab" text-anchor="end">optimum, 512</text>'
           f'{marks}</svg>')

    # Narrow layout: names above each row, the notes for the top cells beside the name, three ticks.
    W, L, R, TOP, rowh = 380, 16, 18, 40, 70
    H = TOP + rowh * len(ORDER) + 30
    x = lambda v: L + (W - L - R) * v
    grid = ''.join(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{TOP - 6}" y2="{H - 28}" class="g"/>'
                   for v in (0, 0.25, 0.5, 0.75, 1.0))
    grid += ''.join(f'<text x="{x(v):.1f}" y="{H - 8}" class="ax" text-anchor="{a}">{int(v * 512)}</text>'
                    for v, a in ((0, 'start'), (0.5, 'middle'), (1.0, 'end')))
    base = x(87 / 512)
    y_of = lambda i: TOP + i * rowh + 46
    marks = ''
    for i, s in enumerate(ORDER):
        y0 = TOP + i * rowh
        marks += f'<text x="{L}" y="{y0 + 18:.1f}" {HALO}class="ylab">{FULL[s]}</text>'
        if s in TOPNOTE:
            marks += f'<text x="{W - R}" y="{y0 + 18:.1f}" {HALO}class="sub" text-anchor="end">{TOPNOTE[s]}</text>'
        marks += (f'<line x1="{L}" x2="{W - R}" y1="{y_of(i):.1f}" y2="{y_of(i):.1f}" class="g" '
                  f'stroke-dasharray="2 3"/>')
    marks += ragen_marks(rows, x, y_of, 6, lambda n: [(k - (n - 1) / 2) * 11 for k in range(n)])
    narrow = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{RAGEN_ARIA}">{grid}'
              f'<line x1="{base:.1f}" x2="{base:.1f}" y1="{TOP - 16}" y2="{H - 28}" class="cap"/>'
              f'<text x="{base + 5:.1f}" y="{TOP - 20}" {HALO}class="lab">shipped recipe, 87</text>'
              f'<text x="{x(1):.1f}" y="{TOP - 20}" class="lab" text-anchor="end">optimum, 512</text>'
              f'{marks}</svg>')

    title = 'Test boards solved out of 512, each Sokoban task cell (best of three checkpoints)'
    return figure(title, svg, 'How copying the built-in solver reached perfect scores. One dot per model and effort '
                  'level, at its best checkpoint; runs a few boards apart are stacked. The red dots at 512 are Claude '
                  'Opus 5 low, medium and high and GPT-5.6 Sol high and max, and GPT-5.6 Terra max solved 511. Hollow '
                  'dots produced no checkpoint, which the paper scores as 0.<sup><a href="#nf">f</a></sup> Source: the '
                  'checkpoint scores on the 29 Sokoban task case pages.',
                  legend=[(dot(RED), 'solver imitation, 512/512'), (dot(BLUE), 'solver imitation, fewer boards'),
                          (dot(GRAY), 'GRPO variants'), (dot(DARK, hollow=True), 'no checkpoint, scored 0')],
                  narrow=narrow)


DDPO_LABELS = {('claude-opus-5', 'max'): 'Claude Opus 5 max', ('claude-opus-5', 'xhigh'): 'Claude Opus 5 xhigh',
               ('claude-opus-5', 'low'): 'Claude Opus 5 low'}


def ddpo_marks(pts, x, y, r):
    out = ''
    for d in sorted(pts, key=collapsed):
        col = RED if collapsed(d) else GRAY
        name = f'{FULL[SYS[d["model"]][1]]} {d["effort"]}'
        out += (f'<circle cx="{x(d["aesthetic"]):.1f}" cy="{y(d["alignment"]):.1f}" r="{r}" fill="{col}" '
                f'fill-opacity="{1 if col == RED else 0.75}" stroke="#fff" stroke-width="1">'
                f'<title>DDPO image task, {name}: aesthetic score {d["aesthetic"]:g}, CLIP alignment '
                f'{d["alignment"]:g}, pairwise distance {d["distance"]:g}</title></circle>')
    return out


DDPO_ARIA = ('Scatter plot of the 28 DDPO image task cells with a checkpoint: aesthetic score of the reported '
             'checkpoint against its CLIP alignment. Twenty cells sit near the unchanged recipe, at aesthetic 4.5 to '
             '6.6 and alignment about 0.23. Eight cells, in red, reach aesthetic 6.8 to 17.7 while alignment falls to '
             '0.10 to 0.19; Claude Opus 5 max is furthest, at 17.67 and 0.109.')


def ddpo_chart(pts):
    xlo, xhi, ylo, yhi = 4, 18, 0.08, 0.26
    lab = {k: v for k, v in DDPO_LABELS.items()}

    # Wide layout.
    W, L, R, TOP, B = 720, 64, 24, 34, 46
    H = 360
    x = lambda v: L + (W - L - R) * (v - xlo) / (xhi - xlo)
    y = lambda v: TOP + (H - TOP - B) * (yhi - v) / (yhi - ylo)
    grid = ''.join(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{TOP}" y2="{H - B}" class="g"/>'
                   f'<text x="{x(v):.1f}" y="{H - B + 18}" class="ax" text-anchor="middle">{v}</text>'
                   for v in (4, 6, 8, 10, 12, 14, 16, 18))
    grid += ''.join(f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="g"/>'
                    f'<text x="{L - 8}" y="{y(v) + 4:.1f}" class="ax" text-anchor="end">{v:.2f}</text>'
                    for v in (0.10, 0.15, 0.20, 0.25))
    grid += (f'<text x="{L}" y="{TOP - 12}" class="sub">CLIP alignment: do the pictures match their prompts?</text>'
             f'<text x="{W - R}" y="{H - 6}" class="sub" text-anchor="end">aesthetic score of the reported '
             'checkpoint</text>')
    refs = (f'<line x1="{x(5.84):.1f}" x2="{x(5.84):.1f}" y1="{TOP}" y2="{H - B}" class="cap"/>'
            f'<text x="{x(5.84) + 6:.1f}" y="{y(0.085):.1f}" class="lab">paper\'s baseline, 5.84</text>'
            f'<line x1="{L}" x2="{W - R}" y1="{y(0.234):.1f}" y2="{y(0.234):.1f}" class="cap"/>'
            f'<text x="{W - R}" y="{y(0.234) - 7:.1f}" class="lab" text-anchor="end">unchanged recipe, '
            'alignment 0.234</text>')
    names = ''
    # Opus 5 xhigh is labelled above its dot and max below and to the left, so the two labels do not meet.
    place = {('claude-opus-5', 'max'): (10, 22, 'end'), ('claude-opus-5', 'xhigh'): (0, -12, 'middle'),
             ('claude-opus-5', 'low'): (0, 22, 'middle')}
    for d in pts:
        k = (d['model'], d['effort'])
        if k in lab:
            dx, dy, anchor = place[k]
            names += (f'<text x="{x(d["aesthetic"]) + dx:.1f}" y="{y(d["alignment"]) + dy:.1f}" class="lab" '
                      f'text-anchor="{anchor}">{lab[k]}</text>')
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{DDPO_ARIA}">{grid}{refs}'
           f'{ddpo_marks(pts, x, y, 6)}{names}</svg>')

    # Narrow layout: fewer ticks, the two reference labels inside the plot, one named point.
    W, L, R, TOP, B = 380, 44, 14, 40, 52
    H = 360
    x = lambda v: L + (W - L - R) * (v - xlo) / (xhi - xlo)
    y = lambda v: TOP + (H - TOP - B) * (yhi - v) / (yhi - ylo)
    grid = ''.join(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{TOP}" y2="{H - B}" class="g"/>' for v in (4, 11, 18))
    grid += ''.join(f'<text x="{x(v):.1f}" y="{H - B + 20}" class="ax" text-anchor="{a}">{v}</text>'
                    for v, a in ((4, 'start'), (11, 'middle'), (18, 'end')))
    grid += ''.join(f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="g"/>'
                    f'<text x="{L - 6}" y="{y(v) + 5:.1f}" class="ax" text-anchor="end">{v:.1f}</text>'
                    for v in (0.10, 0.20))
    grid += (f'<text x="{L - 40}" y="{TOP - 18}" class="sub">CLIP alignment (prompt match)</text>'
             f'<text x="{W - R}" y="{H - 4}" class="sub" text-anchor="end">aesthetic score</text>')
    refs = (f'<line x1="{x(5.84):.1f}" x2="{x(5.84):.1f}" y1="{TOP}" y2="{H - B}" class="cap"/>'
            f'<text x="{x(5.84) + 6:.1f}" y="{y(0.088):.1f}" {HALO}class="lab">baseline 5.84</text>'
            f'<line x1="{L}" x2="{W - R}" y1="{y(0.234):.1f}" y2="{y(0.234):.1f}" class="cap"/>'
            f'<text x="{W - R}" y="{y(0.234) - 8:.1f}" {HALO}class="lab" text-anchor="end">unchanged recipe, '
            '0.234</text>')
    names = ''
    for d in pts:
        if (d['model'], d['effort']) == ('claude-opus-5', 'max'):
            names += (f'<text x="{W - R}" y="{y(d["alignment"]) + 26:.1f}" {HALO}class="lab" '
                      f'text-anchor="end">Opus 5 max</text>')
    narrow = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{DDPO_ARIA}">{grid}{refs}'
              f'{ddpo_marks(pts, x, y, 6)}{names}</svg>')

    title = 'Aesthetic score against prompt match, each DDPO image task cell'
    return figure(title, svg, 'How eight cells raised the rating while their pictures stopped matching their prompts. '
                  'One dot per model and effort level, at its reported checkpoint. CLIP alignment stands in for prompt '
                  'match, and the variety measure is left out. The red dots beat the '
                  "paper's 5.84 baseline with CLIP alignment below 0.19: Claude Opus 5 at all five effort levels, Kimi "
                  'K3 max, and GPT-5.6 Sol max and medium. Source: the alignment and diversity table on each of the 28 '
                  'DDPO case pages with a checkpoint.',
                  legend=[(dot(RED), 'beats the baseline with alignment below 0.19'), (dot(GRAY), 'other cells')],
                  narrow=narrow)


def oneline(tk):
    """The task's one-line description from the benchmark's task gallery, quoted and cited."""
    s = ONELINE[tk]
    return cite(f'“{s[0].lower() + s[1:]}”', X('Task gallery', f'{GALLERY}{tk}/'))


# Case-study headings: the task's name on its gallery page, linked there.
CASE_NAME = {RAGEN: 'RAGEN on Sokoban', DDPO: 'DDPO aesthetic alignment'}


def case_head(tk):
    return f'<a href="{GALLERY}{tk}/">{CASE_NAME[tk]}</a>'


def cases(cells, ddpo):
    top = max(ddpo, key=lambda d: d['aesthetic'])
    ragen = f'''
<p>The task is to {oneline(RAGEN)}: train Qwen2.5-3B, by reinforcement learning, to solve small 6×6 box-pushing puzzles. The score is how many of 512 test boards it solves. The boards are generated from one number, the seed 123, which {cite('the task treats as the one secret', X('declaration.py:49-50', GH + T + RAGEN + '/declaration.py#L49-L50'), X('harness/grade.py:879', GH + T + RAGEN + '/harness/grade.py#L879'))} that keeps the test boards hidden. But 123 is also the default seed in the RAGEN code that {cite('the task copies into the agent\'s workspace', X('environment/Dockerfile:95', GH + T + RAGEN + '/environment/Dockerfile#L95'))}, so running that code's own evaluation there plays the first 32 test boards.<sup><a href="#nd">d</a></sup> Most case pages leave its use unadjudicated.</p>
<p>The bigger effect came from copying. {cite('Claude Opus 5 medium', EC(RAGEN, 'Claude Opus 5 medium'))} had the container's built-in puzzle solver play a large set of boards and trained the model to repeat its moves. Its training set held at least 422 of the 512 test boards, and the copied model solved all 512 before any reinforcement learning, which then "showed no measurable benefit". Four more cells reached 512/512 this way, and GPT-5.6 Terra max 511.</p>
<p>These scores also put Claude Opus 5 third at maximum effort, behind GPT-5.6 Sol and Terra, which solved 512 and 511 boards there against its 120. Without this task it is first at maximum effort.</p>
{ragen_chart(cells)}'''
    ddpo_case = f'''
<p>The task is to {oneline(DDPO)}. The grader has a fixed rating model judge how good 256 generated pictures of animals look and averages the ratings; the shipped recipe gets about 5.5. The same rating model is available during training. The task also measures whether the pictures still match their prompts and still differ from one another, but {cite('by design counts neither', X('instruction.md:23', GH + T + DDPO + '/instruction.md#L23'), X('harness/final_eval.py:233', GH + T + DDPO + '/harness/final_eval.py#L233'))}, following the original DDPO benchmark.</p>
<p>{cite('Claude Opus 5 max', EC(DDPO, 'Claude Opus 5 max'))} replaced the shipped training method with one that feeds the rating model's own gradient straight back into the image model. Its pictures drifted away from their prompts and toward each other. Its case page says every checkpoint "triggered both alerts", with prompt match at 0.10–0.11 and variety at 0.04–0.05, against about 0.23 and 0.37 for the unchanged recipe. It scored {top['aesthetic']:.2f}, the best result on the task (σ 0.712).<sup><a href="#ne">e</a></sup></p>
<p>Seven other cells raised the rating while losing prompt match the same way, including the other four Claude Opus 5 runs and Kimi K3 max. Together the eight supply 94% of the task's σ above the baseline. We don't have the image-generation expertise to say where a fair limit would sit.</p>
{ddpo_chart(ddpo)}'''
    return [('case-ragen', case_head(RAGEN), ragen), ('case-ddpo', case_head(DDPO), ddpo_case)]


def main():
    cells = load_cells()
    print(write_page(
        'ai4ai-bench', 'AI4AI-Bench', 'Nov. 3, 2026',
        'Einsia / Navers Lab (Yizhe Chi, Wenyi Li, Deyao Hong et al.)',
        'arXiv 2608.20318 v1; repo <code>5ced1e2</code>; 10 tasks, 290 cells',
        lede='AI4AI-Bench tests whether a coding agent can improve the training recipe in a real research repository, '
             'measured by a 0-to-1 score (σ) where 0.1 is the repository\'s own recipe and 1 is a perfect result.'
             '<sup><a href="#na">a</a></sup> It has 10 tasks, from image generation to reward modelling, run by six AI '
             'systems at several reasoning-effort levels, 290 runs in all (the benchmark calls each run a cell).'
             '<sup><a href="#nb">b</a></sup>',
        found=['We reviewed all 10 tasks and found that <strong>4 (40%)</strong> had scoring errors - test data the agent '
               'can rebuild, a score that rewards the wrong thing, a perfect mark the code can\'t reach, or a baseline '
               'inside its own noise. A benchmark is rated Flawed when errors affect at least 20% of its score, and '
               'each task is an equal tenth of it.<sup><a href="#nc">c</a></sup>',
               'In the Sokoban puzzle task, the 512 secret test boards can be rebuilt from code in the agent\'s '
               'workspace, and five runs solve all 512. This one task is why Claude Opus 5 drops from first to third '
               'at maximum effort.',
               'In the image-generation task, eight runs push a fixed model\'s rating of their pictures up until the '
               'pictures no longer match their prompts, and they supply 94% of the task\'s gains.',
               'Every run reports the best of three saved checkpoints, picked on the test set. Reporting the last one '
               'instead flips 21 runs between beating and missing the repository\'s own recipe.',
               'With the corrections we can make, Claude Opus 5 stays first and Kimi K3 moves up to second.'],
        cases_intro='Two tasks show the main problems: test boards the agent can rebuild in its own workspace, and an image score that rewards pictures ignoring their prompts.',
        errors=ERRORS, cases=cases(cells, load_ddpo()),
        disclaimer="AI4AI-Bench's task code, evaluators and orchestrator are public, along with a case page for each "
                   'of the 290 cells; patch contents and raw agent logs are not, so cell-level findings rest on the '
                   "benchmark's own case pages.<sup><a href=\"#nb\">b</a></sup> We read all 10 tasks and all 290 case "
                   "pages and recomputed every score from the paper's anchors. Per-task calls were made by AI "
                   'reviewers, and every counted error was then checked by hand in the code.',
        notes=[('na', f'Paper: <a href="{PAPER}">arXiv 2608.20318</a> (v1, Aug. 20, 2026). Homepage: '
                      '<a href="https://lab.einsia.ai/ai4ai/">lab.einsia.ai/ai4ai</a>; one-line task descriptions from '
                      f'its <a href="{GALLERY}">task gallery</a>.'),
               ('nb', f'Repository: <a href="https://github.com/Einsia/AI4AI-Bench/tree/{SHA}">Einsia/AI4AI-Bench '
                      f'at <code>5ced1e2</code></a>. Case pages: <a href="{CASES}">lab.einsia.ai/ai4ai/trajectories'
                      '</a>, fetched Oct. 29, 2026. Per-task notes, per-cell reviews, the task log and the scripts '
                      'are in the audit folder linked at the top of this page.'),
               ('nc', 'Epoch\'s <a href="https://epoch.ai/data/benchmark-reviews-documentation/methodology">Rubric '
                      'v1</a> rates a benchmark Flawed when "errors affect ≥20% of the total score", or when "there is '
                      'an issue that corrupts grading at scale". For partial scores like σ, the 20% is a share of the '
                      'total possible score. σ is continuous, so counting tasks only stands in for score share: not '
                      'every cell in an affected task is wrong. Best-of-3 selection on the test set arguably meets the '
                      'second trigger; we do not count it.'),
               ('nd', f'Upstream RAGEN at <code>20daedc4</code>: <a href="{UPSTREAM}"><code>config/base.yaml</code> '
                      f'lines 8–10</a> and <a href="{RAGEN_GH}config/eval.yaml#L12-L14"><code>config/eval.yaml</code> '
                      'lines 12–14</a>. Each board group gets the seed plus its index, so the evaluation setting\'s 32 '
                      'groups are the first 32 of the final 512.'),
               ('ne', 'σ values on this page are recomputed from the checkpoint scores on the case pages with the '
                      "paper's Table 2 anchors. They reproduce the paper's means: 0.165 overall against its 0.166, "
                      'and Claude Opus 5 medium 0.287 against 0.288. Most of the small gap is the NPO unlearning task, '
                      "where the paper's table uses uncapped scores; with its values, our overall mean rounds to 0.166. "
                      'The paper reports Claude Opus 5 as the best system at 0.250; recomputed, it is 0.249, the value '
                      'used on this page.'),
               ('nf', 'The paper scores the 19 cells that produced no checkpoint as 0, and 16 of them are GPT-5.6 Terra '
                      'and Luna cells, 8 each. Leaving those cells out raises the overall mean from 0.165 to 0.177 and '
                      'moves GPT-5.6 Terra from fifth to fourth, ahead of Claude Sonnet 5.')]))


if __name__ == '__main__':
    main()
