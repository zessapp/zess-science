
class allergen_online:
    # Abstract methods class

    '''
    AllergenOnline Schema
        Entity: Food - Atts: has Common (common-food-name), has Type (food-type), has Species (species-name)
        Entity: protein-allergen - Atts: has uniprot-id (UNIPROT_ID), has ncbi-aid (NCBI_AID), has ncbi-id (NCBI_GID), has sequence (Sequence), has sequence-length (Length),
        has who-iuis-id (IUIS-ID), has allergen-group (Group)
        Entity: publication - Atts: has publication-extract (Allergenicity)
    '''

    # Add to allergen module or class
    def ao_food_allergen_template(self, action, dictionary):

        # First add food names
        graql_insert_query = f'{action}$food isa food, has common-food-name "'+ dictionary['Common'].lower() + '"'

        graql_insert_query += f', has food-type "'+ dictionary['Type'].lower() + '"'
        graql_insert_query += f', has species-name "' + dictionary['Species'].lower() + '"; '

        return graql_insert_query

    def ao_protein_allergen_template(self,action, dictionary):
        # Add protein-allergen
        graql_insert_query = f'{action}$allergen isa protein-allergen, has uniprot-id "' + dictionary['UNIPROT_ID'].upper() + '"'
        graql_insert_query += f', has ncbi-id "' + dictionary['NCBI_GID'].upper() + '"'
        if 'match ' not in action:
            graql_insert_query += f', has ncbi-aid "' + dictionary['NCBI_AID'].upper() + '"'
            graql_insert_query += f', has sequence "' + dictionary['Sequence'].upper() + '"'
        graql_insert_query += f', has sequence-length "' + dictionary['Length'] + '"'
        graql_insert_query += f', has who-iuis-id "' + dictionary['IUIS_ID'].capitalize() + '"'
        if 'match ' not in action:
            graql_insert_query += f', has allergen-group "' + dictionary['Group'] + '"; '
        else:
            graql_insert_query += '"; '
        return graql_insert_query

    def ao_publication_template(self,dictionary):
        return f' insert $pub isa publication, has publication-extract "' + dictionary['Allergenicity'] + '"; '

    def ao_food_allergen_rel_template(self,dictionary):
        # Match food
        graql_insert_query = allergen_online.ao_food_allergen_template(self=self, action = 'match ', dictionary=dictionary)
        # Match protein
        graql_insert_query += allergen_online.ao_protein_allergen_template(self=self, action = '', dictionary=dictionary)
        # insert rel
        graql_insert_query += f' insert $new-allergen-food (allergen-isin-food: $allergen, food-contains-allergen: $food) isa allergen-food-association, has publication-extract "' + dictionary['Allergenicity'] + '";'
        # graql_insert_query += f' $new-allergen-food ;'
        return graql_insert_query
