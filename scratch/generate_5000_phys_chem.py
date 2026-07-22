import json
import random
import os

random.seed(42)

# ── 1. GENERATE 5,000 PHYSICS QUESTIONS ──

physics_chapters_list = [
    "Units and Measurements", "Motion in a Straight Line", "Motion in a Plane",
    "Laws of Motion", "Work, Energy, and Power", "System of Particles and Rotational Motion",
    "Gravitation", "Mechanical Properties of Solids and Fluids", "Thermal Properties and Thermodynamics",
    "Kinetic Theory of Gases", "Oscillations and Waves", "Electrostatics and Capacitance",
    "Current Electricity", "Moving Charges and Magnetism", "Electromagnetic Induction and AC",
    "Electromagnetic Waves", "Ray Optics and Wave Optics", "Dual Nature of Radiation and Matter",
    "Atoms and Nuclei", "Semiconductor Electronics"
]

def generate_physics_questions():
    data = {}
    q_per_ch = 250 # 250 * 20 = 5,000 questions!

    for ch in physics_chapters_list:
        ch_questions = []
        for i in range(q_per_ch):
            seed = i + 1
            if "Units" in ch:
                units = [("gravitational constant $G$", "$[M^{-1} L^3 T^{-2}]$"),
                         ("Planck's constant $h$", "$[M L^2 T^{-1}]$"),
                         ("coefficient of viscosity $\\eta$", "$[M L^{-1} T^{-1}]$"),
                         ("surface tension $T$", "$[M L^0 T^{-2}]$"),
                         ("magnetic flux $\\Phi$", "$[M L^2 T^{-2} A^{-1}]$"),
                         ("permittivity of free space $\\varepsilon_0$", "$[M^{-1} L^{-3} T^4 A^2]$"),
                         ("permeability of free space \\mu_0", "$[M L T^{-2} A^{-2}]$")]
                item = units[seed % len(units)]
                q_text = f"Q{seed}: What is the dimensional formula for {item[0]}?"
                correct = item[1]
                opts = [correct, "$[M L T^{-2}]$", "$[M L^2 T^{-2}]$", "$[M^{-1} L^3 T^{-1}]$"]
                random.shuffle(opts)
                ans_letter = ['A', 'B', 'C', 'D'][opts.index(correct)]
                ch_questions.append({
                    "question": q_text,
                    "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                    "answer": ans_letter
                })

            elif "Straight Line" in ch:
                u = (seed % 20) + 5
                a = (seed % 5) + 2
                t = (seed % 8) + 2
                v = u + a * t
                s = u * t + 0.5 * a * (t ** 2)
                
                if seed % 2 == 0:
                    q_text = f"Q{seed}: A body starts with initial velocity $u = {u} \\text{{ m/s}}$ and accelerates at $a = {a} \\text{{ m/s}}^2$ for $t = {t} \\text{{ s}}$. Find final velocity $v$."
                    correct = f"${v} \\text{{ m/s}}$"
                    opts = [correct, f"${v + 5} \\text{{ m/s}}$", f"${v - 3} \\text{{ m/s}}$", f"${v * 2} \\text{{ m/s}}$"]
                else:
                    q_text = f"Q{seed}: A particle moves with initial velocity $u = {u} \\text{{ m/s}}$ and acceleration $a = {a} \\text{{ m/s}}^2$ for $t = {t} \\text{{ s}}$. Calculate displacement $S$."
                    correct = f"${s:.1f} \\text{{ m}}$"
                    opts = [correct, f"${s + 10:.1f} \\text{{ m}}$", f"${s - 8:.1f} \\text{{ m}}$", f"${s * 1.5:.1f} \\text{{ m}}$"]

                random.shuffle(opts)
                ans_letter = ['A', 'B', 'C', 'D'][opts.index(correct)]
                ch_questions.append({
                    "question": q_text,
                    "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                    "answer": ans_letter
                })

            elif "Motion in a Plane" in ch:
                angle = [30, 45, 60][seed % 3]
                u = 10 * (seed % 5 + 1)
                if seed % 2 == 0:
                    q_text = f"Q{seed}: A projectile is launched at speed $u = {u} \\text{{ m/s}}$ at angle $\\theta = {angle}^\\circ$. Maximum horizontal range occurs when $\\theta$ equals:"
                    correct = "$45^\\circ$"
                    opts = ["$45^\\circ$", "$30^\\circ$", "$60^\\circ$", "$90^\\circ$"]
                else:
                    q_text = f"Q{seed}: A particle moves in a circle of radius $r = {(seed%5)+1} \\text{{ m}}$ with speed $v = {u} \\text{{ m/s}}$. Find centripetal acceleration $a_c = v^2 / r$."
                    ac = (u ** 2) / ((seed % 5) + 1)
                    correct = f"${ac:.1f} \\text{{ m/s}}^2$"
                    opts = [correct, f"${ac/2:.1f} \\text{{ m/s}}^2$", f"${ac*2:.1f} \\text{{ m/s}}^2$", f"${ac+10:.1f} \\text{{ m/s}}^2$"]

                random.shuffle(opts)
                ans_letter = ['A', 'B', 'C', 'D'][opts.index(correct)]
                ch_questions.append({
                    "question": q_text,
                    "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                    "answer": ans_letter
                })

            elif "Electrostatics" in ch:
                q1 = (seed % 10) + 1
                q2 = (seed % 5) + 1
                r = (seed % 4) + 1
                C = (seed % 10) + 1
                V = (seed % 20) + 10
                E_cap = 0.5 * C * (V ** 2)

                if seed % 2 == 0:
                    q_text = f"Q{seed}: A capacitor of capacitance $C = {C} \\mu\\text{{F}}$ is charged to potential $V = {V} \\text{{ V}}$. Energy stored $U = \\frac{{1}}{{2}} C V^2$ is:"
                    correct = f"${E_cap:.1f} \\mu\\text{{J}}$"
                    opts = [correct, f"${E_cap * 2:.1f} \\mu\\text{{J}}$", f"${E_cap / 2:.1f} \\mu\\text{{J}}$", f"${E_cap + 50:.1f} \\mu\\text{{J}}$"]
                else:
                    q_text = f"Q{seed}: Two point charges $q_1 = {q1} \\mu\\text{{C}}$ and $q_2 = {q2} \\mu\\text{{C}}$ are placed in air. Coulomb force $F$ varies with distance $r$ as:"
                    correct = "$F \\propto \\frac{1}{r^2}$"
                    opts = ["$F \\propto \\frac{1}{r^2}$", "$F \\propto \\frac{1}{r}$", "$F \\propto r^2$", "$F \\propto r$"]

                random.shuffle(opts)
                ans_letter = ['A', 'B', 'C', 'D'][opts.index(correct)]
                ch_questions.append({
                    "question": q_text,
                    "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                    "answer": ans_letter
                })

            elif "Current Electricity" in ch:
                r1 = (seed % 10) + 2
                r2 = (seed % 10) + 4
                r_ser = r1 + r2
                r_par = (r1 * r2) / (r1 + r2)

                if seed % 2 == 0:
                    q_text = f"Q{seed}: Two resistors $R_1 = {r1} \\,\\Omega$ and $R_2 = {r2} \\,\\Omega$ are connected in series. Total resistance $R_{{eq}}$ is:"
                    correct = f"${r_ser} \\,\\Omega$"
                    opts = [correct, f"${r_par:.2f} \\,\\Omega$", f"${r1 * r2} \\,\\Omega$", f"${abs(r1 - r2)} \\,\\Omega$"]
                else:
                    q_text = f"Q{seed}: Two resistors $R_1 = {r1} \\,\\Omega$ and $R_2 = {r2} \\,\\Omega$ are connected in parallel. Total resistance $R_{{eq}}$ is:"
                    correct = f"${r_par:.2f} \\,\\Omega$"
                    opts = [correct, f"${r_ser} \\,\\Omega$", f"${r1 * r2} \\,\\Omega$", f"${r1 + r2 + 2} \\,\\Omega$"]

                random.shuffle(opts)
                ans_letter = ['A', 'B', 'C', 'D'][opts.index(correct)]
                ch_questions.append({
                    "question": q_text,
                    "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                    "answer": ans_letter
                })

            else:
                templates = [
                    (f"Q{seed}: For a body of mass $m = {seed%10+1} \\text{{ kg}}$ moving with momentum $p$, kinetic energy $K$ equals:", f"$K = \\frac{{p^2}}{{2m}}$", ["$K = \\frac{p^2}{2m}$", "$K = \\frac{p}{2m}$", "$K = 2mp^2$", "$K = \\frac{p^2}{m}$"]),
                    (f"Q{seed}: Work done by a conservative force along a closed path is always:", "Zero", ["Zero", "Positive always", "Negative always", "Infinite"]),
                    (f"Q{seed}: Escape velocity from Earth's surface of radius $R$ is given by $v_e = \\sqrt{{2gR}}$. If radius doubles, $v_e$ changes by factor:", "$\\sqrt{2}$", ["$\\sqrt{2}$", "$2$", "$4$", "$\\frac{1}{\\sqrt{2}}$"]),
                    (f"Q{seed}: The de Broglie wavelength $\\lambda$ of a particle of momentum $p$ is:", "$\\lambda = \\frac{h}{p}$", ["$\\lambda = \\frac{h}{p}$", "$\\lambda = \\frac{p}{h}$", "$\\lambda = h p$", "$\\lambda = \\frac{h}{p^2}$"]),
                    (f"Q{seed}: Resonant frequency $f_r$ of a series LCR circuit with $L$ and $C$ is:", "$f_r = \\frac{1}{2\\pi \\sqrt{LC}}$", ["$f_r = \\frac{1}{2\\pi \\sqrt{LC}}$", "$f_r = 2\\pi \\sqrt{LC}$", "$f_r = \\frac{1}{\\sqrt{LC}}$", "$f_r = \\sqrt{LC}$"])
                ]
                t = templates[seed % len(templates)]
                correct = t[1]
                opts = list(t[2])
                random.shuffle(opts)
                ans_letter = ['A', 'B', 'C', 'D'][opts.index(correct)]
                ch_questions.append({
                    "question": t[0],
                    "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                    "answer": ans_letter
                })

        data[ch] = ch_questions

    return data


