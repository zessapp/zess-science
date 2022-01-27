
class allerbase:
    # Abstract methods class

    '''
    allerbase Schema
        Entity: protein-allergen - Atts: has who-iuis-id (Allergen), has epitope-sequence (Epitope), has epitope-type (Type of Epitope),
        has sequence-position (Sequence Position), has epitope-nature (Nature of Epitope)
        Entity: publication - Atts: has pubmed-id (Reference), has assay-type-used (Assay), has antibody-used (Antibody Used)

        Relationship: (allergen-found-in-publication: $allergen, publication-allergen-studied-in: $pub) isa allergen-studied-in;
        n.b. append https://pubmed.ncbi.nlm.nih.gov/ to reference start
    '''

    def ab_protein_allergen_template(self, action, dictionary):

        # Add protein-allergen
        graql_insert_query = f'{action}$allergen isa protein-allergen, has who-iuis-id "' + dictionary['Allergen'].capitalize() + '"'
        if 'match ' not in action:
            graql_insert_query += f', has epitope-sequence "' + dictionary['Epitope'] + '"'
            graql_insert_query += f', has epitope-type "' + dictionary['Type of Epitope'].lower() + '"'
        graql_insert_query += f', has sequence-position "' + dictionary['Sequence Position'] + '"'
        graql_insert_query += f', has epitope-nature "' + dictionary['Nature of Epitope'] + '"; '
        return graql_insert_query

    def ab_publication_template(self, action, dictionary):

        # Insert publication for allergen
        graql_insert_query = f' {action} $pub isa publication, has pubmed-id "' + dictionary['Reference'] + '"'
        graql_insert_query += f', has assay-type-used "' + dictionary['Assay'] + '"'
        if 'match ' not in action:
            graql_insert_query += f', has antibody-used "' + dictionary['Antibody Used'] + '"; '
        else:
            graql_insert_query +=  '"; '
        return graql_insert_query

    def ab_allergen_publication_rel_template(self, dictionary):
        # Match food
        graql_insert_query = allerbase.ab_protein_allergen_template(self=self, action = 'match ', dictionary=dictionary)
        # Match protein
        graql_insert_query += allerbase.ab_publication_template(self=self, action = '', dictionary=dictionary)
        # insert rel
        graql_insert_query += f' insert (allergen-found-in-publication: $allergen, studied-in-publication: $pub) isa studied-in;'
        # graql_insert_query += f' $new-allergen-food ;'
        return graql_insert_query
