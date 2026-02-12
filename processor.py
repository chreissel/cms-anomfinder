from coffea import processor
from coffea.analysis_tools import PackedSelection
import awkward as ak
import hist
from utils import *
import dask_awkward as dak
import dask
from coffea.processor import column_accumulator
import correctionlib
from coffea.analysis_tools import Weights

class MyProcessor(processor.ProcessorABC):
    def __init__(self, corrections: str):
        self.cset = {
                'MUO': correctionlib.CorrectionSet.from_file(corrections + '/MUO/2016postVFP_UL/muon_JPsi.json'),
                'LUM': correctionlib.CorrectionSet.from_file(corrections + '/LUM/2016postVFP_UL/puWeights.json')
        }

        self.sf = {
            'muon_id' : self.cset['MUO']['NUM_MediumID_DEN_TrackerMuons'],
            'pu_weight': self.cset['LUM']['Collisions16_UltraLegacy_goldenJSON']
        }

    def process(self, events):

        isMC = events.metadata["isMC"]
        dataset = events.metadata["dataset"]
        
        # event filtering and triggers
        flags = (events.Flag.goodVertices & events.Flag.globalSuperTightHalo2016Filter & events.Flag.HBHENoiseFilter & events.Flag.HBHENoiseIsoFilter & events.Flag.EcalDeadCellTriggerPrimitiveFilter & events.Flag.BadPFMuonFilter & events.Flag.BadChargedCandidateFilter & events.Flag.ecalBadCalibFilter)
        if not isMC:
            flags = flags & events.Flag.eeBadScFilter
        # triggers = (events.HLT.IsoMu24 | events.HLT.IsoTkMu24) # we cannot use the triggers below since Open Data does not provide SF for them!
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
        selected_muons = muons[cut]

        # apply corrections & systematic uncertainties
        weights = Weights(len(selected_events))
        if isMC:
            weights.add('genWeight', selected_events.genWeight)
            weights.add('puWeight', 
                        weight = self.sf['pu_weight'].evaluate(selected_events.Pileup.nTrueInt, 'nominal'),
                        weightUp = self.sf['pu_weight'].evaluate(selected_events.Pileup.nTrueInt, 'up'), 
                        weightDown = self.sf['pu_weight'].evaluate(selected_events.Pileup.nTrueInt, 'down')
                       )
            weights.add('muonId', 
                        weight = ak.prod(self.sf['muon_id'].evaluate(selected_muons.eta, selected_muons.pt, 'nominal'), axis=1),
                        weightUp = ak.prod(self.sf['muon_id'].evaluate(selected_muons.eta, selected_muons.pt, 'systup'), axis=1),
                        weightDown = ak.prod(self.sf['muon_id'].evaluate(selected_muons.eta, selected_muons.pt, 'systdown'), axis=1)
                       )
        
        # inputs for ML starting here
        variables = {
                        "event": selected_events.event,
                        "run": selected_events.run,
                        "luminosityBlock": selected_events.luminosityBlock,
        }
        if isMC:
               variables["weight"] =  ak.Array(weights.weight())
        # add the selected muon kinematics
        for i in range(4):
            variables[f"pt{i}"] = selected_muons.pt[:,i]
            variables[f"eta{i}"] = selected_muons.eta[:,i]
            variables[f"phi{i}"] = selected_muons.phi[:,i]
            variables[f"pdgId{i}"] = selected_muons.pdgId[:,i]
            # displacement variables
            variables[f"dz{i}"] = selected_muons.dz[:,i]
            variables[f"dxy{i}"] = selected_muons.dxy[:,i]

        array = ak.zip(variables, depth_limit=1)
        clean_array = ak.Array(array.layout)

        return {
            dataset: {
                "cutflow": {"all": len(events), "selected": len(events[cut])}, 
                "array": column_accumulator(clean_array)
            }
        }

    def postprocess(self, accumulator):
        return accumulator
