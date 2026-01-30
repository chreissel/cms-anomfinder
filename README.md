# Anomalous Detection Framework for New Physics

This repository contains an **anomaly detection framework** for searches of new physics in **high-energy collider data**, using CMS Open Data in the NanoAOD format. The framework is currently in **early testing stages** and focuses on building a scalable analysis pipeline that can later be extended.

## 1. Setup
Create a Python environment using the provided `env.yml` file. This environment ensures that all required packages for the analysis pipeline are available, including [`coffea`](https://coffeateam.github.io/coffea/), [`hist`](https://hist.readthedocs.io/) and `XRootD` (for downloading CMS Open Data)

```bash
conda env create -f env.yml
conda activate cms-anomfinder
```

## 2. Data Access
The framework uses **CMS Open Data (NanoAOD)** as input. The full CMS Open Data NanoAOD dataset can be found here:
- https://opendata.cern.ch/search?q=&f=experiment%3ACMS&f=file_type%3Ananoaod

### Recommended Test Datasets
Since the framework is currently under development, we recommend starting with two test files: **Data**: DoubleMuon, 2016 Run H, **Simulation**: `ZZTo4L`.

#### Example Download Instructions

```bash
mkdir data
cd data
# Data sample
xrdcp root://eospublic.cern.ch//eos/opendata/cms/Run2016H/DoubleMuon/NANOAOD/UL2016_MiniAODv2_NanoAODv9-v1/2510000/127C2975-1B1C-A046-AABF-62B77E757A86.root .
# Simulation sample
xrdcp root://eospublic.cern.ch//eos/opendata/cms/mc/RunIISummer20UL16NanoAODv9/ZZTo4L_TuneCP5_13TeV_powheg_pythia8/NANOAODSIM/106X_mcRun2_asymptotic_v17-v1/2430000/051E9D22-4F30-8E49-8477-644E65768282.root .
```

## 3. Analysis Pipeline
The analysis workflow is built around a **coffea processor** that applies object and event selection. Key components can be found in the following files:
- `processor.py`: Implements the main analysis logic
- `utils.py`: Provides helper functions used throughout the pipeline

At present, the analysis is executed through a **Jupyter notebook** interface to be found in `FirstTry.ipynb`

## Where do we stand? 
We are in early testing stages. The code is able to run basic object and event selection. Importent next steps are:
- Save analysis outputs to **Parquet files** for downstream machine learning workflows
- Include **systematic uncertainties** for simulation and propagate them through the pipeline
- Scale the workflow to the **full 2016 Run 2 dataset**, including:
  - All available data
  - Relevant simulation backgrounds
  - Potential signal samples for validation and testing

---