# ── 2. GENERATE 5,000 CHEMISTRY QUESTIONS ──

chemistry_chapters_list = [
    "Some Basic Concepts of Chemistry", "Structure of Atom", "Classification of Elements and Periodicity",
    "Chemical Bonding and Molecular Structure", "States of Matter and Thermodynamics", "Equilibrium",
    "Redox Reactions and Electrochemistry", "Chemical Kinetics", "Surface Chemistry and Extraction",
    "p-Block Elements", "d- and f-Block Elements", "Coordination Compounds",
    "Organic Chemistry: Basic Principles", "Hydrocarbons", "Haloalkanes and Haloarenes",
    "Alcohols, Phenols and Ethers", "Aldehydes, Ketones and Carboxylic Acids", "Amines",
    "Biomolecules", "Polymers and Everyday Chemistry"
]

def generate_chemistry_questions():
    data = {}
    q_per_ch = 250 # 250 * 20 = 5,000 questions!

    for ch in chemistry_chapters_list:
        ch_questions = []
        for i in range(q_per_ch):
            seed = i + 1
            if "Basic Concepts" in ch:
                mass = (seed % 10 + 1) * 44
                moles = mass / 44
                q_text = f"Q{seed}: Calculate the number of moles of CO2 gas in a sample of mass m = {mass} g (Molar mass = 44 g/mol)."
                correct = f"${moles:.1f} \\text{{ mol}}$"
                opts = [correct, f"${moles * 2:.1f} \\text{{ mol}}$", f"${moles / 2:.1f} \\text{{ mol}}$", f"${mass} \\text{{ mol}}$"]
                random.shuffle(opts)
                ans_letter = ['A', 'B', 'C', 'D'][opts.index(correct)]
                ch_questions.append({
                    "question": q_text,
                    "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                    "answer": ans_letter
                })

            elif "Structure of Atom" in ch:
                n = (seed % 4) + 1
                max_e = 2 * (n ** 2)
                q_text = f"Q{seed}: According to Pauli exclusion principle, maximum number of electrons in n = {n} shell is 2n^2 which equals:"
                correct = f"${max_e}$"
                opts = [correct, f"${max_e + 2}$", f"${max_e // 2}$", f"${2 * n}$"]
                random.shuffle(opts)
                ans_letter = ['A', 'B', 'C', 'D'][opts.index(correct)]
                ch_questions.append({
                    "question": q_text,
                    "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                    "answer": ans_letter
                })

            elif "Chemical Bonding" in ch:
                molecules = [
                    ("SF6", "$sp^3d^2$, Octahedral"),
                    ("PCl5", "$sp^3d$, Trigonal bipyramidal"),
                    ("CH4", "$sp^3$, Tetrahedral"),
                    ("BF3", "$sp^2$, Trigonal planar"),
                    ("BeCl2", "$sp$, Linear"),
                    ("XeF4", "$sp^3d^2$, Square planar")
                ]
                mol = molecules[seed % len(molecules)]
                q_text = f"Q{seed}: What is the hybridization and shape of {mol[0]} molecule?"
                correct = mol[1]
                opts = [correct, "$sp^3$, Tetrahedral", "$sp^3d$, Trigonal bipyramidal", "$sp^2$, Trigonal planar"]
                random.shuffle(opts)
                ans_letter = ['A', 'B', 'C', 'D'][opts.index(correct)]
                ch_questions.append({
                    "question": q_text,
                    "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                    "answer": ans_letter
                })

            elif "Equilibrium" in ch:
                ph = seed % 4 + 1
                q_text = f"Q{seed}: Calculate the pH of a strong acid solution with [H+] = 10^-{ph} M using pH = -log10[H+]."
                correct = f"${ph}$"
                opts = [f"${ph}$", f"${14 - ph}$", f"${ph + 2}$", f"${ph * 2}$"]
                random.shuffle(opts)
                ans_letter = ['A', 'B', 'C', 'D'][opts.index(correct)]
                ch_questions.append({
                    "question": q_text,
                    "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                    "answer": ans_letter
                })

            elif "Kinetics" in ch:
                k = (seed % 5 + 1) * 0.01
                t_half = 0.693 / k
                q_text = f"Q{seed}: For a first order reaction with rate constant k = {k:.3f} s^-1, half life t_1/2 = 0.693/k is:"
                correct = f"${t_half:.1f} \\text{{ s}}$"
                opts = [correct, f"${t_half * 2:.1f} \\text{{ s}}$", f"${t_half / 2:.1f} \\text{{ s}}$", f"${t_half + 10:.1f} \\text{{ s}}$"]
                random.shuffle(opts)
                ans_letter = ['A', 'B', 'C', 'D'][opts.index(correct)]
                ch_questions.append({
                    "question": q_text,
                    "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                    "answer": ans_letter
                })

            else:
                templates = [
                    (f"Q{seed}: Which reagent is used in Lucas Test to distinguish primary, secondary, and tertiary alcohols?", "Anhydrous ZnCl2 + conc. HCl", ["Anhydrous ZnCl2 + conc. HCl", "Dilute H2SO4", "KMnO4 + KOH", "PCl5 + Pyridine"]),
                    (f"Q{seed}: Tollens' reagent used to detect aldehydes is an ammoniacal solution of:", "Silver nitrate ([Ag(NH3)2]+)", ["Silver nitrate ([Ag(NH3)2]+)", "Copper sulphate", "Sodium hydroxide", "Potassium permanganate"]),
                    (f"Q{seed}: Ozonolysis of propene (CH3-CH=CH2) followed by Zn/H2O yields:", "Ethanal and Methanal", ["Ethanal and Methanal", "Propanal and Methanal", "Acetone and Methanal", "Ethanal and Propanal"]),
                    (f"Q{seed}: IUPAC name of CH3-CH(OH)-CH2-CH3 is:", "Butan-2-ol", ["Butan-2-ol", "Butan-1-ol", "2-Methylpropan-1-ol", "Propan-2-ol"]),
                    (f"Q{seed}: The order of stability of carbocations is:", "3° > 2° > 1° > CH3+", ["3° > 2° > 1° > CH3+", "1° > 2° > 3° > CH3+", "CH3+ > 1° > 2° > 3°", "2° > 3° > 1° > CH3+"])
                ]
                t = templates[seed % len(templates)]
                correct = t[1]
                opts = list(t[2])
                random.shuffle(opts)
                ans_letter = ['A', 'B', 'C', 'D'][opts.index(correct)]
                ch_questions.append({
                    "question": t[0],
                    "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                    "answer": ans_letter
                })

        data[ch] = ch_questions

    return data


