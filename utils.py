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

def make_lepton_pair(leptons):
    pair = ak.combinations(leptons, 2, fields=["l1", "l2"])
    pair = pair[pair.l1.charge != pair.l2.charge]
    num_pair = ak.num(pair)
    return pair, num_pair
