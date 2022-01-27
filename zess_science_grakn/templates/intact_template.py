
class Intact:

    '''
    IntAct Schema
        Entity: protein-allergen - Atts: insert $proA has uniprot-id (Interactor A), has species-name (Taxid interactor A)* , has species-tax-id (Taxid interactor A)**
        * Split for species name, ** split for taxID
        Repeat for entity protein-allergen B

        Relationship: insert $interaction (protein-source: $proA, protein-target: $proB) isa interaction;
        Rel-Entity: $interaction - Atts: has interaction-detect (Interaction type(s)), has interaction-id (Interaction identifiers(s))* , has confidence (Confidence)
        has pubmed-id (Pubmed ID);

    '''

    def __init__(self):
        ## instantiating the 'Inner' class
        self.entities = self.Entities()
        self.relationships = self.Relationships()


    class Entities:
        #  ENTITIES class
        def intact_protein_template(a_or_b, action, dictionary):
            # For protein A
            graql_insert_query = f'{action}$pro{a_or_b} isa protein-allergen, has uniprot-id "' + dictionary[f'Interactor {a_or_b}'] + '"'
            try:
                graql_insert_query += f', has species-name "' + dictionary[f'Taxid interactor {a_or_b}'].split('(')[0].rstrip(' ') + '"'
                graql_insert_query += f', has species-name "' + dictionary[f'Taxid interactor {a_or_b}'].split('(')[1].rstrip(')') +  '"; '
            except:
                graql_insert_query += ';'
                pass
            return graql_insert_query

        def intact_publication_template(dictionary):
            # Insert publication
            graql_insert_query = f' insert $pub isa publication, has pubmed-id "' + dictionary['Pubmed ID'] + '"'
            graql_insert_query += f', has ebi-interaction-id "' + dictionary['Interaction identifier(s)'].replace('EBI-', '') +  '"'
            graql_insert_query += f', has confidence "' + dictionary['Confidence'] +  '"'
            graql_insert_query += f', has interaction-detection "' + dictionary['Interaction type(s)'] +  '"; '
            return graql_insert_query

        # Interaction --> interaction atts
        def intact_interaction_rel_entity_template(dictionary):
            # Insert interaction-detection
            graql_insert_query = f' $interaction isa interaction, has interaction-detection "' + dictionary['Interaction type(s)'] + '"'
            # Additiona atts
            graql_insert_query += f', has ebi-interaction-id "' + dictionary['Interaction identifier(s)'].replace('EBI-', '') +  '"'
            graql_insert_query += f', has confidence "' + dictionary['Confidence'] +  '"'
            graql_insert_query += f', has pubmed-id "' + dictionary['Pubmed ID'] +  '"; '
            return graql_insert_query

    class Relationships:
        #  RELATIONSHIPS class

        # Pro A <--> Pro B
        def intact_interaction_rel_template(dictionary):
            # Match Pro A
            graql_insert_query = Intact.Entities.intact_protein_template(a_or_b='A', action='match ', dictionary=dictionary)
            # Match Pro B
            graql_insert_query += Intact.Entities.intact_protein_template(a_or_b='B', action=' ', dictionary=dictionary)
            # Insert Rel
            graql_insert_query += f' insert $interaction (protein-source: $proA, protein-target: $proB) isa interaction;'
            graql_insert_query += f' $interaction isa interaction, has interaction-detection "' + dictionary['Interaction type(s)'] + '"'
            # Additiona atts
            graql_insert_query += f', has ebi-interaction-id "' + dictionary['Interaction identifier(s)'].replace('EBI-', '') +  '"'
            graql_insert_query += f', has confidence "' + dictionary['Confidence'] +  '"'
            graql_insert_query += f', has pubmed-id "' + dictionary['Pubmed ID'] +  '"; '

            return graql_insert_query
