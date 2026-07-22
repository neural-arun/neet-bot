import json
import random
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'questions_dataset.json')

_bank = None

def load_bank():
    global _bank
    if _bank is not None:
        return _bank
    with open(DATA_PATH) as f:
        _bank = json.load(f)
    return _bank

def get_chapter_list():
    bank = load_bank()
    return sorted(bank['chapters'].keys())

def get_total_count():
    bank = load_bank()
    return bank['total_questions']

def get_random_questions(chapter, count):
    bank = load_bank()
    pool = bank['chapters'].get(chapter, [])
    if not pool:
        return []
    count = min(count, len(pool))
    sampled = random.sample(pool, count)
    res = []
    for q in sampled:
        q_copy = dict(q)
        q_copy['chapter'] = chapter
        res.append(q_copy)
    return res

def get_random_questions_multi(chapters, count):
    bank = load_bank()
    pool = []
    for ch in chapters:
        for q in bank['chapters'].get(ch, []):
            q_copy = dict(q)
            q_copy['chapter'] = ch
            pool.append(q_copy)
    if not pool:
        return []
    count = min(count, len(pool))
    return random.sample(pool, count)

