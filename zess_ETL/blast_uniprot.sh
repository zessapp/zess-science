# Ensure Docker is installed and the latest BLAST image is present

## Create directories for analysis
cd ; mkdir blastdb queries fasta results blastdb_custom
cp $HOME/Zess_science_data/Proteins/uniprotkb_allergenome_fasta/uniprotkb_allergenome_fasta.fa.gz fasta/
gzip -d fasta/uniprotkb_allergenome_fasta.fa.gz
rm fasta/uniprotkb_allergenome_fasta.fa.gz

cp $HOME/Zess_science_data/Allergens/allergen_online.fa queries/

## Step 1 - Create the BLAST database using allergenome
docker run --rm \
    -v $HOME/blastdb_custom:/blast/blastdb_custom:rw \
    -v $HOME/fasta:/blast/fasta:ro \
    -w /blast/blastdb_custom \
    ncbi/blast \
    makeblastdb -in /blast/fasta/uniprotkb_allergenome_fasta.fa -dbtype prot \
    -parse_seqids -out uniprot-allergenome-proteins -title "uniprot allergenome proteins" \
    -blastdb_version 5

## Step 2. Run BLAST+
docker run --rm \
    -v $HOME/blastdb:/blast/blastdb:ro \
    -v $HOME/blastdb_custom:/blast/blastdb_custom:ro \
    -v $HOME/queries:/blast/queries:ro \
    -v $HOME/results:/blast/results:rw \
    ncbi/blast \
    blastp -query /blast/queries/allergen_online.fa -db uniprot-allergenome-proteins \
      -max_target_seqs 5 -num_threads 4 -outfmt 6 \
      -out /blast/results/allergenOnline_blast.txt

cp results/allergenOnline_blast.txt $HOME/Zess_science_data/Allergens/

# Step 3. Tidy up
rm -rf blastdb queries fasta results blastdb_custom
## Finished
