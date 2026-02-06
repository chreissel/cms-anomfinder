import argparse
import json
from pathlib import Path
from coffea import processor
from coffea.nanoevents import NanoAODSchema
import awkward as ak
import hist
from processor import MyProcessor


def parse_args():
    parser = argparse.ArgumentParser(
        description='Run Coffea processor on CMS open data to prepare for downstream anomaly task'
    )
    parser.add_argument(
        '--datasets',
        type=str,
        nargs='+',  
        required=True,
        help='Name of datasets to be processed, if all process all datasets in the folder!'
    )
    parser.add_argument(
        '--executor',
        type=str,
        choices=['dask-lxplus', 'iterative'],
        default='iterative',
        help='Executor type: iterative (local tests), dask-lxplus (LXPLUS cluster)'
    )
    # Dask-specific options
    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of workers for dask (default: 4)'
    )
    parser.add_argument(
        '--max-files',
        type=int,
        default=None,
        help='Maximum number of files to process (for testing)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./results/',
        help='Output directory for parquet files (default: results/)'
    ) 
    return parser.parse_args()


def load_fileset(dataset_path, max_files=None):
    with open(dataset_path, 'r') as f:
        fileset = json.load(f)
    
    # Limit number of files if specified
    if max_files is not None:
        for dataset_name in fileset:
            if 'files' in fileset[dataset_name]:
                files = fileset[dataset_name]['files']
                limited_files = dict(list(files.items())[:max_files])
                fileset[dataset_name]['files'] = limited_files
    
    return fileset


def get_executor(executor_type, workers=4):
    if executor_type == 'iterative':
        return processor.IterativeExecutor()
    
    elif executor_type == 'dask-lxplus':
        print('wrong path') 
    else:
        raise ValueError(f"Unknown executor type: {executor_type}")

def save_to_parquet(result, output_path, compression='snappy'):
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving results to: {output_path}")
    
    for dataset_name in result.keys():
        output_file = output_path / f"{dataset_name}.parquet"
        data = result[dataset_name]['array'].value
        ak.to_parquet(
                data,
                output_file,
                compression=compression,
                extensionarray=False
            )
        print(f"Saved {dataset_name}: {output_file} ({len(data)} events)")

def main():
    args = parse_args()

    # Prepare Dataset
    fileset = {}
    for d in args.datasets:
        print(f"Loading datasets: {args.datasets}")
        fileset.update(load_fileset('./dataset/'+d+'.json', max_files=args.max_files))
   
    # Setup executor
    print(f"Using executor: {args.executor}")
    if args.executor == 'dask-lxplus':
        print(f"Number of workers: {args.workers}")
    executor = get_executor(args.executor, workers=args.workers)
    
    runner = processor.Runner(
        executor=executor,
        schema=NanoAODSchema,
        savemetrics=True,
    )
   
    # Run the processor
    print("Starting processing...")
    result, metrics = runner(
        fileset,
        processor_instance=MyProcessor(corrections='./data/corrections/POG/')
    )

    # Save results to parquet
    output_path = Path(args.output_dir)
    save_to_parquet(result, output_path)

    print("Processing complete!")
    print(f"Metrics: {metrics}")
    
    return result, metrics

if __name__ == '__main__':
    result, metrics = main()
