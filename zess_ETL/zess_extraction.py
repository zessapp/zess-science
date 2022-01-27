import pandas as pd
import sys
import os
import argparse
from datetime import datetime

# Relative path for me - './zess_science_pkg/Extraction/zess_science_pkg/' - this is for local ipython testing
# module_path = os.path.abspath(os.path.join('zess_ETL/'))
# if module_path not in sys.path:
#    sys.path.append(module_path)

from Extraction.zess_science_pkg.main_methods import module_allergen_db as allergen
from Extraction.zess_science_pkg.main_methods import module_downloads as download
from Extraction.zess_science_pkg.main_methods import module_directory as directory
from configs.dir_names import *
from configs.datasets_config import *


class Sources:
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])


def main(args):
    '''
        Executes extraction logic which either uses a simple wget download module, or utilises bs4 for web scraping.
        Requires user-args as defined when running python3 zess_extraction.py --help
    '''
    start_time = datetime.now()

    # N.B. DrugBank requires a commercial license to use commercially; therefore ommitted for now
    # Ommitting or not downloading haptens as databases appear unmaintained and cannot verify
    s = Sources({
                    "allergen_online": 'http://www.allergenonline.org/databasebrowse.shtml',
                    "allerbase": 'http://196.1.114.46:1800/AllerBase/PHP_codes/Query_OutPut/Output.txt',
                    "gwas_catalog": "ftp://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-catalog-associations_ontology-annotated.tsv",
                    "drug_bank": "",
                    "int_act": "ftp://ftp.ebi.ac.uk/pub/databases/intact/current/psimitab/intact.zip",
                    "efo": "http://www.ebi.ac.uk/efo/efo.owl",
                    "omim": "https://data.omim.org/static/omim/data/mim2gene.txt",
                    "uniprotkb_allergenome_fasta": "https://www.uniprot.org/uniprot/?query=database:(type:allergome)&format=fasta&force=true&fil=reviewed:yes&compress=yes",
                    # "uniprot_all_allergenome_fasta": "https://www.uniprot.org/uniprot/?query=database:(type:Allergome)&format=fasta&force=true&compress=yes",
                    "uniprotkb_allergenome_all": "https://www.uniprot.org/uniprot/?query=database:(type:allergome)&format=xml&force=true&fil=reviewed:yes&compress=yes",
                    "go": "http://current.geneontology.org/annotations/goa_human.gaf.gz",
                    "pubmed": "",
                    "hpo": "https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/main/src/ontology/doid.owl",
                    "haptenDB": "",
                    "food_on": "https://raw.githubusercontent.com/FoodOntology/foodon/master/foodon.owl",
                    "usda": "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_csv_2020-04-29.zip",
                    "hgnc_mapping_ens": 'https://www.genenames.org/cgi-bin/download/custom?col=gd_app_sym&col=md_ensembl_id&status=Approved&hgnc_dbtag=on&order_by=gd_app_sym_sort&format=text&submit=submit'
                })



    # Create the folder structure - vars sourced from dir_names config
    main_dir = allergens, proteins, literature, genes, food, drug, disease, ontologies
    if args.make_directory:
        print('Creating the directory structure\n\n')
        directory.main(root_dir=root_dir, main_dir=main_dir, main_dir_names=main_dir_names)

    # ! This is non exhaustive and more datasets are to be added with additional modules! #

    # Gene datasets
    # Download GWAS catalog
    if args.gene_main:
        print('Fetching GWAS data\n\n')
        # Need a check to see if file already exists and to remove if so - then cont
        download.download_file(url=s.gwas_catalog, dir=f'{root_dir}/Genes/gwas_catalog/gwas-catalog-associations_ontology-annotated.tsv')

    if args.gene_mapping:
        print('Fetching gene mapping data\n\n')
        download.download_file(url=s.hgnc_mapping_ens, dir=f'{root_dir}/Genes/mapping/hgnc-ensembl.txt')

    # Protein datasets
    # Download IntAct, uniprotkb_allergenome, uniprot_all_allergenome
    if args.uniprot_main:
        print('Fetching main uniprot data\n\n')
        protein_dict = {'uniprotkb_allergenome_fasta' : [s.uniprotkb_allergenome_fasta, 'uniprotkb_allergenome_fasta.fa.gz'],
                        # 'uniprot_all_allergenome_fasta' : [s.uniprot_all_allergenome_fasta, 'uniprot_all_allergenome_fasta.fa.gz'],
                        'uniprotkb_allergenome_all' : [s.uniprotkb_allergenome_all, 'uniprotkb_allergenome_all.xml.gz']}
        [download.download_file(url=v[0], dir=f'{root_dir}/Proteins/{k}/{v[1]}') for k,v in protein_dict.items()]

    if args.ppi_main:
        print('Fetching intact PPI data\n\n')
        download.download_file(url=s.int_act, dir=f'{root_dir}/Proteins/int_act/intact.zip')

    # Ontology datasets
    if args.ont_general:
        print('Fetching general ontology data\n\n')
        ontology_dict = {'go':[s.go,'goa_human.gaf.gz'], 'hpo':[s.hpo,'hpo.owl'],
                        'efo':[s.efo,'efo.owl']}
        [download.download_file(url=v[0], dir=f'{root_dir}/Ontologies/{k}/{v[1]}') for k,v in ontology_dict.items()]

    if args.ont_food:
        print('Fetching food ontology data\n\n')
        download.download_file(url=s.food_on, dir=f'{root_dir}/Ontologies/food_on/foodon.owl')

    # Food datasets
    if args.food_usda:
        print('Fetching USDA data\n\n')
        food_n = download.download_file(url=s.usda, dir=f'{root_dir}/Food/usda/FoodData_central_csv.zip')
        os.rename(food_n, f'{root_dir}/Food/usda/FoodData_Central_csv.zip')

    # Disease datasets
    # While certain diseases can enhance risk, I am omitting this for now as it's too broad
    # if 'Disease' in mode:
    #     download.download_file(url=s.omim, dir=f'{root_dir}/Disease/omim/mim2gene.txt')

    # Allergy datasets
    if args.allergens:
        print('Fetching allergen data\n\n')
        allergen_df = allergen.scrape_allergendb((s.allergen_online))
        allergen_df.to_csv(f'{root_dir}/Allergens/allergen_online/allergen_online_db.txt', sep="\t", index=None)
        # For whatever reason, I can't get confrimational antibodies, so sequential will have to do until creating an epitope prediction pipeline (should we need that - low priority)
        download.download_file(url=s.allerbase, dir=f'{root_dir}/Allergens/allerbase/linear_epitopes.txt')
    print(f'\nZess Science extraction completed with duration: {datetime.now() - start_time}\n')


