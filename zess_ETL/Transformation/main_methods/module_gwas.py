#from zess_ETL.Transformation.main_methods.module_misc import *
from Transformation.main_methods.module_misc import *
import numpy as np

def main(dir, allergen_list):

    gwas_df = pd.read_csv(dir, sep='\t')
    # To resolve for the URI mapping - append https://www.ebi.ac.uk/efo/{accession_uri} - ensure the accession id has colons replaced with an underscore
    gwas_df['MAPPED_TRAIT_URI'] = gwas_df['MAPPED_TRAIT_URI'].str.split('/').str[-1].str.split('_').str[1]
    # Again, to resolve for PUBMED IDs you'll need to append the respective url, which is https://pubmed.ncbi.nlm.nih.gov/
    gwas_df['PUBMEDID'] = gwas_df['PUBMEDID'].astype(str).str.split('.').str[0]
    # Just remove empty gene IDs as the gene is crucial
    gwas_df['SNP_GENE_IDS'].replace(r'^\s*$', np.nan, regex=True, inplace=True)
    gwas_df['SNP_GENE_IDS'].dropna(inplace=True)

    gwas_df =   gwas_df[['PUBMEDID', 'STUDY', 'DISEASE/TRAIT', 'INITIAL SAMPLE SIZE',
               'REPLICATION SAMPLE SIZE', 'REGION', 'CHR_ID', 'CHR_POS', 'MAPPED_GENE',
               'UPSTREAM_GENE_ID', 'DOWNSTREAM_GENE_ID',
               'STRONGEST SNP-RISK ALLELE', 'CONTEXT','INTERGENIC',
               'RISK ALLELE FREQUENCY', 'P-VALUE', 'OR or BETA', '95% CI (TEXT)', 'MAPPED_TRAIT_URI']]
    # Get the strongest SNP, separate the allele into a new column and keep the accession ID separated
    gwas_df['ALLELE'] = gwas_df['STRONGEST SNP-RISK ALLELE'].str.split('-').str[1]
    gwas_df['STRONGEST SNP-RISK ALLELE'] = gwas_df['STRONGEST SNP-RISK ALLELE'].str.split('-').str[0]
    gwas_df.replace(np.nan, 'Not recorded', inplace=True)

    # Merged upstream and downstream gene ID's together but this means that they will form an attribute of the mapped gene - document
    gwas_df = df_split_df_list(gwas_df.astype(str), 'MAPPED_GENE', ',')
    gwas_df = df_split_df_list(gwas_df.astype(str), 'MAPPED_GENE', '-')

    gwas_df['MAPPED_GENE'].dropna(inplace=True)
    gwas_df['CONTEXT'] = gwas_df['CONTEXT'].str.replace('_', ' ')
    gwas_df['INTERGENIC'] = gwas_df['INTERGENIC'].str.replace('0.0', 'No').str.replace('1.0', 'Yes')

    gwas_df['INITIAL SAMPLE SIZE'] = gwas_df['INITIAL SAMPLE SIZE'].str.replace('approximately ', '~')
    gwas_df['REPLICATION SAMPLE SIZE'] = gwas_df['REPLICATION SAMPLE SIZE'].str.replace('approximately ', '~')

    gwas_df.drop_duplicates(inplace=True)
    # Now identify what allergy info there is (without narrowing it down to food)
    food_allergy_gwas_df = gwas_df[gwas_df['STUDY'].str.upper().str.contains('ALLERGY')]
    # Intolerance returns nothing useful
    food_allergy_gwas_df = food_allergy_gwas_df[~food_allergy_gwas_df['DISEASE/TRAIT'].str.contains('Self-reported allergy')]
    food_allergy_gwas_df = food_allergy_gwas_df[~food_allergy_gwas_df['DISEASE/TRAIT'].str.contains('Food allergy')]
    food_allergy_gwas_df['DISEASE/TRAIT'] = food_allergy_gwas_df['DISEASE/TRAIT'].\
                                            str.replace('\(parent-of-origin effect\)', '').\
                                            str.replace("Hen's egg", 'Egg').\
                                            str.replace('maternal genetic effects', '').\
                                            str.replace("\(\)", '').str.rstrip(' ')

    food_list = list(food_allergy_gwas_df['DISEASE/TRAIT'].str.replace("\(\)", '').str.rstrip(']').str.lower())


    common_foods = []
    for food in food_list:
        for allergen in allergen_list:
            if allergen in food.lower():
                common_foods.append(allergen.capitalize())

    food_allergy_gwas_df['Common'] = common_foods

    # food_allergy_gwas_df['Common food name'] = food_allergy_gwas_df['DISEASE/TRAIT']

    food_allergy_gwas_df.columns = ['PubMed ID', 'Study description', 'Disease/Trait', 'Starting sample size',
           'Replication sample size', 'Chromosome region', 'Chromosome ID', 'Chromosome position',
           'Gene ID', 'Upstream Gene ID', 'Downstream Gene ID', 'SNP',
           'SNP context', 'Intergenic', 'Risk allele frequency', 'P-value',
           'OR or BETA', '95% CI', 'EFO Trait URI', 'Allele', 'Common']

    return food_allergy_gwas_df
