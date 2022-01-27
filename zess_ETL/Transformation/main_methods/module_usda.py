import pandas as pd
import numpy as np

def main(usda_food_df, common_foods_df):

    # Food data types we're interested in
    d_types = ['foundation_food', 'survey_fndds_food']
    # Filter to these datatypes, reduce repeats as we can refer to whatever FcID, so long as it matches
    usda_food_df = usda_food_df[usda_food_df['data_type'].str.contains('|'.join(d_types))].groupby('description').head(1)

    # Get the common foods to map to  from the allergens

    common_foods_df.drop_duplicates(inplace=True)
    foods = common_foods_df['Common'].to_list()
    # Now we will get all the matching descriptions agaisnt our common allergen foods
    # N.b. this doesn't use additional names/syns so yes, it's flawed. We need to rectify this in future with NER
    food_df_list = []
    for food in foods:
        food = food.lstrip(' ').rstrip(' ')
        results = usda_food_df[usda_food_df['description'].str.upper().\
        str.contains(f'{food} '.upper(), na=False) | usda_food_df['description'].str.upper().\
        str.contains(f'{food},'.upper(), na=False)]
        results['Common'] = food
        food_df_list.append(results)

    usda_allergen_mapping_df = pd.concat(food_df_list)
    usda_allergen_mapping_df.replace(np.nan, 'Not found', inplace=True)
    return usda_allergen_mapping_df
