from os.path import expanduser
from grakn.client import GraknClient
from tqdm import tqdm
import argparse
# import os, sys
# module_path = os.path.abspath(os.path.join('zess_science_grakn/'))
# if module_path not in sys.path:
#    sys.path.append(module_path)
# os.getcwd()
from templates.allergen_online_template import allergen_online as ao_class
from templates.allerbase_template import allerbase as ab_class
from templates.gwas_catalog_template import Gwas as gwas_class
from templates.intact_template import Intact as intact_class
from templates.blast_template import Blast as blast_class
from templates.usda_template import Usda as usda_class
from modules.grakn_functions import grakn_subroutines as main_subroutines
from modules.grakn_functions import generic_subroutines as generic_subroutines

def main(root_dir,keyspace,client, args):

    if args.all_flag:
        args.food_usda, args.blast, args.ppi_intact, args.allergens, args.gwas = True, True, True, True, True
    # Init functions from module abstract classes
    main_funcs = main_subroutines()
    generic_funcs = generic_subroutines()

    # Dictionary containing dictionary of data aka inception dictionary
    zsci_trans_df_dict = {
    'allergenOnline': generic_funcs.parse_data_to_dictionaries(f'{root_dir}/Allergens/allergen_online_transformed.tsv'),
    'allerbase': generic_funcs.parse_data_to_dictionaries(f'{root_dir}/Allergens/allerbase_transformed.tsv'),
    'gwas_catalog': generic_funcs.parse_data_to_dictionaries(f'{root_dir}/Genes/gwas_catalog/gwas-catalog-food-allergies_transformed.tsv'),
    'intact': generic_funcs.parse_data_to_dictionaries(f'{root_dir}/Proteins/int_act/intact_transformed.txt'),
    'blast': generic_funcs.parse_data_to_dictionaries(f'{root_dir}/Allergens/allergen_online_blast_transformed.txt'),
    'usda': generic_funcs.parse_data_to_dictionaries(f'{root_dir}/Food/usda/usda_mapping_allergen_transformed.txt')
    }

    if args.allergens:

        # Insert data for allergenOnline
        '''
        AllergenOnline Schema
            Entity: Food - Atts: has Common (common-food-name), has Type (food-type), has Species (species-name)
            Entity: protein-allergen - Atts: has uniprot-id (UNIPROT_ID), has ncbi-aid (NCBI_AID), has ncbi-id (NCBI_GID), has sequence (Sequence), has sequence-length (Length),
            has who-iuis-id (IUIS-ID), has allergen-group (Group)
            Entity: publication - Atts: has publication-extract (Allergenicity)
        '''

        print('Loading AllergenOnline data\n\n')
        ao_subroutines = ao_class()
        allergen_online_query_list = []
        for query_row in tqdm(zsci_trans_df_dict['allergenOnline']):
            allergen_online_query_list.append(ao_subroutines.ao_food_allergen_template(action='insert ', dictionary=query_row))
            allergen_online_query_list.append(ao_subroutines.ao_protein_allergen_template(action='insert ', dictionary=query_row))
            allergen_online_query_list.append(ao_subroutines.ao_publication_template(dictionary=query_row))
            allergen_online_query_list.append(ao_subroutines.ao_food_allergen_rel_template(dictionary=query_row))

        # Load data into graph
        generic_funcs.load_grakn_data(query_list=list(set(allergen_online_query_list)), ds_n='AllergenOnline', client=client, keyspace=keyspace)

        '''
        allerbase Schema
            Entity: protein-allergen - Atts: has who-iuis-id (Allergen), has epitope-sequence (Epitope), has epitope-type (Type of Epitope),
            has sequence-position (Sequence Position), has epitope-nature (Nature of Epitope)
            Entity: publication - Atts: has pubmed-id (Reference), has assay-type-used (Assay), has antibody-used (Antibody Used)

            Relationship: (allergen-found-in-publication: $allergen, publication-allergen-studied-in: $pub) isa allergen-studied-in;
            n.b. append https://pubmed.ncbi.nlm.nih.gov/ to reference start
        '''
        print('Loading Allerbase data\n\n')
        ab_subroutines = ab_class()
        allerbase_query_list = []

        for query_row in tqdm(zsci_trans_df_dict['allerbase']):
            allerbase_query_list.append(ab_subroutines.ab_protein_allergen_template(action='insert', dictionary=query_row))
            allerbase_query_list.append(ab_subroutines.ab_publication_template(action='insert', dictionary=query_row))
            allerbase_query_list.append(ab_subroutines.ab_allergen_publication_rel_template(dictionary=query_row))

        # Load allerbase into graph
        generic_funcs.load_grakn_data(query_list=allerbase_query_list, ds_n='allerbase', client=client, keyspace=keyspace)

    # GWAS data
    '''
    gwas-catalog Schema
        Entity: food - Atts: has common-food-name (Common)
        Entity: snp - Atts: has rs-id (SNP), has allele (Allele), has snp-context (SNP context), has intergenic (Intergenic)
        n.b. transform 'Yes' in intergenic to True
        Entity: gene - Atts: has hgnc-id (Gene ID), has chromosome-id (Chromosome ID), has chromosome-position (Chromosome position),
        has chromosome-region (Chromosome region)
        Entity: upstream-gene - Atts: has ensembl-id (Upstream Gene ID)
        Entity: downstream-gene - Atts: has ensembl-id (Downstream Gene ID)
        Entity: publication - Atts: has pubmed-id (PubMed ID), has publication-extract (Study description),
        has starting-sample-size (Starting sample size),
        has replication-sample-size (Replication sample size), has risk-allele-frequency (Risk allele frequency),
        has p-value (P-value), has odds-ratio-or-beta (OR or BETA), has confidence-interval (95% CI)*
        Entity: disease - Atts: has disease-name (Disease/Trait), has efo-id (EFO Trait URI)

        * Append (95%) to CI string

        Relationship: food - disease: (food-associated-with-disease: $allergen, disease-associated-with-food: $disease) isa food-disease-association;
        Relationship: snp - disease: (disease-associated-with-snp: $disease, snp-associated-with-disease: $snp) isa snp-disease-association;
        Relationship: gene - snp: (gene-related-to-snp: $gene, snp-related-to-gene: $snp) isa gene-snp-relationship;
        Relationship: upstream-gene - snp: (gene-related-to-snp: $upstream, snp-related-to-gene: $snp) isa gene-snp-relationship;
        Relationship: downstream-gene - snp: (gene-related-to-snp: $downstream, snp-related-to-gene: $snp) isa gene-snp-relationship;
        Relationship: disease - publication: (disease-found-in-publication: $disease, studied-in-publication $pub) isa studied-in;
        Relationship: gene - publication: (gene-found-in-publication: $gene, studied-in-publication $pub) isa studied-in;
        Relationship: snp - publication: (snp-found-in-publication: $snp, studied-in-publication $pub) isa studied-in;


        ** Upstream, downstream, and gene need to be checked for 'Not recorded' before creating relationship
    '''

    if args.gwas:
        print('Loading GWAS catalog data\n\n')
        gwas_subroutines = gwas_class()
        gwas_query_list = []

        for query_row in tqdm(zsci_trans_df_dict['gwas_catalog']):
            # Entities
            gwas_query_list.append(gwas_subroutines.Entities.gwas_food_template(action='insert', dictionary=query_row))
            gwas_query_list.append(gwas_subroutines.Entities.gwas_snp_template(action='insert', dictionary=query_row))
            gwas_query_list.append(gwas_subroutines.Entities.gwas_gene_template(action='insert', dictionary=query_row))
            gwas_query_list.append(gwas_subroutines.Entities.gwas_upstream_gene_template(action='insert', dictionary=query_row))
            gwas_query_list.append(gwas_subroutines.Entities.gwas_downstream_gene_template(action='insert', dictionary=query_row))
            gwas_query_list.append(gwas_subroutines.Entities.gwas_publication_template(action='insert', dictionary=query_row))
            gwas_query_list.append(gwas_subroutines.Entities.gwas_disease_template(action='insert', dictionary=query_row))

            # Relationships
            gwas_query_list.append(gwas_subroutines.Relationships.gwas_food_disease_rel_template(dictionary=query_row))
            gwas_query_list.append(gwas_subroutines.Relationships.gwas_snp_disease_rel_template(dictionary=query_row))
            gwas_query_list.append(gwas_subroutines.Relationships.gwas_gene_snp_rel_template(dictionary=query_row))
            gwas_query_list.append(gwas_subroutines.Relationships.gwas_upstream_gene_snp_rel_template(dictionary=query_row))
            gwas_query_list.append(gwas_subroutines.Relationships.gwas_downstream_gene_snp_rel_template(dictionary=query_row))
            # Pub rels
            gwas_query_list.append(gwas_subroutines.Relationships.gwas_disease_publication_rel_template(dictionary=query_row))
            gwas_query_list.append(gwas_subroutines.Relationships.gwas_gene_publication_rel_template(dictionary=query_row))
            gwas_query_list.append(gwas_subroutines.Relationships.gwas_gene_publication_rel_template(dictionary=query_row))

        # Remove None types
        gwas_query_list = list(filter(None, gwas_query_list))
        gwas_query_list = [s.lstrip(' ') for s in gwas_query_list]

        # Load GWAS catalog into graph
        generic_funcs.load_grakn_data(query_list=gwas_query_list, ds_n='GWAS catalog', client=client, keyspace=keyspace)

    # IntAct data
    '''
    IntAct Schema
        Entity: protein-allergen - Atts: insert $proA has uniprot-id (Interactor A), has species-name (Taxid interactor A)* , has species-tax-id (Taxid interactor A)**
        * Split for species name, ** split for taxID
        Repeat for entity protein-allergen B

        Relationship: insert $interaction (protein-source: $proA, protein-target: $proB) isa interaction;
        Rel-Entity: $interaction - Atts: has interaction-detect (Interaction type(s)), has interaction-id (Interaction identifiers(s))* , has confidence (Confidence)
        has pubmed-id (Pubmed ID);

    '''
    if args.ppi_intact:
        print('Loading IntAct data\n\n')
        intact_subroutines = intact_class()
        intact_query_list = []

        for query_row in tqdm(zsci_trans_df_dict['intact']):
            # Entities
            intact_query_list.append(intact_subroutines.Entities.intact_protein_template(a_or_b='A', action='insert ', dictionary=query_row))
            intact_query_list.append(intact_subroutines.Entities.intact_protein_template(a_or_b='B', action='insert ', dictionary=query_row))
            intact_query_list.append(intact_subroutines.Entities.intact_publication_template(dictionary=query_row))

            # Relationships
            intact_query_list.append(intact_subroutines.Relationships.intact_interaction_rel_template(dictionary=query_row))
            # Rel entity
            # intact_query_list.append(intact_subroutines.Entities.intact_interaction_rel_entity_template(dictionary=query_row))

        # Remove None types
        intact_query_list = list(filter(None, intact_query_list))
        intact_query_list = [s.lstrip(' ') for s in intact_query_list]

        # Load IntAct into graph
        generic_funcs.load_grakn_data(query_list=intact_query_list, ds_n='IntAct', client=client, keyspace=keyspace)

    # BLAST data
    '''
    BLAST Schema
        Entity: protein-allergen - Atts: insert $query isa protein-allergen, has uniprot-id (qsedid);
        Entity: protein-allergen - Atts: insert $subject isa protein-allergen, has uniprot-id (sseqid);
        Repeat for entity protein-allergen B

        Relationship: insert $hss (protein-query: $query, protein-subject: $subject) isa has-similar-sequence;
        Rel-Entity: $hss - Atts: $hss isa has-similar-sequence, has blast "True", has percent-identical-matches (pident),
        has alignment-length (length) , has number-of-mismatches (mismatch), has number-of-gap-openings (gapopen), has query-alignment-start (qstart),
        has query-alignment-end (qend), has subject-alignment-start (sstart), has subject-alignment-end (send), has expected-value (evalue), has bit-score (bitscore);
    '''
    if args.blast:
        print('Loading BLAST data\n\n')
        blast_subroutines = blast_class()
        blast_query_list = []

        for query_row in tqdm(zsci_trans_df_dict['blast']):
            # Entities
            blast_query_list.append(blast_subroutines.Entities.blast_protein_entity(q_or_s='qseqid', action='insert ', dictionary=query_row))
            blast_query_list.append(blast_subroutines.Entities.blast_protein_entity(q_or_s='sseqid', action='insert ', dictionary=query_row))

            # Relationships
            blast_query_list.append(blast_subroutines.Relationships.blast_interaction_rel_template(dictionary=query_row))

        blast_query_list = [s.lstrip(' ') for s in blast_query_list]
        # Load BLAST into graph
        generic_funcs.load_grakn_data(query_list=blast_query_list, ds_n='BLAST', client=client, keyspace=keyspace)


    # USDA data - mapping
    '''
    USDA Schema
        Entity: food - Atts: insert $food isa food, has common-food-name (Common)*, has fdc-id (fdc_id),
        has usda-description (description)*, has usda-dataset-type (data_type), has date-published (publication_date)
        * lower

        Could refine publication date name

    '''
    if args.food_usda:
        print('Loading USDA data\n\n')
        usda_subroutine = usda_class()
        usda_query_list = []

        for query_row in tqdm(zsci_trans_df_dict['usda']):
            # Entities
            usda_query_list.append(usda_subroutine.Entities.usda_food_template(dictionary=query_row))

        usda_query_list = [s.lstrip(' ') for s in usda_query_list]
        # Load BLAST into graph
        generic_funcs.load_grakn_data(query_list=usda_query_list, ds_n='USDA', client=client, keyspace=keyspace)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grakn loader for Zess Science data sources - pick your data source(s)\n\n')

    # Populate args
    parser.add_argument(
                        '-g', '--gwas', help='Populate GWAS data', required=False,
                         default=False, action='store_true')
    parser.add_argument(
                        '-ppint', '--ppi_intact', help='Populate IntAct data',
                        required=False, default=False, action='store_true')
    parser.add_argument(
                        '-b', '--blast', help='Populate BLAST data',
                        required=False, default=False, action='store_true')
    parser.add_argument(
                        '-f', '--food_usda', help='Populate food data from USDA',
                        required=False, default=False, action='store_true')
    parser.add_argument(
                        '-a', '--allergens', help='Populate Allergen data from \
                        allerbase & allergenOnline',
                        required=False, default=False, action='store_true')
    parser.add_argument(
                        '-all', '--all_flag', help='Downloads all data',
                        required=False, default=False, action='store_true')

    parser.add_argument(
                        '-k', '--keyspace', help='Keyspace to query',
                        required=True)

    # Add other args too and refactor this all
    args = parser.parse_args()
    root_dir = f"{expanduser('~')}/Zess_science_data"
    keyspace=args.keyspace
    client = GraknClient(uri="127.0.0.1:48555")
    main(root_dir,keyspace,client, args)
