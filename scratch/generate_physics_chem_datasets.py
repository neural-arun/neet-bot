import json
import os

# ── 1. NEET PHYSICS SYLLABUS & QUESTIONS DATASET ──
physics_chapters = {
    "Units and Measurements": [
        {
            "question": "The dimensional formula for gravitational constant $G$ is:",
            "options": {
                "A": "$[M^{-1} L^3 T^{-2}]$",
                "B": "$[M^1 L^3 T^{-2}]$",
                "C": "$[M^{-1} L^2 T^{-2}]$",
                "D": "$[M^{-2} L^3 T^{-1}]$"
            },
            "answer": "A"
        },
        {
            "question": "If momentum $P$, area $A$, and time $T$ are taken as fundamental quantities, then energy has dimensions:",
            "options": {
                "A": "$[P^1 A^{1/2} T^{-1}]$",
                "B": "$[P^2 A^{1/2} T^{-1}]$",
                "C": "$[P^1 A^{1/2} T^{1}]$",
                "D": "$[P^1 A^{-1/2} T^{-1}]$"
            },
            "answer": "A"
        },
        {
            "question": "A screw gauge has a pitch of $1 \\text{ mm}$ and $100$ divisions on its circular scale. The least count is:",
            "options": {
                "A": "$0.01 \\text{ mm}$",
                "B": "$0.001 \\text{ mm}$",
                "C": "$0.1 \\text{ mm}$",
                "D": "$1.0 \\text{ mm}$"
            },
            "answer": "A"
        }
    ],
    "Motion in a Straight Line": [
        {
            "question": "A body starts from rest with uniform acceleration $a$. The displacement in the $n$-th second is given by:",
            "options": {
                "A": "$S_n = \\frac{a}{2}(2n - 1)$",
                "B": "$S_n = a(2n - 1)$",
                "C": "$S_n = \\frac{a}{2}(n^2 - 1)$",
                "D": "$S_n = \\frac{a}{2}(2n + 1)$"
            },
            "answer": "A"
        },
        {
            "question": "A ball is thrown vertically upwards with velocity $u$. The maximum height reached is:",
            "options": {
                "A": "$H = \\frac{u^2}{2g}$",
                "B": "$H = \\frac{u^2}{g}$",
                "C": "$H = \\frac{2u^2}{g}$",
                "D": "$H = \\frac{u}{2g}$"
            },
            "answer": "A"
        }
    ],
    "Motion in a Plane": [
        {
            "question": "For a projectile thrown at angle $\\theta$ with speed $u$, the horizontal range $R$ is maximum when $\\theta$ equals:",
            "options": {
                "A": "$45^\\circ$",
                "B": "$30^\\circ$",
                "C": "$60^\\circ$",
                "D": "$90^\\circ$"
            },
            "answer": "A"
        },
        {
            "question": "Centripetal acceleration of a particle moving in a circle of radius $r$ with constant speed $v$ is:",
            "options": {
                "A": "$a_c = \\frac{v^2}{r}$",
                "B": "$a_c = vr^2$",
                "C": "$a_c = \\frac{v}{r^2}$",
                "D": "$a_c = v^2 r$"
            },
            "answer": "A"
        }
    ],
    "Laws of Motion": [
        {
            "question": "An elevator of mass $M$ accelerates upwards with acceleration $a$. The tension $T$ in the supporting cable is:",
            "options": {
                "A": "$T = M(g + a)$",
                "B": "$T = M(g - a)$",
                "C": "$T = Mg$",
                "D": "$T = Ma$"
            },
            "answer": "A"
        },
        {
            "question": "The angle of friction $\\theta$ is related to the coefficient of static friction $\\mu_s$ by:",
            "options": {
                "A": "$\\tan \\theta = \\mu_s$",
                "B": "$\\sin \\theta = \\mu_s$",
                "C": "$\\cos \\theta = \\mu_s$",
                "D": "$\\cot \\theta = \\mu_s$"
            },
            "answer": "A"
        }
    ],
    "Work, Energy, and Power": [
        {
            "question": "Work done by a conservative force along a closed path is:",
            "options": {
                "A": "Zero",
                "B": "Positive always",
                "C": "Negative always",
                "D": "Depends on speed"
            },
            "answer": "A"
        },
        {
            "question": "A particle of mass $m$ has linear momentum $p$. Its kinetic energy is given by:",
            "options": {
                "A": "$K = \\frac{p^2}{2m}$",
                "B": "$K = \\frac{p}{2m}$",
                "C": "$K = 2mp^2$",
                "D": "$K = \\frac{p^2}{m}$"
            },
            "answer": "A"
        }
    ],
    "System of Particles and Rotational Motion": [
        {
            "question": "The moment of inertia of a uniform solid sphere of mass $M$ and radius $R$ about its diameter is:",
            "options": {
                "A": "$\\frac{2}{5} MR^2$",
                "B": "$\\frac{2}{3} MR^2$",
                "C": "$\\frac{1}{2} MR^2$",
                "D": "$\\frac{7}{5} MR^2$"
            },
            "answer": "A"
        },
        {
            "question": "The relation between torque $\\tau$ and angular momentum $L$ is:",
            "options": {
                "A": "$\\tau = \\frac{dL}{dt}$",
                "B": "$\\tau = L \\cdot t$",
                "C": "$\\tau = \\frac{d^2 L}{dt^2}$",
                "D": "$L = \\frac{d\\tau}{dt}$"
            },
            "answer": "A"
        }
    ],
    "Gravitation": [
        {
            "question": "The escape velocity $v_e$ from the surface of Earth of radius $R$ and mass $M$ is given by:",
            "options": {
                "A": "$v_e = \\sqrt{\\frac{2GM}{R}}$",
                "B": "$v_e = \\sqrt{\\frac{GM}{R}}$",
                "C": "$v_e = \\sqrt{2gR}$",
                "D": "Both A and C"
            },
            "answer": "D"
        },
        {
            "question": "Kepler's third law of planetary motion states that $T^2$ is proportional to:",
            "options": {
                "A": "$r^3$",
                "B": "$r^2$",
                "C": "$r^{1/2}$",
                "D": "$r^{-3}$"
            },
            "answer": "A"
        }
    ],
    "Current Electricity": [
        {
            "question": "Drift velocity $v_d$ of electrons in a conductor is related to electric field $E$ and mobility $\\mu$ by:",
            "options": {
                "A": "$v_d = \\mu E$",
                "B": "$v_d = \\frac{E}{\\mu}$",
                "C": "$v_d = \\mu E^2$",
                "D": "$v_d = \\frac{\\mu}{E}$"
            },
            "answer": "A"
        },
        {
            "question": "In a Wheatstone bridge, the balance condition for four resistances $P, Q, R, S$ is:",
            "options": {
                "A": "$\\frac{P}{Q} = \\frac{R}{S}$",
                "B": "$P \\cdot Q = R \\cdot S$",
                "C": "$\\frac{P}{R} = \\frac{S}{Q}$",
                "D": "$P + Q = R + S$"
            },
            "answer": "A"
        }
    ],
    "Dual Nature of Radiation and Matter": [
        {
            "question": "The de Broglie wavelength $\\lambda$ associated with a particle of momentum $p$ is:",
            "options": {
                "A": "$\\lambda = \\frac{h}{p}$",
                "B": "$\\lambda = \\frac{p}{h}$",
                "C": "$\\lambda = h \\cdot p$",
                "D": "$\\lambda = \\frac{h}{p^2}$"
            },
            "answer": "A"
        },
        {
            "question": "Einstein's photoelectric equation is given by:",
            "options": {
                "A": "$K_{max} = h\\nu - \\phi_0$",
                "B": "$K_{max} = h\\nu + \\phi_0$",
                "C": "$\\phi_0 = h\\nu + K_{max}$",
                "D": "$K_{max} = \\frac{h}{\\nu} - \\phi_0$"
            },
            "answer": "A"
        }
    ],
    "Semiconductor Electronics": [
        {
            "question": "In an n-type semiconductor, the majority charge carriers are:",
            "options": {
                "A": "Electrons",
                "B": "Holes",
                "C": "Positive ions",
                "D": "Neutrons"
            },
            "answer": "A"
        },
        {
            "question": "The depletion layer of a p-n junction diode consists of:",
            "options": {
                "A": "Immobile ions only",
                "B": "Free electrons only",
                "C": "Holes only",
                "D": "Both free electrons and holes"
            },
            "answer": "A"
        }
    ]
}

