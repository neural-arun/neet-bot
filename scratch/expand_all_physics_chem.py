import json

all_physics_chapters = {
    "Units and Measurements": [
        {"question": "The dimensional formula for gravitational constant $G$ is:", "options": {"A": "$[M^{-1} L^3 T^{-2}]$", "B": "$[M^1 L^3 T^{-2}]$", "C": "$[M^{-1} L^2 T^{-2}]$", "D": "$[M^{-2} L^3 T^{-1}]$"}, "answer": "A"},
        {"question": "Least count of a vernier calliper with 10 vernier divisions matching 9 main scale divisions ($1\\text{ mm}$ each) is:", "options": {"A": "$0.1 \\text{ mm}$", "B": "$0.01 \\text{ mm}$", "C": "$0.001 \\text{ mm}$", "D": "$1.0 \\text{ mm}$"}, "answer": "A"}
    ],
    "Motion in a Straight Line": [
        {"question": "A body starting from rest moves with uniform acceleration $a$. The displacement in $n$-th second is:", "options": {"A": "$S_n = \\frac{a}{2}(2n - 1)$", "B": "$S_n = a(2n - 1)$", "C": "$S_n = \\frac{a}{2}(n^2 - 1)$", "D": "$S_n = \\frac{a}{2}(2n + 1)$"}, "answer": "A"},
        {"question": "A particle thrown vertically upwards with speed $u$ reaches maximum height $H$. $H$ is equal to:", "options": {"A": "$\\frac{u^2}{2g}$", "B": "$\\frac{u^2}{g}$", "C": "$\\frac{2u^2}{g}$", "D": "$\\frac{u}{2g}$"}, "answer": "A"}
    ],
    "Motion in a Plane": [
        {"question": "The angle of projection $\\theta$ for maximum horizontal range of a projectile is:", "options": {"A": "$45^\\circ$", "B": "$30^\\circ$", "C": "$60^\\circ$", "D": "$90^\\circ$"}, "answer": "A"},
        {"question": "Centripetal acceleration $a_c$ of a particle in circular motion of radius $r$ with speed $v$ is:", "options": {"A": "$\\frac{v^2}{r}$", "B": "$v^2 r$", "C": "$\\frac{v}{r}$", "D": "$v r^2$"}, "answer": "A"}
    ],
    "Laws of Motion": [
        {"question": "Tension $T$ in a cable lifting an elevator of mass $M$ upwards with acceleration $a$ is:", "options": {"A": "$M(g + a)$", "B": "$M(g - a)$", "C": "$Mg$", "D": "$Ma$"}, "answer": "A"},
        {"question": "Limiting friction $F_s$ is related to normal reaction $N$ by:", "options": {"A": "$F_s = \\mu_s N$", "B": "$F_s = \\frac{N}{\\mu_s}$", "C": "$F_s = \\mu_s N^2$", "D": "$F_s = \\frac{\\mu_s}{N}$"}, "answer": "A"}
    ],
    "Work, Energy, and Power": [
        {"question": "Kinetic energy $K$ of a body of mass $m$ with momentum $p$ is:", "options": {"A": "$\\frac{p^2}{2m}$", "B": "$\\frac{p}{2m}$", "C": "$2mp^2$", "D": "$\\frac{p^2}{m}$"}, "answer": "A"},
        {"question": "Power $P$ delivered by force $\\vec{F}$ to a body moving with velocity $\\vec{v}$ is:", "options": {"A": "$\\vec{F} \\cdot \\vec{v}$", "B": "$\\vec{F} \\times \\vec{v}$", "C": "$\\frac{F}{v}$", "D": "$F v^2$"}, "answer": "A"}
    ],
    "System of Particles and Rotational Motion": [
        {"question": "Moment of inertia of a thin uniform ring of mass $M$ and radius $R$ about its diameter is:", "options": {"A": "$\\frac{1}{2} MR^2$", "B": "$MR^2$", "C": "$\\frac{2}{5} MR^2$", "D": "$\\frac{2}{3} MR^2$"}, "answer": "A"},
        {"question": "Torque $\\tau$ is related to angular momentum $L$ by:", "options": {"A": "$\\tau = \\frac{dL}{dt}$", "B": "$\\tau = L t$", "C": "$\\tau = \\frac{d^2L}{dt^2}$", "D": "$L = \\frac{d\\tau}{dt}$"}, "answer": "A"}
    ],
    "Gravitation": [
        {"question": "Escape velocity $v_e$ from Earth's surface of radius $R$ is:", "options": {"A": "$\\sqrt{2gR}$", "B": "$\\sqrt{gR}$", "C": "$2\\sqrt{gR}$", "D": "$\\frac{\\sqrt{gR}}{2}$"}, "answer": "A"},
        {"question": "Acceleration due to gravity $g_h$ at height $h \\ll R$ above Earth's surface is:", "options": {"A": "$g\\left(1 - \\frac{2h}{R}\\right)$", "B": "$g\\left(1 - \\frac{h}{R}\\right)$", "C": "$g\\left(1 + \\frac{2h}{R}\\right)$", "D": "$g\\left(1 - \\frac{h}{2R}\\right)$"}, "answer": "A"}
    ],
    "Mechanical Properties of Solids and Fluids": [
        {"question": "Young's modulus $Y$ is defined as the ratio of:", "options": {"A": "Longitudinal stress to longitudinal strain", "B": "Shear stress to shear strain", "C": "Volumetric stress to volumetric strain", "D": "Tensile stress to shear strain"}, "answer": "A"},
        {"question": "Terminal velocity $v_t$ of a spherical ball falling in a viscous fluid depends on radius $r$ as:", "options": {"A": "$v_t \\propto r^2$", "B": "$v_t \\propto r$", "C": "$v_t \\propto \\frac{1}{r}$", "D": "$v_t \\propto r^3$"}, "answer": "A"}
    ],
    "Thermodynamics": [
        {"question": "First law of thermodynamics is a statement of conservation of:", "options": {"A": "Energy", "B": "Mass", "C": "Momentum", "D": "Temperature"}, "answer": "A"},
        {"question": "Efficiency $\\eta$ of a Carnot engine working between temperatures $T_1$ (source) and $T_2$ (sink) is:", "options": {"A": "$1 - \\frac{T_2}{T_1}$", "B": "$1 - \\frac{T_1}{T_2}$", "C": "$\\frac{T_2}{T_1}$", "D": "$\\frac{T_1 - T_2}{T_2}$"}, "answer": "A"}
    ],
    "Kinetic Theory of Gases": [
        {"question": "The root mean square speed $v_{rms}$ of gas molecules of molar mass $M$ at temperature $T$ is:", "options": {"A": "$\\sqrt{\\frac{3RT}{M}}$", "B": "$\\sqrt{\\frac{8RT}{\\pi M}}$", "C": "$\\sqrt{\\frac{2RT}{M}}$", "D": "$\\sqrt{\\frac{RT}{M}}$"}, "answer": "A"},
        {"question": "Average kinetic energy per molecule of a monoatomic gas at absolute temperature $T$ is:", "options": {"A": "$\\frac{3}{2} k_B T$", "B": "$\\frac{5}{2} k_B T$", "C": "$\\frac{1}{2} k_B T$", "D": "$3 k_B T$"}, "answer": "A"}
    ],
    "Oscillations and Waves": [
        {"question": "Time period $T$ of a simple pendulum of length $L$ is given by:", "options": {"A": "$T = 2\\pi \\sqrt{\\frac{L}{g}}$", "B": "$T = 2\\pi \\sqrt{\\frac{g}{L}}$", "C": "$T = \\pi \\sqrt{\\frac{L}{g}}$", "D": "$T = \\frac{1}{2\\pi} \\sqrt{\\frac{L}{g}}$"}, "answer": "A"},
        {"question": "Velocity of sound in an ideal gas of density $\\rho$ and pressure $P$ (Laplace correction) is:", "options": {"A": "$v = \\sqrt{\\frac{\\gamma P}{\\rho}}$", "B": "$v = \\sqrt{\\frac{P}{\\rho}}$", "C": "$v = \\sqrt{\\frac{\\rho}{\\gamma P}}$", "D": "$v = \\gamma \\sqrt{\\frac{P}{\\rho}}$"}, "answer": "A"}
    ],
    "Electrostatics": [
        {"question": "Electrostatic force $F$ between two point charges $q_1$ and $q_2$ separated by distance $r$ in vacuum is:", "options": {"A": "$F = \\frac{1}{4\\pi \\varepsilon_0} \\frac{q_1 q_2}{r^2}$", "B": "$F = \\frac{1}{4\\pi \\varepsilon_0} \\frac{q_1 q_2}{r}$", "C": "$F = \\varepsilon_0 \\frac{q_1 q_2}{r^2}$", "D": "$F = \\frac{q_1 q_2}{4\\pi r^2}$"}, "answer": "A"},
        {"question": "Capacitance of a parallel plate capacitor with plate area $A$ and separation $d$ in vacuum is:", "options": {"A": "$C = \\frac{\\varepsilon_0 A}{d}$", "B": "$C = \\frac{\\varepsilon_0 d}{A}$", "C": "$C = \\frac{A}{\\varepsilon_0 d}$", "D": "$C = \\varepsilon_0 A d$"}, "answer": "A"}
    ],
    "Current Electricity": [
        {"question": "Drift velocity $v_d$ of electrons in a conductor of cross-section $A$ carrying current $I$ with electron density $n$ is:", "options": {"A": "$v_d = \\frac{I}{n e A}$", "B": "$v_d = \\frac{n e A}{I}$", "C": "$v_d = \\frac{I A}{n e}$", "D": "$v_d = n e A I$"}, "answer": "A"},
        {"question": "Equivalent resistance $R_{eq}$ of two resistors $R_1$ and $R_2$ connected in parallel is:", "options": {"A": "$\\frac{R_1 R_2}{R_1 + R_2}$", "B": "$R_1 + R_2$", "C": "$\\frac{R_1 + R_2}{R_1 R_2}$", "D": "$\\frac{R_1}{R_2}$"}, "answer": "A"}
    ],
    "Moving Charges and Magnetism": [
        {"question": "Force $\\vec{F}$ on a charge $q$ moving with velocity $\\vec{v}$ in a magnetic field $\\vec{B}$ is:", "options": {"A": "$\\vec{F} = q(\\vec{v} \\times \\vec{B})$", "B": "$\\vec{F} = q(\\vec{v} \\cdot \\vec{B})$", "C": "$\\vec{F} = \\frac{q}{\\vec{v} \\times \\vec{B}}$", "D": "$\\vec{F} = q \\vec{v} B$"}, "answer": "A"},
        {"question": "Magnetic field at the center of a circular loop of radius $R$ carrying current $I$ is:", "options": {"A": "$B = \\frac{\\mu_0 I}{2R}$", "B": "$B = \\frac{\\mu_0 I}{2\\pi R}$", "C": "$B = \\frac{\\mu_0 I}{4\\pi R}$", "D": "$B = \\frac{\\mu_0 I}{\\pi R}$"}, "answer": "A"}
    ],
    "Electromagnetic Induction and AC": [
        {"question": "Induced emf $\\varepsilon$ according to Faraday's law of electromagnetic induction is:", "options": {"A": "$\\varepsilon = -\\frac{d\\Phi_B}{dt}$", "B": "$\\varepsilon = -\\Phi_B t$", "C": "$\\varepsilon = \\frac{d^2\\Phi_B}{dt^2}$", "D": "$\\varepsilon = -L \\Phi_B$"}, "answer": "A"},
        {"question": "Resonant frequency $f_r$ in a series LCR circuit with inductance $L$ and capacitance $C$ is:", "options": {"A": "$f_r = \\frac{1}{2\\pi \\sqrt{LC}}$", "B": "$f_r = 2\\pi \\sqrt{LC}$", "C": "$f_r = \\frac{1}{\\sqrt{LC}}$", "D": "$f_r = \\frac{\\sqrt{LC}}{2\\pi}$"}, "answer": "A"}
    ],
    "Electromagnetic Waves": [
        {"question": "Speed of electromagnetic waves in vacuum $c$ is related to $\\varepsilon_0$ and $\\mu_0$ by:", "options": {"A": "$c = \\frac{1}{\\sqrt{\\mu_0 \\varepsilon_0}}$", "B": "$c = \\sqrt{\\mu_0 \\varepsilon_0}$", "C": "$c = \\frac{1}{\\mu_0 \\varepsilon_0}$", "D": "$c = \\mu_0 \\varepsilon_0$"}, "answer": "A"}
    ],
    "Ray Optics and Wave Optics": [
        {"question": "Lens maker's formula for a thin lens of refractive index $\\mu$ in air is:", "options": {"A": "$\\frac{1}{f} = (\\mu - 1)\\left(\\frac{1}{R_1} - \\frac{1}{R_2}\\right)$", "B": "$\\frac{1}{f} = (\\mu + 1)\\left(\\frac{1}{R_1} + \\frac{1}{R_2}\\right)$", "C": "$\\frac{1}{f} = \\mu \\left(\\frac{1}{R_1} - \\frac{1}{R_2}\\right)$", "D": "$f = (\\mu - 1)(R_1 - R_2)$"}, "answer": "A"},
        {"question": "Fringe width $\\beta$ in Young's double slit experiment with wavelength $\\lambda$, slit separation $d$, and screen distance $D$ is:", "options": {"A": "$\\beta = \\frac{\\lambda D}{d}$", "B": "$\\beta = \\frac{\\lambda d}{D}$", "C": "$\\beta = \\frac{D}{d \\lambda}$", "D": "$\\beta = \\lambda D d$"}, "answer": "A"}
    ],
    "Dual Nature of Radiation and Matter": [
        {"question": "Einstein's photoelectric equation relates kinetic energy $K_{max}$, frequency $\\nu$, and work function $\\phi_0$ as:", "options": {"A": "$K_{max} = h\\nu - \\phi_0$", "B": "$K_{max} = h\\nu + \\phi_0$", "C": "$\\phi_0 = h\\nu + K_{max}$", "D": "$K_{max} = \\frac{h}{\\nu} - \\phi_0$"}, "answer": "A"}
    ],
    "Atoms and Nuclei": [
        {"question": "Bohr radius $r_1$ of the first orbit of hydrogen atom is approximately equal to:", "options": {"A": "$0.53 \\text{ \\AA}$", "B": "$5.3 \\text{ \\AA}$", "C": "$0.053 \\text{ \\AA}$", "D": "$1.06 \\text{ \\AA}$"}, "answer": "A"},
        {"question": "Half-life $T_{1/2}$ of a radioactive substance is related to decay constant $\\lambda$ by:", "options": {"A": "$T_{1/2} = \\frac{0.693}{\\lambda}$", "B": "$T_{1/2} = 0.693 \\lambda$", "C": "$T_{1/2} = \\frac{\\lambda}{0.693}$", "D": "$T_{1/2} = \\frac{1}{\\lambda}$"}, "answer": "A"}
    ],
    "Semiconductor Electronics": [
        {"question": "In an n-type semiconductor, majority carriers are electrons and minority carriers are:", "options": {"A": "Holes", "B": "Protons", "C": "Positrons", "D": "Neutrons"}, "answer": "A"},
        {"question": "The truth table with output $Y = \\overline{A \\cdot B}$ corresponds to which logic gate?", "options": {"A": "NAND gate", "B": "NOR gate", "C": "AND gate", "D": "OR gate"}, "answer": "A"}
    ]
}

