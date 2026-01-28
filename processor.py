from coffea import processor
import awkward as ak
import hist
from utils import *

class MyProcessor(processor.ProcessorABC):
    def __init__(self):
        self._accumulator = {
            "events": processor.defaultdict_accumulator(int),
            "nMuons": hist.Hist(
                hist.axis.Integer(0, 10, name="nMuons", label="Number of muons"),
                storage=hist.storage.Weight(),
                ),
        }

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, events):
        out = {
            "events": processor.defaultdict_accumulator(int),
            "nMuons": hist.Hist(
                hist.axis.Integer(0, 10, name="nMuons", label="Number of muons"),
                storage=hist.storage.Weight(),
                )
        }

        out["events"]["all"] += len(events)

        # event filtering and triggers are missing!
        # all MC/data corrections are missing!

        # needs reasonable event selection & reconstruction HERE!
        muons = select_muons(events)
        n_muons = ak.num(muons)
        out["nMuons"].fill(nMuons=n_muons)

        return out

    def postprocess(self, accumulator):
        return accumulator
