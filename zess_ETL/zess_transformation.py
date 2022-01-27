import argparse
import pandas as pd
import numpy as np
import os, sys
import zipfile
from datetime import datetime

# Relative path for me - './zess_science_pkg/Extraction/zess_science_pkg/' - this is for local ipython testing
# module_path = os.path.abspath(os.path.join('zess_ETL/'))
# if module_path not in sys.path:
#    sys.path.append(module_path)
# import warnings
# warnings.filterwarnings('ignore')

from configs.dir_names import *
from configs.allergen_list import *
from Transformation.main_methods import module_directory as directory
from Transformation.main_methods  import module_allergens as allergen_funcs
from Transformation.main_methods import module_gwas as gwas_funcs
from Transformation.main_methods import module_int_act as int_act_funcs
from Transformation.main_methods import module_usda as usda_funcs
from Transformation.main_methods import module_blast as blast_funcs

def main(args):

    start_time = datetime.now()

    append_dir = lambda value: [val + '/transformed/' for val in value]
    main_dir = append_dir(allergens), append_dir(proteins), append_dir(literature), \
               append_dir(genes), append_dir(food), append_dir(drug), \
               append_dir(disease), append_dir(ontologies)
    if args.make_directory:
        directory.main(root_dir=root_dir, main_dir=main_dir, main_dir_names=main_dir_names)


    # # ALLERGENS # #
    if args.allergens:
        print('Starting transformation for AllergenOnline data\n')
        # Transform allergenOnline db
        allergen_online_df = pd.read_csv(f'{root_dir}/Allergens/allergen_online/allergen_online_db.txt', sep="\t")
        allergen_online_df = allergen_funcs.allergen_online_filter(df=allergen_online_df, fa_out_dir=f'{root_dir}/Allergens/allergen_online.fa' )
        allergen_online_df.to_csv(f'{root_dir}/Allergens/allergen_online_transformed.tsv', sep="\t", index=None)
        print('Finished transformation for AllergenOnline data\n')
        # Import epitope data from allerbase
        print('Starting transformation for Allerbase data\n')
        allerbase_df = allergen_funcs.allerbase(f'{root_dir}/Allergens/allerbase/linear_epitopes.txt')
        allerbase_df.to_csv(f'{root_dir}/Allergens/allerbase_transformed.tsv', sep="\t", index=None)
        print('Finished transformation for Allerbase data\n')


    # # GENETIC DATA # #
    if args.gene:
        # GWAS data
        print('Starting transformation for GWAS data\n')
        food_allergy_gwas_df = gwas_funcs.main(dir=f'{root_dir}/Genes/gwas_catalog/gwas-catalog-associations_ontology-annotated.tsv', allergen_list=eu_allergens)
        food_allergy_gwas_df.to_csv(f'{root_dir}/Genes/gwas_catalog/gwas-catalog-food-allergies_transformed.tsv', sep='\t', index=None)
        print('Finished transformation for GWAS data\n')

    # # PROTEIN DATA # #
    if args.ppi_intact:
        try:
            print('Starting transformation for IntAct data\n')
            # Extract
            with zipfile.ZipFile(f'{root_dir}/Proteins/int_act/intact.zip') as zip_ref:
                zip_ref.extractall(f'{root_dir}/Proteins/int_act/')

            # Limit scope of what we want to see and reduce loading time (C vectorization on data column wise is slow)
            int_act_cols = ['#ID(s) interactor A', 'ID(s) interactor B',
            'Interaction detection method(s)', 'Publication Identifier(s)',
            'Interaction type(s)', 'Interaction identifier(s)',
            'Confidence value(s)', 'Taxid interactor A', 'Taxid interactor B']

            int_act_df = pd.read_csv(f'{root_dir}/Proteins/int_act/intact.txt', sep='\t',usecols=int_act_cols)
            allergen_online_df = pd.read_csv(f'{root_dir}/Allergens/allergen_online_transformed.tsv', sep="\t")

            int_act_df = int_act_funcs.main(int_act_df=int_act_df, allergen_online_df=allergen_online_df)
            int_act_df.to_csv(f'{root_dir}/Proteins/int_act/intact_transformed.txt', sep='\t',index=None)
            print('Finished transformation for IntAct data\n')
        except Exception as e:
            print(f'Error with transforming IntAct data due to {e}, possibly missing the Allergen data?\nSkipping...\n')
            pass

    # BLAST #
    if args.blast:
        try:
            print('Performing BLAST transformations\n')
            # Run BLAST for potential homologus hits  with potentially smiliar epitopes - could be extended further to include species source, etc
            blast_df = pd.read_csv(f'{root_dir}/Allergens/allergenOnline_blast.txt', sep='\t', header=None)
            # Qseq ID -(has_similar_sequence)-> Seq ID (from DB) <-- atts: all other cols
            blast_df = blast_funcs.main(base_dir=sys.path[0], blast_df=blast_df)
            blast_df = blast_df.iloc[2:]
            blast_df.to_csv(f'{root_dir}/Allergens/allergen_online_blast_transformed.txt', sep='\t', index=None)
            print('Finished transformation BLAST data\n')
        except Exception as e:
            print(f'Error with transforming BLAST data due to {e}, possibly missing the Allergen data?\nSkipping...\n')
            pass


    # # OMIM data ##
    # While certain diseases can enhance risk I am omitting this as it's too broad - DisGenNet could be useful in future
    # omim_df = pd.read_csv(f'{root_dir}/Disease/omim/mim2gene.txt', sep='\t', skiprows=4)
    # omim_df.dropna(inplace=True)


    # # PUBMED data # #
    # TO DO - XML --> relational OR JSON-LD
    if args.food_usda:
        try:
            print('Performing USDA food data transformations\n')
            # # USDA data - depends on allergenOnline # #
            with zipfile.ZipFile(f'{root_dir}/Food/usda/FoodData_central_csv.zip') as zip_ref:
                zip_ref.extractall(f'{root_dir}/Food/usda/')

            usda_food_df = pd.read_csv(f'{root_dir}/Food/usda/food.csv')
            common_foods_df = pd.read_csv(f'{root_dir}/Allergens/allergen_online_transformed.tsv', sep="\t", usecols=['Common'])
            usda_allergen_mapping_df = usda_funcs.main(usda_food_df=usda_food_df, common_foods_df=common_foods_df)
            usda_allergen_mapping_df.to_csv(f'{root_dir}/Food/usda/usda_mapping_allergen_transformed.txt', sep='\t', index=None)

            # Remove junk from the zipped file
            usda_dir_l = os.listdir(f'{root_dir}/Food/usda/')
            filtered_files = [file for file in usda_dir_l if file.endswith(".csv")]
            for file in filtered_files:
            	path_to_file = os.path.join(f'{root_dir}/Food/usda/', file)
            	os.remove(path_to_file)

            print('Finished USDA food data transformations\n')
        except Exception as e:
            print(f'Error with transforming USDA data due to {e}, possibly missing the Allergen data?\nSkipping...\n')
            pass

    print(f'\nZess Science Transformation completed with duration: {datetime.now() - start_time}\n')

