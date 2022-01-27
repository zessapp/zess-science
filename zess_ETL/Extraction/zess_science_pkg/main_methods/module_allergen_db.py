import re
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup


def scrape_allergendb(url):
    print('Scraping allergenOnline for data...\n')
    # STEP 1: set up the HTTP request to GET raw content
    html_content = requests.get(url).text

    # STEP 2: We'll now parse the HTML content
    soup = BeautifulSoup(html_content, 'lxml')

    # STEP 3: fetch the database variable
    scripts = soup.find_all('script')
    finder = re.findall(r'var allergen_database = .*?;', str(scripts))

    # STEP 4: Convert the variable to a JSON
    db_json_list = finder[0].replace('var allergen_database = ', '').lstrip('[').lstrip('{').rstrip(';').rstrip(']').rstrip('}').split('},{')
    # List the columns as posted on the database site
    allergen_db_cols = ['Species', 'Common', 'IUIS Allergen', 'Type', 'Group',
                        'Allergenicity', 'Length', 'Accession', '#GI', 'First Version']
    # Collect into a dataframe list & concat
    df_list, common_name = [], 0
    for i, row in enumerate(db_json_list):
        try:
            current_row = json.loads(''.join(('{', row, '}')))
            if str(current_row['common']) is '':
                try:

                    species_name = current_row['species']
                    # Fetch the tax ID from NCBI Entrez
                    tax_id_content = requests.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=taxonomy&term={species_name}').text
                    tax_id_soup = BeautifulSoup(tax_id_content, 'lxml')
                    for td in tax_id_soup.findAll('id'):
                        tax_id = td.get_text()

                    # Now we can fetch the parent common species
                    parent_name_content = requests.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=taxonomy&id={tax_id}&retmode=xml').text
                    name_soup = BeautifulSoup(parent_name_content, 'lxml')
                    for td in name_soup.findAll('division'):
                        parent_name_content = td.get_text()

                    current_row['common'] = parent_name_content
                    if common_name % 10 == 0:
                        print(f'Updated {common_name + 1} common name(s), current common name updated to {parent_name_content}')
                    common_name += 1
                except:
                    pass

            row_mapping = {
                            'Species': [current_row['species']],
                            'Common' : [current_row['common']],
                            'IUIS Allergen' : [current_row['allergen']],
                            'Type': [current_row['type']],
                            'Group': [current_row['groupname']],
                            'Allergenicity': [current_row['confidence']],
                            'Length': [current_row['length']],
                            'Accession': [current_row['GBSeq_accession-version']],
                            '#GI': [current_row['GI']],
                            'First Version': [current_row['tempflag']]
                            }

            temp_df = pd.DataFrame(row_mapping, columns=allergen_db_cols)
            df_list.append(temp_df)
        except:
            print(f'Failed for row index {i}')
            pass
    print(f'\nUpdated a total of {common_name + 1} common names')
    # STEP 5: Produce the dataframe and return it
    return pd.concat(df_list)
