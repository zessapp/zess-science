
class Gwas:
    # Abstract methods class
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

        Relationship: food - disease: (food-associated-with-disease: $food, disease-associated-with-food: $disease) isa food-disease-association;
        Relationship: snp - disease: (disease-associated-with-snp: $disease, snp-associated-with-disease: $snp) isa snp-disease-association;
        Relationship: gene - snp: (gene-related-to-snp: $gene, snp-related-to-gene: $snp) isa gene-snp-relationship;
        Relationship: upstream-gene - snp: (gene-related-to-snp: $upstream, snp-related-to-gene: $snp) isa gene-snp-relationship;
        Relationship: downstream-gene - snp: (gene-related-to-snp: $downstream, snp-related-to-gene: $snp) isa gene-snp-relationship;
        Relationship: disease - publication: (disease-found-in-publication: $disease, studied-in-publication $pub) isa studied-in;
        Relationship: gene - publication: (gene-found-in-publication: $gene, studied-in-publication $pub) isa studied-in;
        Relationship: snp - publication: (snp-found-in-publication: $snp, studied-in-publication $pub) isa studied-in;


        ** Upstream, downstream, and gene need to be checked for 'Not recorded' before creating relationship
    '''

    def __init__(self):
        ## instantiating the 'Inner' class
        self.entities = self.Entities()
        self.relationships = self.Relationships()


    class Entities:
        #  ENTITIES class

        # Food
        def gwas_food_template(action, dictionary):
            # Add food
            return f'{action}$food isa food, has common-food-name "' + dictionary['Common'].lower() + '";'

        # SNPs
        def gwas_snp_template(action, dictionary):
            # Insert SNPs
            graql_insert_query = f' {action} $snp isa snp, has rs-id "' + dictionary['SNP'] + '"'
            if 'match ' not in action:
                graql_insert_query += f', has allele "' + dictionary['Allele'] + '"'
                graql_insert_query += f', has snp-context "' + dictionary['SNP context'] + '"'
                # Teneary comparor to assess what to input for Intergenic bool
                intergenic = 'true' if 'Yes' in dictionary['Intergenic'] else 'false'
                graql_insert_query += f', has intergenic "' + intergenic + '"; '
            else:
                graql_insert_query += ';'
            return graql_insert_query

        # Genes
        def gwas_gene_template(action, dictionary):
            # Insert SNPs
            graql_insert_query = f' {action} $gene isa gene, has hgnc-id "' + dictionary['Gene ID'] + '"'
            graql_insert_query += f', has chromosome-id "' + dictionary['Chromosome ID'] + '"'
            graql_insert_query += f', has chromosome-position "' + dictionary['Chromosome position'] + '"'
            graql_insert_query += f', has chromosome-region "' + dictionary['Chromosome region'] + '"; '
            return graql_insert_query

        def gwas_upstream_gene_template(action, dictionary):
            return f' {action} $upstream isa upstream-gene, has ensembl-id "' + dictionary['Upstream Gene ID'] + '"; '

        def gwas_downstream_gene_template(action, dictionary):
            return f' {action} $downstream isa downstream-gene, has ensembl-id "' + dictionary['Downstream Gene ID'] + '"; '

        # Publications
        def gwas_publication_template(action,dictionary):
            # Insert pubs
            graql_insert_query = f' {action} $pub isa publication, has pubmed-id "' + dictionary['PubMed ID'] + '"'
            if 'match ' not in action:
                graql_insert_query += f', has publication-extract "' + dictionary['Study description'] + '"'
                graql_insert_query += f', has starting-sample-size "' + dictionary['Starting sample size'] + '"'
                graql_insert_query += f', has replication-sample-size "' + dictionary['Replication sample size'] + '"'
            graql_insert_query += f', has risk-allele-frequency "' + dictionary['Risk allele frequency'] + '"'
            graql_insert_query += f', has p-value "' + dictionary['P-value'] + '"'
            graql_insert_query += f', has odds-ratio-or-beta "' + dictionary['OR or BETA'] + '"'
            graql_insert_query += f', has confidence-interval "' + dictionary['95% CI'] + ' (95% CI)' + '"; '
            return graql_insert_query

        # Disease
        def gwas_disease_template(action,dictionary):
            # Insert Disease (not literally, though)
            graql_insert_query = f' {action} $disease isa disease, has disease-name "' + dictionary['Disease/Trait'] + '"'
            graql_insert_query += f', has efo-id "' + dictionary['EFO Trait URI'] + '"; '
            return graql_insert_query

    class Relationships:
        #  RELATIONSHIPS class

        # Food <--> Disease
        def gwas_food_disease_rel_template(dictionary):
            # Match the Food
            graql_insert_query = Gwas.Entities.gwas_food_template(action = 'match ', dictionary=dictionary)
            # Now match the Disease
            graql_insert_query += Gwas.Entities.gwas_disease_template(action = '', dictionary=dictionary)
            # Insert the relationship
            graql_insert_query += f' insert (food-associated-with-disease: $food, disease-associated-with-food: $disease) isa food-disease-association;'
            return graql_insert_query

        # SNP <--> Disease
        def gwas_snp_disease_rel_template(dictionary):
            # Match the SNP
            graql_insert_query = Gwas.Entities.gwas_snp_template(action = 'match ', dictionary=dictionary)
            # Now match the Disease
            graql_insert_query += Gwas.Entities.gwas_disease_template(action = '', dictionary=dictionary)
            # Insert the relationship
            graql_insert_query += f' insert (disease-associated-with-snp: $disease, snp-associated-with-disease: $snp) isa snp-disease-association;'
            return graql_insert_query

        # Gene <--> SNP
        def gwas_gene_snp_rel_template(dictionary):
            # Check entity is present
            if 'Not recorded' not in dictionary['Gene ID']:
                # Match the SNP
                graql_insert_query = Gwas.Entities.gwas_snp_template(action = 'match ', dictionary=dictionary)
                # Now match the Gene
                graql_insert_query += Gwas.Entities.gwas_gene_template(action = '', dictionary=dictionary)
                # Insert the relationship
                graql_insert_query += f' insert (gene-related-to-snp: $gene, snp-related-to-gene: $snp) isa gene-snp-relationship;'
                return graql_insert_query
            else:
                return None

        # Upstream-gene <--> SNP
        def gwas_upstream_gene_snp_rel_template(dictionary):
            # Check entity is present
            if 'Not recorded' not in dictionary['Upstream Gene ID']:
                # Match the SNP
                graql_insert_query = Gwas.Entities.gwas_snp_template(action = 'match ', dictionary=dictionary)
                # Now match the upstream Gene
                graql_insert_query += Gwas.Entities.gwas_upstream_gene_template(action = '', dictionary=dictionary)
                # Insert the relationship
                graql_insert_query += f' insert (gene-related-to-snp: $upstream, snp-related-to-gene: $snp) isa gene-snp-relationship;'
                return graql_insert_query
            else:
                return None

        # Downstream-gene <--> SNP
        def gwas_downstream_gene_snp_rel_template(dictionary):
            # Check entity is present
            if 'Not recorded' not in dictionary['Downstream Gene ID']:
                # Match the SNP
                graql_insert_query = Gwas.Entities.gwas_snp_template(action = 'match ', dictionary=dictionary)
                # Now match the downstream Gene
                graql_insert_query += Gwas.Entities.gwas_downstream_gene_template(action = '', dictionary=dictionary)
                # Insert the relationship
                graql_insert_query += f' insert (gene-related-to-snp: $downstream, snp-related-to-gene: $snp) isa gene-snp-relationship;'
                return graql_insert_query
            else:
                return None

        # Publication rels

        # Disease <--> Publication
        def gwas_disease_publication_rel_template(dictionary):
            # Match the SNP
            graql_insert_query = Gwas.Entities.gwas_disease_template(action = 'match ', dictionary=dictionary)
            # Now match the publication
            graql_insert_query += Gwas.Entities.gwas_publication_template(action = '', dictionary=dictionary)
            # Insert the relationship
            graql_insert_query += f' insert (disease-found-in-publication: $disease, studied-in-publication: $pub) isa studied-in;'
            return graql_insert_query

        # Gene <--> Publication
        def gwas_gene_publication_rel_template(dictionary):
            # Match the SNP
            graql_insert_query = Gwas.Entities.gwas_gene_template(action = 'match ', dictionary=dictionary)
            # Now match the publication
            graql_insert_query += Gwas.Entities.gwas_publication_template(action = '', dictionary=dictionary)
            # Insert the relationship
            graql_insert_query += f' insert (gene-found-in-publication: $gene, studied-in-publication: $pub) isa studied-in;'
            return graql_insert_query

        # SNP <--> Publication
        def gwas_gene_publication_rel_template(dictionary):
            # Match the SNP
            graql_insert_query = Gwas.Entities.gwas_snp_template(action = 'match ', dictionary=dictionary)
            # Now match the publication
            graql_insert_query += Gwas.Entities.gwas_publication_template(action = '', dictionary=dictionary)
            # Insert the relationship
            graql_insert_query += f' insert (snp-found-in-publication: $snp, studied-in-publication: $pub) isa studied-in;'
            return graql_insert_query