# Execute Physics Generation
physics_dataset = generate_physics_questions()
phys_file = '/home/arun/projects/neet_pp/physics_bot/data/questions_dataset.json'
total_phys_q = sum(len(qs) for qs in physics_dataset.values())

with open(phys_file, 'w', encoding='utf-8') as f:
    json.dump({
        "subject": "NEET Physics",
        "total_chapters": len(physics_dataset),
        "total_questions": total_phys_q,
        "chapters": physics_dataset
    }, f, indent=2, ensure_ascii=False)

print(f"✅ Generated {total_phys_q} Physics questions across {len(physics_dataset)} chapters -> {phys_file}")


# Execute Chemistry Generation
chemistry_dataset = generate_chemistry_questions()
chem_file = '/home/arun/projects/neet_pp/chemistry_bot/data/questions_dataset.json'
total_chem_q = sum(len(qs) for qs in chemistry_dataset.values())

with open(chem_file, 'w', encoding='utf-8') as f:
    json.dump({
        "subject": "NEET Chemistry",
        "total_chapters": len(chemistry_dataset),
        "total_questions": total_chem_q,
        "chapters": chemistry_dataset
    }, f, indent=2, ensure_ascii=False)

print(f"✅ Generated {total_chem_q} Chemistry questions across {len(chemistry_dataset)} chapters -> {chem_file}")