if __name__ == '__main__':
    # Create the parsers
    parser = argparse.ArgumentParser(description='Transformation for Zess Science data sources - pick your data source(s)\n\n')

    # Populate the arguments
    parser.add_argument(
                        '-mkdir', '--make_directory',
                        help='For local use: if this is your first time,\
                        selecting this option will enable the creation of a \
                        transformed local directory structure to be in place with the\
                        extracted dirs config with base dir of \
                        $HOME/Zess_science_data/', required=False)
    parser.add_argument(
                        '-g', '--gene', help='Currently transforms GWAS\
                         catalog data', required=False,
                         default=False, action='store_true')
    parser.add_argument(
                        '-ppint', '--ppi_intact', help='Transforms IntAct data\
                        Requires allergen data to be transformed',
                        required=False, default=False, action='store_true')
    parser.add_argument(
                        '-b', '--blast', help='Performs BLAST\
                        Requires allergen data to be transformed first',
                        required=False, default=False, action='store_true')
    parser.add_argument(
                        '-fusda', '--food_usda', help='Transforms the USDA food.csv data\
                        Matches most relevant foods, requires allergen transformed data',
                        required=False, default=False, action='store_true')
    parser.add_argument(
                        '-a', '--allergens', help='Transforms the allergen data\
                        for both allerbase and allergenOnline - a dependency for most of these transformations later here',
                        required=False, default=False, action='store_true')

    args = parser.parse_args()


    main(args)
