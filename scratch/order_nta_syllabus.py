import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'neet_bot', 'data')

# Official NTA / NCERT Syllabus Chapter Order

NTA_PHYSICS_ORDER = [
    "Units and Measurements",
    "Motion in a Straight Line",
    "Motion in a Plane",
    "Laws of Motion",
    "Work, Energy, and Power",
    "System of Particles and Rotational Motion",
    "Gravitation",
    "Mechanical Properties of Solids and Fluids",
    "Thermal Properties and Thermodynamics",
    "Kinetic Theory of Gases",
    "Oscillations and Waves",
    "Electrostatics and Capacitance",
    "Current Electricity",
    "Moving Charges and Magnetism",
    "Electromagnetic Induction and AC",
    "Electromagnetic Waves",
    "Ray Optics and Wave Optics",
    "Dual Nature of Radiation and Matter",
    "Atoms and Nuclei",
    "Semiconductor Electronics"
]

NTA_CHEMISTRY_ORDER = [
    "Some Basic Concepts of Chemistry",
    "Structure of Atom",
    "Classification of Elements and Periodicity",
    "Chemical Bonding and Molecular Structure",
    "States of Matter and Thermodynamics",
    "Equilibrium",
    "Redox Reactions and Electrochemistry",
    "Chemical Kinetics",
    "Surface Chemistry and Extraction",
    "p-Block Elements",
    "d- and f-Block Elements",
    "Coordination Compounds",
    "Organic Chemistry: Basic Principles",
    "Hydrocarbons",
    "Haloalkanes and Haloarenes",
    "Alcohols, Phenols and Ethers",
    "Aldehydes, Ketones and Carboxylic Acids",
    "Amines",
    "Biomolecules",
    "Polymers and Everyday Chemistry"
]

NTA_BIOLOGY_ORDER = [
    "The Living World",
    "Biological Classification",
    "Plant Kingdom",
    "Animal Kingdom",
    "Morphology of Flowering Plants",
    "Anatomy of Flowering Plants",
    "Structural Organisation in Animals",
    "Cell: The Unit of Life",
    "Biomolecules",
    "Cell Cycle and Cell Division",
    "Transport in Plants",
    "Mineral Nutrition",
    "Photosynthesis in Higher Plants",
    "Respiration in Plants",
    "Plant Growth and Development",
    "Digestion and Absorption",
    "Breathing and Exchange of Gases",
    "Body Fluids and Circulation",
    "Excretory Products and Their Elimination",
    "Locomotion and Movement",
    "Neural Control and Coordination",
    "Chemical Coordination and Integration",
    "Reproduction in Organisms",
    "Sexual Reproduction in Flowering Plants",
    "Human Reproduction",
    "Reproductive Health",
    "Principles of Inheritance and Variation",
    "Molecular Basis of Inheritance",
    "Evolution",
    "Human Health and Disease",
    "Strategies for Enhancement in Food Production",
    "Microbes in Human Welfare",
    "Biotechnology: Principles and Processes",
    "Biotechnology and Its Applications",
    "Organisms and Populations",
    "Ecosystem",
    "Biodiversity and Conservation",
    "Environmental Issues"
]

def reorder_file(filename, nta_order):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_chapters = data.get('chapters', {})
    ordered_chapters = {}

    # First add chapters in NTA order
    for ch in nta_order:
        if ch in existing_chapters:
            ordered_chapters[ch] = existing_chapters[ch]

    # Then add any remaining chapters
    for ch, qs in existing_chapters.items():
        if ch not in ordered_chapters:
            ordered_chapters[ch] = qs

    data['chapters'] = ordered_chapters
    data['chapter_order'] = list(ordered_chapters.keys())

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Reordered {filename}: {len(ordered_chapters)} chapters saved in official NTA order.")

reorder_file('questions_dataset.json', NTA_BIOLOGY_ORDER)
reorder_file('physics_questions.json', NTA_PHYSICS_ORDER)
reorder_file('chemistry_questions.json', NTA_CHEMISTRY_ORDER)
