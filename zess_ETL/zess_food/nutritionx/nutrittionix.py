import json
from nutritionix import Nutritionix
import argparse
import requests
import pandas as pd
import tabulate as tabulate
from time import sleep
from secret import secret
import os

def main(args):

    print('Processing your query...\n\n')
    query = args.food

    nix = Nutritionix(app_id=secret['app_id'], api_key=secret['api_key'])

    # Return only USDA matches
    results = nix.search().nxql(
        filters={
            "exists": {
                "usda_fields": "true"
            }

        },

        fields=["item_name", "item_id", "serving_weight_grams", "nf_calories",
                "nf_total_fat", "nf_saturated_fat", "nf_cholesterol", "nf_sodium",
                "nf_total_carbohydrate", "nf_dietary_fiber", "nf_sugars",
                "nf_protein", "nf_potassium", "nf_p", "full_nutrients"],
        query=query
        ).json()

    results_df = pd.json_normalize(results['hits'])
    del results_df['_index']
    del results_df['_id']
    del results_df['_type']
    results_df.columns=results_df.columns.str.replace('_', ' ').str.replace('fields.', '').str.replace('nf', '').str.lstrip(' ')
    results_df = results_df[['item id', 'item name', 'score', 'calories', 'total fat', 'saturated fat', 'cholesterol', 'sodium', 'total carbohydrate', 'dietary fiber', 'sugars', 'protein']]
    print('\n\nCheck out your table below!\n\n')
    sleep(1.2)
    print(results_df.to_markdown())
    results_df.to_csv(f'{os.getcwd()}/nutritionix_query.txt', sep='\t', index=None)
    print(f'\n\n\nData has been written out to {os.getcwd()}/nutritionix_query.txt\n\nFinished running script. Goodbye.\n\n')

if __name__ == '__main__':
    # Set up the parser
    parser = argparse.ArgumentParser(description='Nutritionix api wrapper, pick your foods to search\n\n')

    parser.add_argument(
                        '-f', '--food',
                        help='You must use this flag to set what food you wish\
                        to search for in Nutritionix',
                        required=True)
    args = parser.parse_args()

    main(args)
