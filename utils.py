import awkward as ak

def select_muons(events):
    mu = events.Muon
    base = (mu.pt > 5) & (abs(mu.eta) < 2.4)
    # can be updated with different WP etc.
    return mu[base & mu.mediumId & (mu.pfRelIso04_all < 0.25)]

def select_electrons(events):
    el = events.Electron
    base = (el.pt > 7) & (abs(el.eta) < 2.5)
    # can be updated with different WP etc.
    return el[base & (el.cutBased >= 3)]

Z_MASS = 91.1876
Z_CANDIDATE_MASS_MIN = 12.0
Z_CANDIDATE_MASS_MAX = 120.0
FOUR_LEPTON_MASS_MIN = 70.0

def make_Z_candidates(leptons):

    # make all possible Z boson combinations
    pair = ak.combinations(leptons, 2, fields=["l1", "l2"])
    opp_charge = (pair.l1.charge != pair.l2.charge)
    mass = (pair.l1 + pair.l2).mass
    z_mask = opp_charge & (mass > Z_CANDIDATE_MASS_MIN) & (mass < Z_CANDIDATE_MASS_MAX)
    return pair[z_mask]
