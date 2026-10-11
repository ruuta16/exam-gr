# nosaukums → (periodu skaits, labākais zināmais rezultāts)
# mazajiem None — optimumu rēķina exact.py
SMALL = {
    "mazs_06": (5, None),
    "mazs_09": (6, None),
    "mazs_12": (8, None),
}

# Toronto versija I: https://people.cs.nott.ac.uk/pszrq/data.htm
# labākie zināmie: arXiv:2201.07525, 9. tabula. pur93 šai versijai nav publicēts.
TORONTO = {
    "hec92": (18, 10.03),
    "sta83": (13, 156.86),
    "yor83": (21, 34.40),
    "ute92": (10, 24.76),
    "ear83": (24, 32.42),
    "tre92": (23, 7.59),
    "lse91": (18, 9.77),
    "kfu93": (20, 12.80),
    "rye93": (23, 7.84),
    "car92": (32, 3.64),
    "uta92": (35, 2.95),
    "car91": (35, 4.24),
    "pur93": (42, None),
}

INSTANCES = {**SMALL, **TORONTO}
