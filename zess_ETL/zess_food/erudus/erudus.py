import json
import requests
import pandas as pd
import os
import sys
from secret import authorization_body
import argparse



def main(args):

    case_label_name, food_type, page = args.food, args.food_type, args.page

    # Request authorization token
    response = requests.post('https://services.erudus.com/api/access_token', json=authorization_body)
    if response.status_code == 200:
        print("successful response")
        access_token = response.json()['access_token']
        # request product information
        header = {'Authorization': f'Bearer {access_token}', 'Content-type': 'application/json'}
        # Example request - can remove paging later
        #page, case_label_name, type = '1', 'pepper', 'sauce'
        # Veg, Meat, vegeterian, etc
        #type = 'sauce'
        if page is not None:
            product_response = requests.get(f'https://services.erudus.com/api/public/v1/products?page={page}&case_label_name={case_label_name}&status=active', headers = header)
        else:
            product_response = requests.get(f'https://services.erudus.com/api/public/v1/products?case_label_name={case_label_name}&status=active', headers = header)
        # Let's find out more about the product - pick one at random
        data = product_response.json()['data']
        filtered_products = []
        for product in data:
            if f' {case_label_name.upper()} ' in product['case_label_name'].upper():
                #product_ids.append(product['id'])
                product_id = product['id']
                product_info = requests.get(f'https://services.erudus.com/api/public/v1/products/{product_id}', headers = header)
                try:
                    if f'{food_type.upper()}' in product_info.json()['data']['generic_type'].upper():
                        # From here you can add more conditions which will limit the food based on allergens, among other things
                        filtered_products.append(product_info.json()['data'])
                except:
                    print('Field not found')
                    pass

        product_len = len(filtered_products)
        print(f'Identified {product_len} products fitting the given parameters')
        if product_len == 0:
            print("As nothing has been identified with your query, I'm quitting.\n")
            sys.exit()

        product_df = pd.json_normalize(filtered_products)
        product_df.rename(columns={'id':'data.id'}, inplace=True)

        components_df_list = [pd.json_normalize(component) for component in product_df['components']]
        component_df = pd.concat(components_df_list)
        component_df.rename(columns={'id':'components.id'}, inplace=True)
        component_df['data.id'] = product_df['data.id']

        filtered_erudus_df = product_df.merge(component_df, on='data.id')
        filtered_erudus_df.to_csv(f'{os.getcwd()}/erudus_query.txt', sep='\t', index=None)
        print(f'Data has been written out to {os.getcwd()}/erudus_query.txt')

    else:
        print(f"Unable to correct due to error code {response.status_code}, quitting.")
        sys.exit()

if __name__ == '__main__':
    # Set up the parser
    parser = argparse.ArgumentParser(description='Erudus api wrapper, pick your foods to search\n\n')

    parser.add_argument(
                        '-f', '--food',
                        help='You must use this flag to set what food you wish\
                        to search for in Erudus',
                        required=True)
    parser.add_argument(
                        '-t', '--food_type',
                        help='You must use this flag to set what type of food you wish\
                        to search for in Erudus.\ni.e. sauce or vegetable',
                        required=True)
    parser.add_argument(
                        '-p', '--page',
                        help='You must use this flag to set how many pages you wish\
                        to search for on Erudus of food you wish',
                        required=True)
    args = parser.parse_args()

    main(args)
