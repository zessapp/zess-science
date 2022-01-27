class Usda:
    # Entity mapping only class
    '''
    USDA Schema
        Entity: food - Atts: insert $food isa food, has common-food-name (Common)*, has fdc-id (fdc_id),
        has usda-description (description)*, has usda-dataset-type (data_type), has date-published (publication_date)
        * lower

        Could refine publication date name

    '''

    def __init__(self):
        ## instantiating the 'Entities' class
        self.entities = self.Entities()

    class Entities:

        def usda_food_template(dictionary):
            # First add food names
            graql_insert_query = f'insert $food isa food, has common-food-name "'+ dictionary['Common'].lower() + '"'

            graql_insert_query += f', has fdc-id "'+ dictionary['fdc_id'] + '"'
            desc = dictionary['description'].lower()
            graql_insert_query += f', has usda-description "' + desc.replace("\"", '') + '"'
            graql_insert_query += f', has usda-dataset-type "'+ dictionary['data_type'] + '"'
            graql_insert_query += f', has date-published "'+ dictionary['publication_date'] + '"; '

            return graql_insert_query
