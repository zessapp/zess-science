import pandas as pd
import numpy as np


def search_for(df, l, col, operator):
    if operator == '~':
        return df[~df[col].str.contains('|'.join(l))]
    else:
        return df[df[col].str.contains('|'.join(l))]

def format_taxid(col, df):
    species_list = list(df[col].str.replace(r'[^(]*\(|\)[^)]*', ''))
    taxid_list = list(df[col].str.split('(').str[0].str.split(':').str[1])
    df[col] = [f"{s} ({t})" for s, t in zip(species_list, taxid_list)]


def main(int_act_df, allergen_online_df):
    int_act_df['Publication Identifier(s)'] = int_act_df['Publication Identifier(s)'].str.split('|').str[0].str.replace('pubmed:', '')

    # Now remove all unassigned PubMed ID's as we only want data we can reference to on ULMS so not including imex and mint. DOIs too as we want to map to NCBI only
    search_list = ['unassigned', 'mint', 'imex', 'doi']
    int_act_df = search_for(df=int_act_df, l=search_list, col='Publication Identifier(s)', operator='~')


    int_act_df.rename(columns={'Publication Identifier(s)':'Pubmed ID',
                                'Confidence value(s)': 'Confidence',
                                '#ID(s) interactor A': 'Interactor A',
                                'ID(s) interactor B': 'Interactor B'}, inplace=True)

    int_act_df['Confidence'] = int_act_df['Confidence'].str.split(':').str[1].str.split('|').str[0].str.replace('intact-miscore:', '').str.replace(r'[a-zA-Z]','')

    mask = pd.to_numeric(int_act_df['Confidence'], errors='coerce')
    idx = mask.isna()
    int_act_df = int_act_df[~idx]

    # Clean up the interaction identifiers
    search_list = ['uniprot']
    int_act_df = search_for(df=int_act_df, l=search_list,
                            col='Interactor A', operator='')
    int_act_df = search_for(df=int_act_df, l=search_list,
                            col='Interactor B', operator='')

    int_act_df['Interactor A'] = int_act_df['Interactor A'].str.replace('uniprotkb:', '')
    int_act_df['Interactor B'] = int_act_df['Interactor B'].str.replace('uniprotkb:', '')

    int_act_df['Interaction identifier(s)'] = int_act_df['Interaction identifier(s)'].str.split('|').str[0].str.replace('intact:', '')
    int_act_df['Interaction type(s)'] = int_act_df['Interaction type(s)'].str.split('(').str[1].str.replace('(', '').str.replace(')', '')
    int_act_df['Interaction detection method(s)'] = int_act_df['Interaction detection method(s)'].str.split('(').str[1].str.replace('(', '').str.replace(')', '')
    # Format the columns
    tax_id_cols = ['Taxid interactor A', 'Taxid interactor B']
    [format_taxid(col, int_act_df) for col in tax_id_cols]
    # Map with what we have in our allergen database to be more concise
    uniprot_list = list(allergen_online_df['UNIPROT_ID'])
    int_act_df = int_act_df[int_act_df.isin(uniprot_list).any(1)]
    # Let's make sure we now only get human - X/human interaction results
    int_act_df = int_act_df[(int_act_df['Taxid interactor A'].str.contains('9606')) | (int_act_df['Taxid interactor B'].str.contains('9606'))]

    return int_act_df
