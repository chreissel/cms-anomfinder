# Anomalous Detection Framework for New Physics

This repository provides an **anomaly detection** framework for searches for new physics in high-energy collider data, based on CMS Open Data in the NanoAOD format. The project is currently in an **early testing** phase and focuses on developing a scalable and modular analysis pipeline that can be extended in future iterations.

At present, the repository contains the core analysis code. It will soon be expanded to include additional components, such as machine-learning–based data compression and statistical inference modules.

## 1. Setup
We recommend running the analysis on the CERN lxplus server. To do so, you must register for a CERN account first. Next, we suggest installing miniforge as described [here](https://abpcomputing.web.cern.ch/guides/python_inst/). After that, create a Python environment using the provided `env.yml` file. This environment ensures that all required packages for the analysis pipeline are available, including [`coffea`](https://coffeateam.github.io/coffea/), [`hist`](https://hist.readthedocs.io/) and `XRootD` (for downloading CMS Open Data)

```bash
conda env create -f env.yml
conda activate cms-anomfinder
```

## 2. Data Access
The framework uses **CMS Open Data (NanoAOD)** as input. The full CMS Open Data NanoAOD dataset can be found here:
- https://opendata.cern.ch/search?q=&f=experiment%3ACMS&f=file_type%3Ananoaod
  
When running on the lxplus server, the CMS Open Data is available locally and will be loaded directly from the CERN storage system.

The `datasets/` directory contains configuration files that point to the corresponding data locations. You can add additional signal, background, or data samples by including new entries in this folder.

If you are unable or prefer not to run on lxplus, the dataset can also be downloaded manually. An example is provided below.

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
- `utils.py`: Provides helper functions used throughout the pipeline, for example for object selection
- `main.py`: Serves as the entry point to run the analysis. It loads datasets, sets up the chosen executor (local or Dask on lxplus), runs the processor, and saves results to Parquet files.

`main.py` provides several command-line options:

| Option | Description |
|--------|-------------|
| `--datasets` | Names of datasets to process (required). If multiple are provided, all are processed. |
| `--executor` | Executor type: `iterative` (local) or `dask-lxplus` (CERN lxplus cluster). Default: `iterative`. |
| `--workers` | Number of Dask workers (default: 4). |
| `--max-files` | Maximum number of files to process per dataset (useful for testing). |
| `--output-dir` | Directory where Parquet output files are saved (default: `./results/`). |

### Example Usage

Run the analysis locally on a subset of datasets:
```bash
python main.py --datasets ZZTo4L_TuneCP5_13TeV_powheg_pythia8 TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8 --executor iterative --max-files 10 
```
Run the analysis on the CERN lxplus cluster using dask:
```bash
python main.py --datasets ZZTo4L_TuneCP5_13TeV_powheg_pythia8 TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8 --executor dask-lxplus --workers 8 
```

## Where do we stand? 
Here’s a polished Markdown version suitable for a GitHub README, keeping the task list format and making it clear and readable:

## Current Status and Next Steps

This project is currently in **early testing stages**. The code is able to perform basic object and event selection, and the overall infrastructure is able to scale to larger datasets.  

The next phase of development will focus on refining object selection, implementing potential systematic uncertainties, and applying necessary corrections.

- [ ] Scale the workflow to the **full 2016 Run 2 dataset**, including:
  - [ ] All available data
  - [x] Relevant simulation backgrounds
  - [ ] Potential signal samples for validation and testing
- [ ] Include electron decay channels
- [ ] Incorporate jets to improve background suppression
- [ ] Add systematic effects, particularly lepton energy smearing
