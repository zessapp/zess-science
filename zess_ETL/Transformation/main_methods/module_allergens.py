import csv
import requests
from bs4 import BeautifulSoup
import numpy as np
import math
import pandas as pd
import urllib.parse
import urllib.request
import io
from datetime import datetime



def allerbase_decorator(function):
    def allerbase_wrapper(d):
        data = function(d)
        allerbase_df = pd.DataFrame(data[2:])
        allerbase_df = allerbase_df.drop(allerbase_df.index[[1]])
        allerbase_df.columns = allerbase_df.iloc[0]
        return allerbase_df[1:]
    return allerbase_wrapper


@allerbase_decorator
def reformat_encoding(dir):
    d = []
    with open(dir, encoding='mac_roman') as csvfile:
        areader = csv.reader(csvfile, delimiter='\t')
        max_elems = 0
        for row in areader:
            if max_elems < len(row): max_elems = len(row)
        csvfile.seek(0)
        for i, row in enumerate(areader):
            # Pad the rows
            d.append(row + ["" for x in range(max_elems-len(row))])
    return d

def compare_ids(dic, id_list, id_set, column_list, type):
    missing_ids = [x for x in id_list if x not in id_set]
    for id in missing_ids:
        dic[id] = f'{type} not found'
    df = pd.DataFrame(columns=[column_list[0], column_list[1]])
    df[column_list[0]] = dic.keys()
    df[column_list[1]] = dic.values()
    return df

def allerbase(dir):

    allerbase_df = reformat_encoding(dir)

    # Format is completely messed up so just drop the bad data as we can't format every case just yet
    formatted_allerbase_df = allerbase_df[allerbase_df['Reference'].apply(lambda x: str(x).isdigit())]
    formatted_allerbase_df = formatted_allerbase_df.drop(formatted_allerbase_df.columns[[5, 6, 8, 9, 13, 14,15]], axis=1)

    unformatted_allerbase_df = allerbase_df[~allerbase_df['Reference'].apply(lambda x: str(x).isdigit())]
    unformatted_allerbase_df = unformatted_allerbase_df.drop(unformatted_allerbase_df.columns[[5, 6, 7, 9, 10, 14,15]], axis=1)
    unformatted_allerbase_df.columns = formatted_allerbase_df.columns

    allerbase_filtered_df = formatted_allerbase_df.append(unformatted_allerbase_df, ignore_index=True)
    allerbase_filtered_df.replace('-', 'Not recorded', inplace=True)
    allerbase_filtered_df.rename(columns={'Isoallergen / Variant':'IUIS_ID'}, inplace=True)
    # We are only interested in the Antigens present in AllergenOnline right now - so map to that
    # Write allergen data back out to transformed folders
    allerbase_filtered_df.dropna(inplace=True)
    allerbase_filtered_df.drop_duplicates(inplace=True)
    return allerbase_filtered_df

def eutil_api_mode(url, extension, search_set, mode, tag, dic):
    print(f"\n\nFetching {mode.replace('_', ' ').title()}s, this can take a while as the API requires you to search item by item... please wait\n")
    for i, v in enumerate(search_set):
        content = requests.get(f'{url}{v}{extension}').text
        soup = BeautifulSoup(content, 'lxml')
        for td in soup.findAll(tag):
            dic[v] = td.get_text()

def ncbi_eutils(mode, search_set, dic):
        '''
            Utilises NCBIS eutils esearch or efetch to retrieve data.
            While batch processing is possible, it's prone to failure, ergo iterations on each is important.
        '''
        if mode.upper() == 'TAX_ID':
            url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=taxonomy&term='
            eutil_api_mode(url=url, extension='', search_set=search_set, mode=mode.upper(), tag='id', dic=dic)
        elif mode.upper() == 'SEQ':
            url, extension = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&id=', '&rettype=fasta&retmode=xml'
            eutil_api_mode(url=url, extension=extension, search_set=search_set, mode=mode.upper(), tag='tseq_sequence', dic=dic)

def annotate(main_df, columns, mode, type):
    id_set = set(main_df[columns[0]])
    dic = {}
    ncbi_eutils(mode=mode, search_set=id_set, dic=dic)
    df = compare_ids(dic=dic, id_list=dic.keys(),
                            id_set=id_set, column_list=columns,
                            type=type)
    return main_df.merge(df, on=[columns[0]], how='inner')

def fetch_uniprot_ids(GI_list):
    '''
        Fetches the UniProt ID's from NCBI GI accessions to map to the main allergen database
    '''
    url = 'https://www.uniprot.org/uploadlists/'
    params = {
    'from': 'P_GI',
    'to': 'ACC',
    'format': 'tab',
    'query': str(list(GI_list)).replace('[', '').replace(']','').replace(',', ' ')
    }

    data = urllib.parse.urlencode(params)
    data = data.encode('utf-8')
    req = urllib.request.Request(url, data)
    with urllib.request.urlopen(req) as f:
       response = f.read()

    uniprot_df = pd.read_csv(io.StringIO(response.decode('utf-8')), sep='\t')
    uniprot_df.columns = ['NCBI_GID', 'UNIPROT_ID']
    return uniprot_df

def allergen_online_filter(df, fa_out_dir):
    print('Starting to filter allergenOnline data\n\n')

    df.rename(columns={'IUIS Allergen':'IUIS_ID',
                      'Accession':'NCBI_AID', '#GI':'NCBI_GID',
                      'First version':'db_version'}, inplace=True)
    allergen_online_df = df[df['Type'].str.contains('Food')]
    allergen_online_df['IUIS_ID']=allergen_online_df['IUIS_ID'].replace(['Unassigned'], 'Not given')
    # Can later be used to fetch pubmed papers related to species and common names
    # i.e. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&id=P00785.4&rettype=fasta&retmode=text
    # Can also perform later epitope prediction

    # Batch download the AA sequences
    allergen_online_df = annotate(main_df=allergen_online_df,
                                    columns=['NCBI_AID', 'Sequence'], mode='SEQ',
                                    type='Sequence')
    # Get tax IDs
    allergen_online_df = annotate(main_df=allergen_online_df,
                                    columns=['Species', 'Tax_ID'], mode='TAX_ID',
                                    type='Tax ID')

    GI_list = allergen_online_df['NCBI_GID']
    uniprot_df = fetch_uniprot_ids(GI_list)
    allergen_online_df = allergen_online_df.merge(uniprot_df, on=['NCBI_GID'], how='inner')

    allergen_online_df = allergen_online_df[['Species', 'Tax_ID', 'Common',
                                            'IUIS_ID', 'Type', 'Group',
                                            'Allergenicity','Length', 'UNIPROT_ID',
                                            'NCBI_AID', 'NCBI_GID',  'Sequence']]

    # Make a fasta file for allergenOnline
    pro_list = list(allergen_online_df['UNIPROT_ID'])
    seq_list = list(allergen_online_df['Sequence'])

    ofile = open(fa_out_dir, "w")

    for i in range(len(seq_list)):
        ofile.write(f'>{pro_list[i]}\n{seq_list[i]}\n')
    ofile.close()

    return allergen_online_df
