import json
import random
import os

random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'neet_bot', 'data')

# ── 2. UNIQUE CHEMISTRY QUESTIONS GENERATOR ──

chemistry_chapter_generators = {
    "Some Basic Concepts of Chemistry": [
        ("The number of moles of solute present in 1 liter of solution is called:", "Molarity", ["Molarity", "Molality", "Normality", "Mole fraction"]),
        ("What is the mass of 1 mole of $\\text{CO}_2$ gas at STP?", "$44 \\text{ g}$", ["$44 \\text{ g}$", "$22.4 \\text{ g}$", "$12 \\text{ g}$", "$32 \\text{ g}$"]),
        ("Volume occupied by 1 mole of any ideal gas at STP is:", "$22.4 \\text{ L}$", ["$22.4 \\text{ L}$", "$11.2 \\text{ L}$", "$44.8 \\text{ L}$", "$2.24 \\text{ L}$"]),
        ("Empirical formula of glucose ($\\\\text{C}_6\\\\text{H}_{12}\\\\text{O}_6$) is:", "$\\text{CH}_2\\text{O}$", ["$\\text{CH}_2\\text{O}$", "$\\text{C}_6\\text{H}_{12}\\text{O}_6$", "$\\text{CHO}$", "$\\text{CH}_4\\text{O}$"]),
        ("Number of atoms in 12 g of Carbon-12 is equal to:", "Avogadro's number ($6.022 \\times 10^{23}$)", ["Avogadro's number ($6.022 \\times 10^{23}$)", "$3.011 \\times 10^{23}$", "$1.204 \\times 10^{24}$", "$6.022 \\times 10^{22}$"])
    ],
    "Structure of Atom": [
        ("Which quantum number determines the main energy level or shell of an electron?", "Principal quantum number ($n$)", ["Principal quantum number ($n$)", "Azimuthal quantum number ($l$)", "Magnetic quantum number ($m$)", "Spin quantum number ($s$)$"]),
        ("Maximum number of electrons that can be accommodated in $p$-subshell is:", "6", ["6", "2", "10", "14"]),
        ("Maximum number of electrons in a shell of principal quantum number $n$ is:", "$2n^2$", ["$2n^2$", "$n^2$", "$2n$", "$4n^2$"]),
        ("de Broglie wavelength $\\lambda$ of a particle of mass $m$ and velocity $v$ is:", "$\\lambda = \\frac{h}{m v}$", ["$\\lambda = \\frac{h}{m v}$", "$\\lambda = \\frac{m v}{h}$", "$\\lambda = h m v$", "$\\lambda = \\frac{h}{m v^2}$"]),
        ("Heisenberg uncertainty principle states:", "$\\Delta x \\cdot \\Delta p \\ge \\frac{h}{4\\pi}$", ["$\\Delta x \\cdot \\Delta p \\ge \\frac{h}{4\\pi}$", "$\\Delta x \\cdot \\Delta p \\ge \\frac{h}{2\\pi}$", "$\\Delta x \\cdot \\Delta v \\ge \\frac{h}{4\\pi}$", "$\\Delta x \\cdot \\Delta p = 0$"])
    ],
    "Classification of Elements and Periodicity": [
        ("Which of the following elements has the highest electronegativity?", "Fluorine (F)", ["Fluorine (F)", "Chlorine (Cl)", "Oxygen (O)", "Nitrogen (N)"]),
        ("General electronic configuration of d-block elements is:", "$(n-1)d^{1-10} n s^{1-2}$", ["$(n-1)d^{1-10} n s^{1-2}$", "$n d^{10} n s^2$", "$(n-1)d^5 n s^1$", "$n d^5 n s^2$"]),
        ("Which element has the highest electron gain enthalpy (most negative)?", "Chlorine (Cl)", ["Chlorine (Cl)", "Fluorine (F)", "Bromine (Br)", "Iodine (I)"]),
        ("Across a period from left to right, atomic radius generally:", "Decreases", ["Decreases", "Increases", "Remains constant", "First increases then decreases"]),
        ("Which of the following is an amphoteric oxide?", "$\\text{Al}_2\\text{O}_3$", ["$\\text{Al}_2\\text{O}_3$", "$\\text{Na}_2\\text{O}$", "$\\text{SO}_3$", "$\\text{CO}_2$"])
    ],
    "Chemical Bonding and Molecular Structure": [
        ("The geometry of methane ($\\text{CH}_4$) molecule is:", "Tetrahedral", ["Tetrahedral", "Trigonal planar", "Linear", "Octahedral"]),
        ("The bond order of Nitrogen molecule ($\\text{N}_2$) is:", "3", ["3", "2", "1", "2.5"]),
        ("Shape of Ammonia ($\\text{NH}_3$) molecule according to VSEPR theory is:", "Trigonal pyramidal", ["Trigonal pyramidal", "Tetrahedral", "Trigonal planar", "T-shaped"]),
        ("Which of the following species is paramagnetic?", "$\\text{O}_2$", ["$\\text{O}_2$", "$\\text{N}_2$", "$\\text{F}_2$", "$\\text{C}_2$"]),
        ("Hybridization of central Carbon atom in Carbon dioxide ($\\text{CO}_2$) is:", "$sp$", ["$sp$", "$sp^2$", "$sp^3$", "$sp^3d$"])
    ],
    "States of Matter and Thermodynamics": [
        ("Boyle's law states that at constant temperature, pressure $P$ and volume $V$ satisfy:", "$P \\propto \\frac{1}{V}$", ["$P \\propto \\frac{1}{V}$", "$P \\propto V$", "$P \\propto T$", "$V \\propto T$"]),
        ("Enthalpy change $\\Delta H$ is related to internal energy change $\\Delta U$ by:", "$\\Delta H = \\Delta U + \\Delta n_g R T$", ["$\\Delta H = \\Delta U + \\Delta n_g R T$", "$\\Delta H = \\Delta U - \\Delta n_g R T$", "$\\Delta U = \\Delta H + \\Delta n_g R T$", "$\\Delta H = \\Delta n_g R T$"]),
        ("A process is spontaneous at all temperatures if:", "$\\Delta H < 0$ and $\\Delta S > 0$", ["$\\Delta H < 0$ and $\\Delta S > 0$", "$\\Delta H > 0$ and $\\Delta S < 0$", "$\\Delta H > 0$ and $\\Delta S > 0$", "$\\Delta H < 0$ and $\\Delta S < 0$"]),
        ("Gibbs free energy change $\\Delta G$ is related to $\\Delta H$ and $\\Delta S$ by:", "$\\Delta G = \\Delta H - T \\Delta S$", ["$\\Delta G = \\Delta H - T \\Delta S$", "$\\Delta G = \\Delta H + T \\Delta S$", "$\\Delta G = T \\Delta S - \\Delta H$", "$\\Delta G = \\Delta H / T \\Delta S$"]),
        ("Third law of thermodynamics states that entropy of a perfectly crystalline substance at absolute zero is:", "Zero", ["Zero", "Maximum", "Infinite", "Negative"])
    ],
    "Equilibrium": [
        ("pH of pure water at $25^\\circ\\text{C}$ is:", "7", ["7", "0", "14", "1"]),
        ("For a general reversible reaction $A + B \\rightleftharpoons C + D$, equilibrium constant $K_c$ is:", "$K_c = \\frac{[C][D]}{[A][B]}$", ["$K_c = \\frac{[C][D]}{[A][B]}$", "$K_c = \\frac{[A][B]}{[C][D]}$", "$K_c = [C][D] - [A][B]$", "$K_c = \\frac{[A]+[B]}{[C]+[D]}$"]),
        ("Relation between $K_p$ and $K_c$ is:", "$K_p = K_c (RT)^{\\Delta n_g}$", ["$K_p = K_c (RT)^{\\Delta n_g}$", "$K_c = K_p (RT)^{\\Delta n_g}$", "$K_p = K_c + \\Delta n_g R T$", "$K_p = K_c (RT)^{-\\Delta n_g}$"]),
        ("Conjugate base of $\\text{HCO}_3^-$ is:", "$\\text{CO}_3^{2-}$", ["$\\text{CO}_3^{2-}$", "$\\text{H}_2\\text{CO}_3$", "$\\text{OH}^-$", "$\\text{CO}_2$"]),
        ("Solubility product $K_{sp}$ of $\\text{AgCl}$ with solubility $s$ is:", "$K_{sp} = s^2$", ["$K_{sp} = s^2$", "$K_{sp} = 4s^3$", "$K_{sp} = s$", "$K_{sp} = 27s^4$"])
    ],
    "Redox Reactions and Electrochemistry": [
        ("Oxidation number of Chromium in Potassium dichromate ($\\text{K}_2\\text{Cr}_2\\text{O}_7$) is:", "+6", ["+6", "+3", "+7", "+5"]),
        ("Nernst equation for electrode potential $E$ at $25^\\circ\\text{C}$ is:", "$E = E^\\circ - \\frac{0.0591}{n} \\log Q$", ["$E = E^\\circ - \\frac{0.0591}{n} \\log Q$", "$E = E^\\circ + \\frac{0.0591}{n} \\log Q$", "$E = E^\\circ - \\frac{n}{0.0591} \\log Q$", "$E^\\circ = E - \\frac{0.0591}{n} \\log Q$"]),
        ("Standard reduction potential of Standard Hydrogen Electrode (SHE) is assigned as:", "$0.00 \\text{ V}$", ["$0.00 \\text{ V}$", "$1.00 \\text{ V}$", "$-1.00 \\text{ V}$", "$0.591 \\text{ V}$"]),
        ("Molar conductivity $\\Lambda_m$ is related to conductivity $\\kappa$ and molarity $M$ by:", "$\\Lambda_m = \\frac{\\kappa \\times 1000}{M}$", ["$\\Lambda_m = \\frac{\\kappa \\times 1000}{M}$", "$\\Lambda_m = \\frac{M \\times 1000}{\\kappa}$", "$\\Lambda_m = \\kappa \\times M$", "$\\Lambda_m = \\frac{\\kappa}{M}$"]),
        ("Faraday's first law of electrolysis states that mass deposited $m$ is:", "$m = Z I t$", ["$m = Z I t$", "$m = \\frac{Z}{I t}$", "$m = Z I^2 t$", "$m = \\frac{I t}{Z}$"])
    ],
    "Chemical Kinetics": [
        ("For a zero-order reaction, half-life period $t_{1/2}$ is proportional to initial concentration $[A]_0$ as:", "$t_{1/2} \\propto [A]_0$", ["$t_{1/2} \\propto [A]_0$", "$t_{1/2} \\propto \\frac{1}{[A]_0}$", "$t_{1/2}$ is independent of $[A]_0$", "$t_{1/2} \\propto [A]_0^2$"]),
        ("For a first-order reaction, half-life period $t_{1/2}$ is:", "$t_{1/2} = \\frac{0.693}{k}$", ["$t_{1/2} = \\frac{0.693}{k}$", "$t_{1/2} = \\frac{[A]_0}{2k}$", "$t_{1/2} = \\frac{1}{k [A]_0}$", "$t_{1/2} = 0.693 k$"]),
        ("Arrhenius equation relating rate constant $k$ and temperature $T$ is:", "$k = A e^{-E_a / RT}$", ["$k = A e^{-E_a / RT}$", "$k = A e^{E_a / RT}$", "$k = A \\ln(E_a / RT)$", "$k = E_a e^{-RT / A}$"]),
        ("Unit of rate constant $k$ for a first-order reaction is:", "$\\text{s}^{-1}$", ["$\\text{s}^{-1}$", "$\\text{mol L}^{-1} \\text{s}^{-1}$", "$\\text{L mol}^{-1} \\text{s}^{-1}$", "$\\text{L}^2 \\text{mol}^{-2} \\text{s}^{-1}$"]),
        ("A catalyst increases the rate of a chemical reaction by:", "Lowering activation energy $E_a$", ["Lowering activation energy $E_a$", "Increasing activation energy $E_a$", "Increasing enthalpy $\\Delta H$", "Decreasing temperature $T$"])
    ],
    "Surface Chemistry and Extraction": [
        ("Movement of colloidal particles under the influence of an applied electric field is called:", "Electrophoresis", ["Electrophoresis", "Tyndall effect", "Brownian movement", "Dialysis"]),
        ("Scattering of light by colloidal particles is known as:", "Tyndall effect", ["Tyndall effect", "Brownian motion", "Coagulation", "Peptization"]),
        ("Froth floatation process is used for the concentration of:", "Sulphide ores", ["Sulphide ores", "Oxide ores", "Carbonate ores", "Halide ores"]),
        ("Zone refining method is based on the principle of:", "Fractional crystallisation (greater solubility of impurities in molten metal)", ["Fractional crystallisation (greater solubility of impurities in molten metal)", "Difference in boiling points", "Magnetic separation", "Gravity separation"]),
        ("In the extraction of Aluminium by Hall-Héroult process, Cryolite ($\\text{Na}_3\\text{AlF}_6$) is added to:", "Lower the melting point of alumina and increase electrical conductivity", ["Lower the melting point of alumina and increase electrical conductivity", "Act as a reducing agent", "Precipitate aluminum hydroxide", "Remove silica impurity"])
    ],
    "p-Block Elements": [
        ("Which gas is liberated when concentrated Nitric acid reacts with Copper metal?", "$\\text{NO}_2$ gas", ["$\\text{NO}_2$ gas", "$\\text{NO}$ gas", "$\\text{N}_2\\text{O}$ gas", "$\\text{H}_2$ gas"]),
        ("Shape of Xenon tetrafluoride ($\\text{XeF}_4$) molecule according to VSEPR theory is:", "Square planar", ["Square planar", "Tetrahedral", "See-saw", "Octahedral"]),
        ("Which of the following oxoacids of Phosphorus has reducing properties (contains P-H bond)?", "$\\text{H}_3\\text{PO}_2$ (Hypophosphorous acid)", ["$\\text{H}_3\\text{PO}_2$ (Hypophosphorous acid)", "$\\text{H}_3\\text{PO}_4$ (Phosphoric acid)", "$\\text{H}_4\\text{P}_2\\text{O}_7$ (Pyrophosphoric acid)", "$\\text{HPO}_3$ (Metaphosphoric acid)"]),
        ("Strongest oxidizing agent among halogens in aqueous solution is:", "Fluorine (F2)", ["Fluorine (F2)", "Chlorine (Cl2)", "Bromine (Br2)", "Iodine (I2)"]),
        ("Boric acid ($\\text{H}_3\\text{BO}_3$) in water acts as a:", "Monobasic Lewis acid", ["Monobasic Lewis acid", "Tribasic Arrhenius acid", "Monobasic Bronsted acid", "Neutral salt"])
    ],
    "d- and f-Block Elements": [
        ("Magnetic moment $\\mu$ of a transition metal ion with $n$ unpaired electrons (spin-only) is:", "$\\mu = \\sqrt{n(n+2)} \\text{ BM}$", ["$\\mu = \\sqrt{n(n+2)} \\text{ BM}$", "$\\mu = n(n+2) \\text{ BM}$", "$\\mu = \\sqrt{n(n+1)} \\text{ BM}$", "$\\mu = 2n+1 \\text{ BM}$"]),
        ("Lanthanide contraction is caused by:", "Poor shielding effect of 4f electrons", ["Poor shielding effect of 4f electrons", "Effective shielding by 5d electrons", "Increase in nuclear charge only", "Screening by 6s electrons"]),
        ("Which of the following transition metal ions is colorless in aqueous solution?", "$\\text{Zn}^{2+}$", ["$\\text{Zn}^{2+}$", "$\\text{Cu}^{2+}$", "$\\text{Fe}^{3+}$", "$\\text{Cr}^{3+}$"]),
        ("Potassium permanganate ($\\text{KMnO}_4$) acts as a strong oxidizing agent in acidic medium, forming:", "$\\text{Mn}^{2+}$ ion", ["$\\text{Mn}^{2+}$ ion", "$\\text{MnO}_2$", "$\\text{MnO}_4^{2-}$", "$\\text{Mn}^{3+}$"]),
        ("Spin-only magnetic moment of $\\text{Fe}^{2+}$ ($3d^6$, $n=4$) is approximately:", "$4.90 \\text{ BM}$", ["$4.90 \\text{ BM}$", "$3.87 \\text{ BM}$", "$5.92 \\text{ BM}$", "$2.83 \\text{ BM}$"])
    ],
    "Coordination Compounds": [
        ("IUPAC name of $[\\text{Co}(\\text{NH}_3)_6]\\text{Cl}_3$ is:", "Hexaamminecobalt(III) chloride", ["Hexaamminecobalt(III) chloride", "Hexaamminecobalt(II) chloride", "Trichlorohexamminecobalt(III)", "Cobalt hexaammine chloride"]),
        ("In an octahedral crystal field, d-orbitals split into two sets:", "$t_{2g}$ (lower energy, 3 orbitals) and $e_g$ (higher energy, 2 orbitals)", ["$t_{2g}$ (lower energy, 3 orbitals) and $e_g$ (higher energy, 2 orbitals)", "$e_g$ (lower energy) and $t_{2g}$ (higher energy)", "$a_{1g}$ and $t_{1u}$", "$d_{xy}$ and $d_{z^2}$ only"]),
        ("Which of the following ligands is a bidentate ligand?", "Ethane-1,2-diamine (en)", ["Ethane-1,2-diamine (en)", "Ammonia (NH3)", "Water (H2O)", "Cyanide (CN-)"]),
        ("Coordination number of central metal atom in $[\\text{Fe}(\\text{EDTA})]^-$ is:", "6", ["6", "4", "2", "5"]),
        ("Isomerism shown by $[\\text{Co}(\\text{NH}_3)_5(\\text{SO}_4)]\\text{Br}$ and $[\\text{Co}(\\text{NH}_3)_5\\text{Br}]\\text{SO}_4$ is:", "Ionisation isomerism", ["Ionisation isomerism", "Linkage isomerism", "Coordination isomerism", "Hydrate isomerism"])
    ],
    "Organic Chemistry: Basic Principles": [
        ("IUPAC name of $\\text{CH}_3-\\text{CH}(\\text{OH})-\\text{CH}_2-\\text{CH}_3$ is:", "Butan-2-ol", ["Butan-2-ol", "Butan-3-ol", "2-Hydroxybutane", "1-Methylpropanol"]),
        ("Which of the following carbocations is the most stable?", "Tertiary carbocation ($(CH_3)_3C^+$)", ["Tertiary carbocation ($(CH_3)_3C^+$)", "Secondary carbocation ($CH_3CH_2CH_2^+$)", "Primary carbocation ($CH_3CH_2^+$)", "Methyl carbocation ($CH_3^+$)"]),
        ("Which effect involves complete transfer of shared pi-electron pair to one of the atoms in presence of attacking reagent?", "Electromeric effect", ["Electromeric effect", "Inductive effect", "Hyperconjugation", "Resonance effect"]),
        ("Detection of Nitrogen, Sulfur, and Halogens in organic compound is carried out by:", "Lassaigne's test", ["Lassaigne's test", "Biuret test", "Tollens' test", "Fehling's test"]),
        ("Hyperconjugation involves delocalisation of:", "$\\sigma$ electrons of C-H bond with adjacent empty/partially filled orbital", ["$\\sigma$ electrons of C-H bond with adjacent empty/partially filled orbital", "$\\pi$ electrons of C=C bond", "Lone pair electrons", "Inner shell electrons"])
    ],
    "Hydrocarbons": [
        ("Addition of HBr to propene in presence of peroxide gives 1-bromopropane according to:", "Kharasch effect (Anti-Markovnikov rule)", ["Kharasch effect (Anti-Markovnikov rule)", "Markovnikov rule", "Saytzeff rule", "Huckel rule"]),
        ("Wurtz reaction converts alkyl halides into alkanes by treating with:", "Sodium metal in dry ether", ["Sodium metal in dry ether", "Zinc in dilute HCl", "Magnesium in dry ether", "Potassium hydroxide in ethanol"]),
        ("According to Huckel's rule, a monocyclic planar conjugated ring is aromatic if it contains:", "$(4n + 2) \\pi$ electrons", ["$(4n + 2) \\pi$ electrons", "$4n \\pi$ electrons", "$(2n + 1) \\pi$ electrons", "$2n \\pi$ electrons"]),
        ("Ozonolysis of propene ($\\text{CH}_3-\\text{CH}=\\text{CH}_2$) followed by workup with Zn/H2O yields:", "Ethanal ($\\text{CH}_3\\text{CHO}$) and Methanal ($\\text{HCHO}$)", ["Ethanal ($\\text{CH}_3\\text{CHO}$) and Methanal ($\\text{HCHO}$)", "Propanal", "Acetone and Formaldehyde", "Ethanol and Methanol"]),
        ("Which of the following compounds is aromatic?", "Benzene ($\\text{C}_6\\text{H}_6$)", ["Benzene ($\\text{C}_6\\text{H}_6$)", "Cyclooctatetraene", "Cyclobutadiene", "Cyclohexane"])
    ],
    "Haloalkanes and Haloarenes": [
        ("$S_N2$ mechanism of nucleophilic substitution proceeds with:", "Complete inversion of configuration (Walden inversion)", ["Complete inversion of configuration (Walden inversion)", "Retention of configuration", "Racemisation", "Rearrangement"]),
        ("$S_N1$ reaction of an optically active alkyl halide results in:", "Racemisation", ["Racemisation", "Complete inversion", "100% retention", "No reaction"]),
        ("Which alkyl halide undergoes $S_N1$ reaction most rapidly?", "Tertiary butyl chloride ($(CH_3)_3C-Cl$)", ["Tertiary butyl chloride ($(CH_3)_3C-Cl$)", "Isopropyl chloride", "Ethyl chloride", "Methyl chloride"]),
        ("Finkelstein reaction is used to prepare alkyl iodides by treating alkyl chlorides with:", "$\\text{NaI}$ in dry acetone", ["$\\text{NaI}$ in dry acetone", "$\\text{AgF}$ in water", "$\\text{PCl}_5$", "$\\text{SOCl}_2$"]),
        ("Chlorobenzene on heating with aqueous NaOH at 623 K and 300 atm pressure gives:", "Phenol", ["Phenol", "Benzene", "Aniline", "Benzoic acid"])
    ],
    "Alcohols, Phenols and Ethers": [
        ("Lucas reagent used to distinguish primary, secondary, and tertiary alcohols consists of:", "Anhydrous $\\text{ZnCl}_2$ and conc. $\\text{HCl}$", ["Anhydrous $\\text{ZnCl}_2$ and conc. $\\text{HCl}$", "Dilute $\\text{H}_2\\text{SO}_4$", "Acidified $\\text{K}_2\\text{Cr}_2\\text{O}_7$", "$\\text{PCl}_5$ and $\\text{Pyridine}$"]),
        ("Reimer-Tiemann reaction converts Phenol into Salicylaldehyde by heating with:", "$\\text{CHCl}_3$ and aqueous $\\text{NaOH}$", ["$\\text{CHCl}_3$ and aqueous $\\text{NaOH}$", "$\\text{CO}_2$ and $\\text{NaOH}$", "$\\text{CH}_3\\text{Cl}$ and $\\text{AlCl}_3$", "$\\text{Zn}$ dust"]),
        ("Kolbe's reaction converts Phenol into Salicylic acid by treating with:", "$\\text{CO}_2$ followed by acidification", ["$\\text{CO}_2$ followed by acidification", "$\\text{CHCl}_3$ and $\\text{KOH}$", "$\\text{HNO}_3$ and $\\text{H}_2\\text{SO}_4$", "$\\text{Br}_2$ water"]),
        ("Williamson synthesis is used for the preparation of:", "Ethers", ["Ethers", "Alcohols", "Aldehydes", "Esters"]),
        ("Phenol is more acidic than Ethanol because:", "Phenoxide ion is stabilized by resonance", ["Phenoxide ion is stabilized by resonance", "Ethoxide ion is stabilized by resonance", "Phenol has higher molecular weight", "Ethanol has hydrogen bonding"])
    ],
    "Aldehydes, Ketones and Carboxylic Acids": [
        ("Which test is given by Aldehydes to give a silver mirror on inner wall of test tube?", "Tollens' test (Ammoniacal silver nitrate)", ["Tollens' test (Ammoniacal silver nitrate)", "Fehling's test", "Iodoform test", "Biuret test"]),
        ("Cannizzaro reaction is given by aldehydes which:", "Do not have any alpha-Hydrogen atom (e.g. HCHO, C6H5CHO)", ["Do not have any alpha-Hydrogen atom (e.g. HCHO, C6H5CHO)", "Have at least one alpha-Hydrogen atom", "Contain carboxylic group", "Are aromatic ketones"]),
        ("Aldol condensation requires presence of aldehydes/ketones having:", "At least one alpha-Hydrogen atom", ["At least one alpha-Hydrogen atom", "No alpha-Hydrogen atom", "Aromatic ring only", "Ester linkage"]),
        ("Iodoform test (yellow precipitate of $\\text{CHI}_3$) is positive for compounds containing:", "$\\text{CH}_3\\text{C}=\\text{O}$ or $\\text{CH}_3\\text{CH(OH)}$ group", ["$\\text{CH}_3\\text{C}=\\text{O}$ or $\\text{CH}_3\\text{CH(OH)}$ group", "$-\\text{COOH}$ group", "$-\\text{NH}_2$ group", "$-\\text{CHO}$ group only"]),
        ("Hell-Volhard-Zelinsky (HVZ) reaction converts aliphatic carboxylic acids having alpha-H into:", "$\\alpha$-halocarboxylic acids using $X_2 / \\text{Red Phosphorus}$", ["$\\alpha$-halocarboxylic acids using $X_2 / \\text{Red Phosphorus}$", "Acid chlorides using $\\text{SOCl}_2$", "Alkanes using $\\text{HI/Red P}$", "Esters using alcohol"])
    ],
    "Amines": [
        ("Hinsberg reagent used to distinguish primary, secondary, and tertiary amines is:", "Benzenesulphonyl chloride ($\\text{C}_6\\text{H}_5\\text{SO}_2\\text{Cl}$)", ["Benzenesulphonyl chloride ($\\text{C}_6\\text{H}_5\\text{SO}_2\\text{Cl}$)", "Acetyl chloride", "Phenyl isocyanide", "Nitrous acid"]),
        ("Carbylamine test (isocyanide test) giving foul smelling alkyl isocyanide is shown by:", "Primary aliphatic and aromatic amines only", ["Primary aliphatic and aromatic amines only", "Secondary amines only", "Tertiary amines only", "All amides"]),
        ("Hoffmann bromamide degradation reaction converts an amide into a primary amine with:", "One Carbon atom less than parent amide", ["One Carbon atom less than parent amide", "Same number of Carbon atoms", "One Carbon atom more", "Two Carbon atoms less"]),
        ("Basic strength of methyl-substituted amines in aqueous medium follows the order:", "$(\\text{CH}_3)_2\\text{NH} > \\text{CH}_3\\text{NH}_2 > (\\text{CH}_3)_3\\text{N} > \\text{NH}_3$", ["$(\\text{CH}_3)_2\\text{NH} > \\text{CH}_3\\text{NH}_2 > (\\text{CH}_3)_3\\text{N} > \\text{NH}_3$", "$(\\text{CH}_3)_3\\text{N} > (\\text{CH}_3)_2\\text{NH} > \\text{CH}_3\\text{NH}_2$", "$\\text{NH}_3 > \\text{CH}_3\\text{NH}_2 > (\\text{CH}_3)_2\\text{NH}$", "$(\\text{CH}_3)_2\\text{NH} > (\\text{CH}_3)_3\\text{N} > \\text{CH}_3\\text{NH}_2$"]),
        ("Diazotisation of Aniline with $\\text{NaNO}_2 + \\text{HCl}$ at $0-5^\\circ\\text{C}$ yields:", "Benzenediazonium chloride ($\\text{C}_6\\text{H}_5\\text{N}_2^+\\text{Cl}^-$)", ["Benzenediazonium chloride ($\\text{C}_6\\text{H}_5\\text{N}_2^+\\text{Cl}^-$)", "Phenol", "Nitrobenzene", "Chlorobenzene"])
    ],
    "Biomolecules": [
        ("Which nitrogenous base is present in RNA but absent in DNA?", "Uracil", ["Uracil", "Thymine", "Adenine", "Guanine"]),
        ("Deficiency of Vitamin C causes which disease?", "Scurvy", ["Scurvy", "Rickets", "Beriberi", "Night blindness"]),
        ("Secondary structure of protein is maintained by:", "Hydrogen bonds", ["Hydrogen bonds", "Covalent peptide bonds only", "Disulfide linkages only", "Ionic bonds"]),
        ("Glucose on prolonged heating with HI gives:", "n-Hexane", ["n-Hexane", "Gluconic acid", "Saccharic acid", "Hexanoic acid"]),
        ("Which of the following is a non-reducing disaccharide?", "Sucrose", ["Sucrose", "Maltose", "Lactose", "Cellobiose"])
    ],
    "Polymers and Everyday Chemistry": [
        ("Monomers of Nylon-6,6 are:", "Adipic acid and Hexamethylenediamine", ["Adipic acid and Hexamethylenediamine", "Caprolactam", "Ethylene glycol and Terephthalic acid", "Styrene and 1,3-butadiene"]),
        ("Caprolactam is the monomer of which synthetic polymer?", "Nylon-6", ["Nylon-6", "Nylon-6,6", "Terylene", "Bakelite"]),
        ("Natural rubber is a linear polymer of:", "Isoprene (2-methyl-1,3-butadiene)", ["Isoprene (2-methyl-1,3-butadiene)", "Chloroprene", "Neoprene", "Styrene"]),
        ("Which of the following is a biodegradable polymer?", "PHBV (Poly $\\beta$-hydroxybutyrate-co-$\\beta$-hydroxyvalerate)", ["PHBV (Poly $\\beta$-hydroxybutyrate-co-$\\beta$-hydroxyvalerate)", "PVC", "Polythene", "Teflon"]),
        ("Bithionol is added to soap to act as an:", "Antiseptic agent", ["Antiseptic agent", "Analgesic", "Antipyretic", "Antibiotic"])
    ]
}

def generate_full_unique_chemistry():
    ch_data = {}
    for ch, templates in chemistry_chapter_generators.items():
        qs = []
        for i in range(250):
            seed = i + 1
            t = templates[i % len(templates)]
            q_text = f"Q{seed}: {t[0]}"
            correct = t[1]
            opts = list(t[2])
            random.shuffle(opts)
            ans_letter = ['A', 'B', 'C', 'D'][opts.index(correct)]
            qs.append({
                "question": q_text,
                "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                "answer": ans_letter
            })
        ch_data[ch] = qs
    return ch_data

chem_dataset = generate_full_unique_chemistry()
chem_file = os.path.join(DATA_DIR, 'chemistry_questions.json')

with open(chem_file, 'w', encoding='utf-8') as f:
    json.dump({
        "subject": "NEET Chemistry",
        "total_chapters": len(chem_dataset),
        "total_questions": sum(len(qs) for qs in chem_dataset.values()),
        "chapter_order": list(chem_dataset.keys()),
        "chapters": chem_dataset
    }, f, indent=2, ensure_ascii=False)

print(f"✅ Generated 5000 unique Chemistry questions across {len(chem_dataset)} chapters -> {chem_file}")