if __name__ == '__main__':
    # Create the parsers
    parser = argparse.ArgumentParser(description='Extraction for Zess Science data sources - pick your data source(s)\n\n')

    # Populate the arguments
    parser.add_argument(
                        '-mkdir', '--make_directory',
                        help='For local use: if this is your first time,\
                        selecting this option will enable the creation of a \
                        local directory structure as manually configured in the\
                        dirs section - your base directory will be\
                        $HOME/Zess_science_data/', required=False)
    parser.add_argument(
                        '-gmain', '--gene_main', help='Currently extracts GWAS\
                         catalog data', required=False,
                         default=False, action='store_true')
    parser.add_argument(
                        '-gmap', '--gene_mapping', help='Currently extracts\
                         HGNC-Ensembl mapping data', required=False,
                         default=False, action='store_true')
    parser.add_argument(
                        '-unimain', '--uniprot_main', help='Currently extracts\
                        uniprot(KB) fasta data & XML with publication links.',
                        required=False, default=False, action='store_true')
    parser.add_argument(
                        '-ppim', '--ppi_main', help='Currently extracts\
                        IntAct PPI data only.',
                        required=False, default=False, action='store_true')
    parser.add_argument(
                        '-ontg', '--ont_general', help='Currently extracts\
                        a range of ontology datasets in OWL format.',
                        required=False, default=False, action='store_true')
    parser.add_argument(
                        '-ontf', '--ont_food', help='Currently extracts\
                        the FoodOn ontology dataset (OWL).',
                        required=False, default=False, action='store_true')
    parser.add_argument(
                        '-fusda', '--food_usda', help='Currently extracts\
                        all USDA food data (uses food.csv).',
                        required=False, default=False, action='store_true')
    parser.add_argument(
                        '-a', '--allergens', help='Currently extracts\
                        allergenOnline & allerbase data',
                        required=False, default=False, action='store_true')

    args = parser.parse_args()


    main(args)