# ── 2. NEET CHEMISTRY SYLLABUS & QUESTIONS DATASET ──
chemistry_chapters = {
    "Some Basic Concepts of Chemistry": [
        {
            "question": "The number of moles in $44 \\text{ g}$ of $\\text{CO}_2$ gas at STP is:",
            "options": {
                "A": "$1 \\text{ mol}$",
                "B": "$2 \\text{ mol}$",
                "C": "$0.5 \\text{ mol}$",
                "D": "$44 \\text{ mol}$"
            },
            "answer": "A"
        },
        {
            "question": "Molarity $M$ of a solution is defined as number of moles of solute per:",
            "options": {
                "A": "Litre of solution",
                "B": "Kilogram of solvent",
                "C": "Litre of solvent",
                "D": "Kilogram of solution"
            },
            "answer": "A"
        }
    ],
    "Structure of Atom": [
        {
            "question": "The maximum number of electrons in a subshell with azimuthal quantum number $l = 2$ (d-subshell) is:",
            "options": {
                "A": "$10$",
                "B": "$6$",
                "C": "$14$",
                "D": "$2$"
            },
            "answer": "A"
        },
        {
            "question": "According to Bohr's model, the angular momentum of an electron in $n$-th orbit is quantized as:",
            "options": {
                "A": "$L = \\frac{nh}{2\\pi}$",
                "B": "$L = \\frac{h}{2\\pi n}$",
                "C": "$L = \\frac{2\\pi n}{h}$",
                "D": "$L = nh$"
            },
            "answer": "A"
        }
    ],
    "Chemical Bonding and Molecular Structure": [
        {
            "question": "The geometry and hybridization of $\\text{SF}_6$ molecule are:",
            "options": {
                "A": "Octahedral, $sp^3d^2$",
                "B": "Trigonal bipyramidal, $sp^3d$",
                "C": "Tetrahedral, $sp^3$",
                "D": "Square planar, $dsp^2$"
            },
            "answer": "A"
        },
        {
            "question": "Which of the following has zero dipole moment?",
            "options": {
                "A": "$\\text{BF}_3$",
                "B": "$\\text{NH}_3$",
                "C": "$\\text{H}_2\\text{O}$",
                "D": "$\\text{SO}_2$"
            },
            "answer": "A"
        }
    ],
    "Equilibrium": [
        {
            "question": "For the gaseous reaction $\\text{N}_2 + 3\\text{H}_2 \\rightleftharpoons 2\\text{NH}_3$, the relation between $K_p$ and $K_c$ is:",
            "options": {
                "A": "$K_p = K_c (RT)^{-2}$",
                "B": "$K_p = K_c (RT)^2$",
                "C": "$K_p = K_c (RT)^{-1}$",
                "D": "$K_p = K_c$"
            },
            "answer": "A"
        },
        {
            "question": "The pH of a $10^{-3} \\text{ M}$ solution of $\\text{HCl}$ is:",
            "options": {
                "A": "$3$",
                "B": "$11$",
                "C": "$7$",
                "D": "$1$"
            },
            "answer": "A"
        }
    ],
    "Organic Chemistry: Some Basic Principles and Techniques": [
        {
            "question": "The IUPAC name of $\\text{CH}_3-\\text{CH}(\\text{OH})-\\text{CH}_2-\\text{CH}_3$ is:",
            "options": {
                "A": "Butan-2-ol",
                "B": "Butan-1-ol",
                "C": "2-Methylpropan-1-ol",
                "D": "Propan-2-ol"
            },
            "answer": "A"
        },
        {
            "question": "Which of the following carbocations is the most stable?",
            "options": {
                "A": "$(CH_3)_3C^+$ (Tertiary)",
                "B": "$(CH_3)_2CH^+$ (Secondary)",
                "C": "CH_3CH_2^+ (Primary)",
                "D": "CH_3^+ (Methyl)"
            },
            "answer": "A"
        }
    ],
    "Coordination Compounds": [
        {
            "question": "The IUPAC name of the complex $[K_3[Fe(CN)_6]]$ is:",
            "options": {
                "A": "Potassium hexacyanidoferrate(III)",
                "B": "Potassium hexacyanidoferrate(II)",
                "C": "Tripotassium hexacyanoiron(III)",
                "D": "Potassium cyanoferrate(III)"
            },
            "answer": "A"
        },
        {
            "question": "Which type of isomerism is shown by $[Co(NH_3)_5(SO_4)]Br$ and $[Co(NH_3)_5Br]SO_4$?",
            "options": {
                "A": "Ionisation isomerism",
                "B": "Linkage isomerism",
                "C": "Coordination isomerism",
                "D": "Geometrical isomerism"
            },
            "answer": "A"
        }
    ]
}

# Save Physics Dataset
phys_file = '/home/arun/projects/neet_pp/physics_bot/data/questions_dataset.json'
with open(phys_file, 'w', encoding='utf-8') as f:
    json.dump({
        "subject": "NEET Physics",
        "total_chapters": len(physics_chapters),
        "chapters": physics_chapters
    }, f, indent=2, ensure_ascii=False)

print(f"Physics dataset written to {phys_file} with {len(physics_chapters)} chapters.")

# Save Chemistry Dataset
chem_file = '/home/arun/projects/neet_pp/chemistry_bot/data/questions_dataset.json'
with open(chem_file, 'w', encoding='utf-8') as f:
    json.dump({
        "subject": "NEET Chemistry",
        "total_chapters": len(chemistry_chapters),
        "chapters": chemistry_chapters
    }, f, indent=2, ensure_ascii=False)

print(f"Chemistry dataset written to {chem_file} with {len(chemistry_chapters)} chapters.")
