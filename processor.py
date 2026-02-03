from coffea import processor
from coffea.analysis_tools import PackedSelection
import awkward as ak
import hist
from utils import *
import dask_awkward as dak
import dask
from coffea.processor import column_accumulator

class MyProcessor(processor.ProcessorABC):
    def __init__(self):
        pass

    def process(self, events):

        isMC = events.metadata["isMC"]
        dataset = events.metadata["dataset"]
        
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
        cutflow = selc.cutflow("Filter", "Triggers", "Lepton selection")
        cut = selc.all()
       
        # save basic event identification & monitoring variables
        selected_events = events[cut]
        variables = {
                        "event": selected_events.event,
                        "run": selected_events.run,
                        "luminosityBlock": selected_events.luminosityBlock,
        }
        if isMC:
               variables["weight"] =  selected_events.genWeight
        # add the selected muon kinematics
        selected_muons = muons[cut]
        for i in range(4):
            variables[f"pt{i}"] = selected_muons.pt[:,i]
            variables[f"eta{i}"] = selected_muons.eta[:,i]
            variables[f"phi{i}"] = selected_muons.phi[:,i]
            variables[f"pdgId{i}"] = selected_muons.pdgId[:,i]
            # displacement variables
            variables[f"dz{i}"] = selected_muons.dz[:,i]
            variables[f"dxy{i}"] = selected_muons.dxy[:,i]

        
            
        return {
            dataset: {
                "cutflow": {"all": len(events), "selected": len(events[cut])}, 
                "array": column_accumulator(ak.zip(variables, depth_limit=1))
            }
        }

    def postprocess(self, accumulator):
        return accumulator