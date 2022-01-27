import pandas as pd
import sys
import subprocess

def main(base_dir, blast_df):
    sh_cmd = f'time {base_dir}/blast_uniprot.sh'
    output = subprocess.run(sh_cmd.split(), capture_output=True)
    print(f'Finished running blast with output\n\n{output}\n\n')

    # Load the blast output with header as shown below
    header = ['qseqid','sseqid','pident','length','mismatch','gapopen','qstart',
    'qend','sstart','send','evalue','bitscore']
    blast_df.columns = header
    blast_df = blast_df.groupby('qseqid').head(3) # Top 3 hits
    return blast_df
