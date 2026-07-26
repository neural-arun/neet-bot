import json
import os
import re

NTA_CHEMISTRY = [
    "Some Basic Concepts of Chemistry", "Structure of Atom", "Classification of Elements and Periodicity",
    "Chemical Bonding and Molecular Structure", "States of Matter and Thermodynamics", "Equilibrium",
    "Redox Reactions and Electrochemistry", "Chemical Kinetics", "p-Block Elements", "d- and f-Block Elements",
    "Coordination Compounds", "Organic Chemistry: Basic Principles", "Hydrocarbons",
    "Haloalkanes and Haloarenes", "Alcohols, Phenols and Ethers", "Aldehydes, Ketones and Carboxylic Acids",
    "Amines", "Biomolecules"
]

NTA_PHYSICS = [
    "Units and Measurements", "Motion in a Straight Line", "Motion in a Plane", "Laws of Motion",
    "Work, Energy and Power", "System of Particles and Rotational Motion", "Gravitation",
    "Mechanical Properties of Solids and Fluids", "Thermal Properties and Thermodynamics",
    "Kinetic Theory of Gases", "Oscillations and Waves", "Electrostatics and Capacitance",
    "Current Electricity", "Moving Charges and Magnetism", "Electromagnetic Induction and AC",
    "Electromagnetic Waves", "Ray Optics and Wave Optics", "Dual Nature of Radiation and Matter",
    "Atoms and Nuclei", "Semiconductor Electronics"
]

NTA_BIOLOGY = [
    "The Living World", "Biological Classification", "Plant Kingdom", "Animal Kingdom",
    "Morphology of Flowering Plants", "Anatomy of Flowering Plants", "Structural Organisation in Animals",
    "Cell: The Unit of Life", "Biomolecules", "Cell Cycle and Cell Division",
    "Photosynthesis in Higher Plants", "Respiration in Plants", "Plant Growth and Development",
    "Breathing and Exchange of Gases", "Body Fluids and Circulation", "Excretory Products and Their Elimination",
    "Locomotion and Movement", "Neural Control and Coordination", "Chemical Coordination and Integration",
    "Sexual Reproduction in Flowering Plants", "Human Reproduction", "Reproductive Health",
    "Principles of Inheritance and Variation", "Molecular Basis of Inheritance", "Evolution",
    "Human Health and Disease", "Microbes in Human Welfare", "Biotechnology: Principles and Processes",
    "Biotechnology and Its Applications", "Organisms and Populations", "Ecosystem", "Biodiversity and Conservation"
]

def map_to_nta(raw_ch, nta_list):
    raw = raw_ch.lower().strip()
    for official in nta_list:
        off_low = official.lower()
        # Direct string matching or substring overlap
        if raw in off_low or off_low in raw:
            return official
        # Keyword matching
        words = [w for w in raw.split() if len(w) > 3]
        if any(w in off_low for w in words):
            return official
    return nta_list[0]

def normalize_subject_file(subject_name, dataset_path, nta_list, dataset2_dir):
    if not os.path.exists(dataset_path):
        return
        
    ds = json.load(open(dataset_path))
    raw_chapters = ds.get('chapters', {})
    
    mapped_chapters = {ch: [] for ch in nta_list}
    
    for raw_ch, q_list in raw_chapters.items():
        official_ch = map_to_nta(raw_ch, nta_list)
        for q in q_list:
            q['chapter'] = official_ch
            mapped_chapters[official_ch].append(q)
            
    # Clean duplicates & ensure positive question counts
    final_chapters = {}
    total_q = 0
    for ch_n in nta_list:
        qs = mapped_chapters[ch_n]
        seen = set()
        unique_qs = []
        for q in qs:
            norm = re.sub(r'\W+', '', q['question'].lower())[:60]
            if norm not in seen:
                seen.add(norm)
                unique_qs.append(q)
        final_chapters[ch_n] = unique_qs
        total_q += len(unique_qs)
        
        # Write dataset2 chapter file
        slug = ch_n.lower().replace(':', '').replace('-', ' ').replace(',', '').strip().replace(' ', '_')
        slug = re.sub(r'[\:\—\-\,\&\(\)]+', ' ', ch_n).strip().lower()
        slug = re.sub(r'\s+', '_', slug)
        
        payload = {
            "subject": subject_name,
            "chapter": ch_n,
            "total_questions": len(unique_qs),
            "questions": unique_qs
        }
        with open(os.path.join(dataset2_dir, f"{slug}.json"), 'w') as f:
            json.dump(payload, f, indent=2)

    ds['chapters'] = final_chapters
    ds['total_chapters'] = len(final_chapters)
    ds['total_questions'] = total_q
    
    with open(dataset_path, 'w') as f:
        json.dump(ds, f, indent=2)
        
    print(f"Mapped {subject_name} into {len(final_chapters)} Official NTA Chapters ({total_q} pristine PYQs).")
    return ds

def main():
    print("Normalizing Chapters to Official NTA NEET Syllabus...\n")
    
    chem_ds = normalize_subject_file('Chemistry', 'dataset/chemistry/chemistry_pyqs_dataset.json', NTA_CHEMISTRY, 'dataset2/chemistry')
    phys_ds = normalize_subject_file('Physics', 'dataset/physics/physics_pyqs_dataset.json', NTA_PHYSICS, 'dataset2/physics')
    bio_ds = normalize_subject_file('Biology', 'dataset/biology/biology_pyqs_dataset.json', NTA_BIOLOGY, 'dataset2/biology')

    print("\nSynchronizing normalized datasets to all Telegram Bot directories...")
    with open('chemistry_bot/data/questions_dataset.json', 'w') as f:
        json.dump(chem_ds, f, indent=2)
    with open('physics_bot/data/questions_dataset.json', 'w') as f:
        json.dump(phys_ds, f, indent=2)
    with open('neet_bot/data/chemistry_questions.json', 'w') as f:
        json.dump(chem_ds, f, indent=2)
    with open('neet_bot/data/physics_questions.json', 'w') as f:
        json.dump(phys_ds, f, indent=2)
    with open('neet_bot/data/questions_dataset.json', 'w') as f:
        json.dump(bio_ds, f, indent=2)

    print("\nChapter Normalization Complete!")

if __name__ == '__main__':
    main()
