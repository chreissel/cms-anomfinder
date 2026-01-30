from coffea import processor
from coffea.analysis_tools import PackedSelection
import awkward as ak
import hist
from utils import *

class MyProcessor(processor.ProcessorABC):
    def __init__(self):
        self._accumulator = {
            "events": processor.defaultdict_accumulator(int),
            "nLeptons": hist.Hist(
                hist.axis.Integer(0, 10, name="nLeptons", label="Number of leptons (muons)"),
                storage=hist.storage.Weight(),
                ),
        }

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, events):
        out = {
            "events": processor.defaultdict_accumulator(int),
            "nLeptons": hist.Hist(
                hist.axis.Integer(0, 10, name="nLeptons", label="Number of leptons (muons)"),
                storage=hist.storage.Weight(),
                ),
        }
        isMC = events.metadata["isMC"]
        out["events"]["all"] += len(events)

        # event filtering and triggers
        flags = (events.Flag.goodVertices & events.Flag.globalSuperTightHalo2016Filter & events.Flag.HBHENoiseFilter & events.Flag.HBHENoiseIsoFilter & events.Flag.EcalDeadCellTriggerPrimitiveFilter & events.Flag.BadPFMuonFilter & events.Flag.BadChargedCandidateFilter & events.Flag.ecalBadCalibFilter)
        if not isMC:
            flags = flags & events.Flag.eeBadScFilter
        triggers = (events.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL | events.HLT.Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL | events.HLT.TripleMu_12_10_5)
        # trigger vetos for electon channels missing!

        # simplified muon selection compared to CMS AN2016_442
        muons = select_muons(events)
        n_muons = ak.num(muons)

        # event selection
        selc = PackedSelection()
        selc.add_multiple(
                {
                    "Filter": flags,
                    "Triggers": triggers,
                    "Lepton selection":  (n_muons > 3),
                }
        )
        print(selc)
        cutflow = selc.cutflow("Filter", "Triggers", "Lepton selection")
        cutflow.print()
        cut = selc.all()
       
        out["nLeptons"].fill(nLeptons=n_muons)
        out["events"]["selected"] += len(events[cut])

        return out

    def postprocess(self, accumulator):
        return accumulator
