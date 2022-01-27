from os.path import expanduser

home = expanduser('~')
root_dir = f'{home}/Zess_science_data'
main_dir_names = ['Allergens', 'Proteins', 'Literature', 'Genes', 'Food', 'Drug', 'Disease', 'Ontologies']

allergens = [
'allergen_online',
'allerbase'
]

proteins = [
'uniprotkb_allergenome_fasta',
'uniprot_all_allergenome_fasta',
'uniprotkb_allergenome_all',
'int_act'
]

literature = [
'pubmed'
]

genes = [
'gwas_catalog',
'mapping'
]

food = [
'usda'
]

drug = [
'drug_bank',
'chembl'
]

disease = [
'omim'
]

ontologies = [
'go',
'hpo',
'efo',
'food_on'
]
