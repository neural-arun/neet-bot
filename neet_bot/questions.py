import json
import random
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

PATHS = {
    'biology': os.path.join(DATA_DIR, 'questions_dataset.json'),
    'physics': os.path.join(DATA_DIR, 'physics_questions.json'),
    'chemistry': os.path.join(DATA_DIR, 'chemistry_questions.json')
}

_banks = {}

def load_bank(subject='biology'):
    subj = (subject or 'biology').lower()
    if subj not in PATHS:
        subj = 'biology'
        
    if subj in _banks:
        return _banks[subj]
        
    path = PATHS[subj]
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset file missing for subject {subj}: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        _banks[subj] = json.load(f)
    return _banks[subj]

def get_chapter_list(subject='biology'):
    bank = load_bank(subject)
    if 'chapter_order' in bank:
        return list(bank['chapter_order'])
    return list(bank['chapters'].keys())

def get_total_count(subject='biology'):
    bank = load_bank(subject)
    return bank.get('total_questions', len(bank.get('chapters', {})))

def get_random_questions(chapter, count, subject='biology'):
    bank = load_bank(subject)
    pool = bank['chapters'].get(chapter, [])
    if not pool:
        return []
    count = min(count, len(pool))
    sampled = random.sample(pool, count)
    res = []
    for q in sampled:
        q_copy = dict(q)
        q_copy['chapter'] = chapter
        q_copy['subject'] = subject
        res.append(q_copy)
    random.shuffle(res)
    return res

def get_random_questions_multi(chapters, count, subject='biology'):
    bank = load_bank(subject)
    if not chapters:
        return []

    shuffled_ch = list(chapters)
    random.shuffle(shuffled_ch)

    sampled_qs = []
    per_ch_count = max(1, count // len(shuffled_ch))

    for ch in shuffled_ch:
        pool = bank['chapters'].get(ch, [])
        if not pool:
            continue
        take = min(per_ch_count, len(pool))
        ch_sample = random.sample(pool, take)
        for q in ch_sample:
            q_copy = dict(q)
            q_copy['chapter'] = ch
            q_copy['subject'] = subject
            sampled_qs.append(q_copy)

    if len(sampled_qs) < count:
        remaining_pool = []
        for ch in shuffled_ch:
            for q in bank['chapters'].get(ch, []):
                q_copy = dict(q)
                q_copy['chapter'] = ch
                q_copy['subject'] = subject
                if q_copy not in sampled_qs:
                    remaining_pool.append(q_copy)
        if remaining_pool:
            extra_take = min(count - len(sampled_qs), len(remaining_pool))
            sampled_qs.extend(random.sample(remaining_pool, extra_take))

    random.shuffle(sampled_qs)
    return sampled_qs[:count]