all_chemistry_chapters = {
    "Some Basic Concepts of Chemistry": [
        {"question": "Molarity $M$ of a solution is expressed in units of:", "options": {"A": "$\\text{mol L}^{-1}$", "B": "$\\text{mol kg}^{-1}$", "C": "$\\text{g L}^{-1}$", "D": "$\\text{mol}^{-1} \\text{L}$"}, "answer": "A"},
        {"question": "Number of atoms in $12 \\text{ g}$ of Carbon-12 isotope is equal to Avogadro number $N_A$, which is:", "options": {"A": "$6.022 \\times 10^{23}$", "B": "$6.022 \\times 10^{22}$", "C": "$3.011 \\times 10^{23}$", "D": "$1.66 \\times 10^{-24}$"}, "answer": "A"}
    ],
    "Structure of Atom": [
        {"question": "Heisenberg uncertainty principle is expressed mathematically as:", "options": {"A": "$\\Delta x \\cdot \\Delta p \\ge \\frac{h}{4\\pi}$", "B": "$\\Delta x \\cdot \\Delta p \\ge \\frac{h}{2\\pi}$", "C": "$\\Delta x \\cdot \\Delta v \\ge \\frac{h}{4\\pi}$", "D": "$\\Delta x = \\frac{h}{\\Delta p}$"}, "answer": "A"},
        {"question": "Maximum number of electrons in an orbital with principal quantum number $n = 3$ is:", "options": {"A": "18", "B": "8", "C": "32", "D": "10"}, "answer": "A"}
    ],
    "Classification of Elements and Periodicity": [
        {"question": "Which element has the highest electronegativity on Pauling scale?", "options": {"A": "Fluorine (F)", "B": "Chlorine (Cl)", "C": "Oxygen (O)", "D": "Nitrogen (N)"}, "answer": "A"},
        {"question": "Ionization enthalpy generally increases across a period from left to right due to increase in:", "options": {"A": "Effective nuclear charge ($Z_{eff}$)", "B": "Atomic radius", "C": "Shielding effect", "D": "Principal quantum number"}, "answer": "A"}
    ],
    "Chemical Bonding and Molecular Structure": [
        {"question": "Hybridization and shape of $\\text{SF}_6$ molecule are:", "options": {"A": "$sp^3d^2$, Octahedral", "B": "$sp^3d$, Trigonal bipyramidal", "C": "$sp^3$, Tetrahedral", "D": "$dsp^2$, Square planar"}, "answer": "A"},
        {"question": "Bond order of $\\text{O}_2$ molecule according to Molecular Orbital Theory is:", "options": {"A": "2", "B": "1", "C": "2.5", "D": "3"}, "answer": "A"}
    ],
    "Thermodynamics (Chemistry)": [
        {"question": "Gibbs free energy change $\\Delta G$ is related to enthalpy change $\\Delta H$ and entropy change $\\Delta S$ by:", "options": {"A": "$\\Delta G = \\Delta H - T\\Delta S$", "B": "$\\Delta G = \\Delta H + T\\Delta S$", "C": "$\\Delta G = T\\Delta S - \\Delta H$", "D": "$\\Delta G = \\frac{\\Delta H}{T\\Delta S}$"}, "answer": "A"},
        {"question": "A reaction is spontaneous at all temperatures if:", "options": {"A": "$\\Delta H < 0$ and $\\Delta S > 0$", "B": "$\\Delta H > 0$ and $\\Delta S < 0$", "C": "$\\Delta H > 0$ and $\\Delta S > 0$", "D": "$\\Delta H < 0$ and $\\Delta S < 0$"}, "answer": "A"}
    ],
    "Equilibrium": [
        {"question": "pH of a solution is defined as:", "options": {"A": "$-\\log_{10}[H^+]$", "B": "$\\log_{10}[H^+]$", "C": "$-\\ln[H^+]$", "D": "$\\frac{1}{[H^+]}$"}, "answer": "A"},
        {"question": "Solubility product $K_{sp}$ of $\\text{AgCl}$ with solubility $S \\text{ mol L}^{-1}$ is:", "options": {"A": "$K_{sp} = S^2$", "B": "$K_{sp} = 4S^3$", "C": "$K_{sp} = 27S^4$", "D": "$K_{sp} = S$"}, "answer": "A"}
    ],
    "Redox Reactions and Electrochemistry": [
        {"question": "Nernst equation for electrode potential $E$ at $298 \\text{ K}$ is:", "options": {"A": "$E = E^\\circ - \\frac{0.0591}{n} \\log_{10} Q$", "B": "$E = E^\\circ + \\frac{0.0591}{n} \\log_{10} Q$", "C": "$E = E^\\circ - \\frac{0.0591}{n} \\ln Q$", "D": "$E = E^\\circ - 0.0591 n \\log_{10} Q$"}, "answer": "A"},
        {"question": "In a galvanic cell, oxidation occurs at the:", "options": {"A": "Anode (Negative electrode)", "B": "Cathode (Positive electrode)", "C": "Salt bridge", "D": "Outer circuit wire"}, "answer": "A"}
    ],
    "Chemical Kinetics": [
        {"question": "Half-life period $t_{1/2}$ of a first-order reaction is independent of initial concentration $A_0$ and equals:", "options": {"A": "$\\frac{0.693}{k}$", "B": "$\\frac{A_0}{2k}$", "C": "$\\frac{1}{k A_0}$", "D": "$\\frac{2k}{0.693}$"}, "answer": "A"},
        {"question": "Arrhenius equation relating rate constant $k$ with activation energy $E_a$ and temperature $T$ is:", "options": {"A": "$k = A e^{-E_a / RT}$", "B": "$k = A e^{+E_a / RT}$", "C": "$k = A \\ln(E_a / RT)$", "D": "$k = \\frac{A E_a}{RT}$"}, "answer": "A"}
    ],
    "Solutions": [
        {"question": "Raoult's law for a solution of volatile liquids states that relative lowering of vapor pressure equals:", "options": {"A": "Mole fraction of solute ($x_2$)", "B": "Molarity of solution", "C": "Molality of solution", "D": "Mole fraction of solvent ($x_1$)"}, "answer": "A"},
        {"question": "Van't Hoff factor $i$ for complete dissociation of $\\text{NaCl}$ in water is:", "options": {"A": "2", "B": "1", "C": "3", "D": "0.5"}, "answer": "A"}
    ],
    "Surface Chemistry and Extraction": [
        {"question": "Freundlich adsorption isotherm equation is:", "options": {"A": "$\\frac{x}{m} = k P^{1/n}$", "B": "$\\frac{x}{m} = k P^n$", "C": "$\\frac{x}{m} = k + P$", "D": "$\\frac{x}{m} = \\frac{k}{P}$"}, "answer": "A"}
    ],
    "p-Block Elements": [
        {"question": "Which noble gas is most abundant in Earth's atmosphere?", "options": {"A": "Argon (Ar)", "B": "Helium (He)", "C": "Neon (Ne)", "D": "Xenon (Xe)"}, "answer": "A"},
        {"question": "In Haber's process for ammonia synthesis ($\text{N}_2 + 3\text{H}_2 \rightleftharpoons 2\text{NH}_3$), catalyst used is:", "options": {"A": "Finely divided Iron (Fe) with Mo promoter", "B": "Platinum (Pt) gauge", "C": "Nickel (Ni)", "D": "Vanadium pentoxide ($V_2O_5$)"}, "answer": "A"}
    ],
    "d- and f-Block Elements": [
        {"question": "Transition elements show variable oxidation states due to small energy difference between:", "options": {"A": "$(n-1)d$ and $ns$ orbitals", "B": "$ns$ and $np$ orbitals", "C": "$(n-2)f$ and $(n-1)d$ orbitals", "D": "$ns$ and $(n-2)f$ orbitals"}, "answer": "A"}
    ],
    "Coordination Compounds": [
        {"question": "IUPAC name of $[K_3[Fe(CN)_6]]$ is:", "options": {"A": "Potassium hexacyanidoferrate(III)", "B": "Potassium hexacyanidoferrate(II)", "C": "Tripotassium hexacyanoiron(III)", "D": "Potassium cyanoferrate(III)"}, "answer": "A"}
    ],
    "Organic Chemistry: Basic Principles": [
        {"question": "IUPAC name of $\\text{CH}_3-\\text{CH}(\\text{OH})-\\text{CH}_2-\\text{CH}_3$ is:", "options": {"A": "Butan-2-ol", "B": "Butan-1-ol", "C": "2-Methylpropan-1-ol", "D": "Propan-2-ol"}, "answer": "A"}
    ],
    "Hydrocarbons": [
        {"question": "Ozonolysis of propene ($\text{CH}_3-\text{CH}=\text{CH}_2$) followed by $\text{Zn}/\text{H}_2\text{O}$ yields:", "options": {"A": "Ethanal ($\text{CH}_3\text{CHO}$) and Methanal ($\text{HCHO}$)", "B": "Propanal and Methanal", "C": "Acetone and Methanal", "D": "Ethanal and Propanal"}, "answer": "A"}
    ],
    "Haloalkanes and Haloarenes": [
        {"question": "$S_N2$ reaction mechanism proceeds with complete inversion of configuration known as:", "options": {"A": "Walden inversion", "B": "Racemisation", "C": "Retention of configuration", "D": "Tautomerisation"}, "answer": "A"}
    ],
    "Alcohols, Phenols and Ethers": [
        {"question": "Lucas reagent used to distinguish $1^\\circ, 2^\\circ, 3^\\circ$ alcohols consists of:", "options": {"A": "Anhydrous $\\text{ZnCl}_2$ + conc. $\\text{HCl}$", "B": "Dilute $\\text{H}_2\\text{SO}_4$ + $\\text{KMnO}_4$", "C": "Conc. $\\text{HNO}_3$ + conc. $\\text{H}_2\\text{SO}_4$", "D": "$\\text{PCl}_5$ + Pyridine"}, "answer": "A"}
    ],
    "Aldehydes, Ketones and Carboxylic Acids": [
        {"question": "Tollens' reagent used to test aldehydes is an ammoniacal solution of:", "options": {"A": "Silver nitrate ($[Ag(NH_3)_2]^+$)", "B": "Copper sulphate ($\text{CuSO}_4$)", "C": "Sodium hydroxide ($\text{NaOH}$)", "D": "Potassium permanganate ($\text{KMnO}_4$)"}, "answer": "A"}
    ],
    "Amines": [
        {"question": "Hinsberg reagent used to distinguish primary, secondary, and tertiary amines is:", "options": {"A": "Benzenesulphonyl chloride ($\\text{C}_6\\text{H}_5\\text{SO}_2\\text{Cl}$)", "B": "Acetyl chloride", "C": "Phosgene gas", "D": "Nitrous acid ($\\text{HNO}_2$)"}, "answer": "A"}
    ],
    "Biomolecules (Chemistry)": [
        {"question": "Which carbohydrate is known as table sugar?", "options": {"A": "Sucrose (Glucose + Fructose)", "B": "Maltose", "C": "Lactose", "D": "Starch"}, "answer": "A"}
    ]
}

# Write Physics Dataset
with open('/home/arun/projects/neet_pp/physics_bot/data/questions_dataset.json', 'w', encoding='utf-8') as f:
    json.dump({
        "subject": "NEET Physics",
        "total_chapters": len(all_physics_chapters),
        "chapters": all_physics_chapters
    }, f, indent=2, ensure_ascii=False)

# Write Chemistry Dataset
with open('/home/arun/projects/neet_pp/chemistry_bot/data/questions_dataset.json', 'w', encoding='utf-8') as f:
    json.dump({
        "subject": "NEET Chemistry",
        "total_chapters": len(all_chemistry_chapters),
        "chapters": all_chemistry_chapters
    }, f, indent=2, ensure_ascii=False)

print(f"COMPLETE: Physics dataset has {len(all_physics_chapters)} chapters.")
print(f"COMPLETE: Chemistry dataset has {len(all_chemistry_chapters)} chapters.")
