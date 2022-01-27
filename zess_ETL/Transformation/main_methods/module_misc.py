import pandas as pd


def df_split_df_list(df, target_column, separator):
    """ df = dataframe to split,
    target_column = the column containing the values to split
    separator = the symbol used to perform the split
    Returns: a dataframe with each entry for the target column separated, with each element moved into a new row.
    The values in the other columns are duplicated across the newly divided rows.
    """
    def split_list_2_rows(row, row_accumulator, target_column, separator):
        split_row = row[target_column].split(separator)
        for s in split_row:
            new_row = row.to_dict()
            new_row[target_column] = s
            row_accumulator.append(new_row)
    new_rows = []
    df.apply(split_list_2_rows, axis=1, args=(
        new_rows, target_column, separator))
    new_df = pd.DataFrame(new_rows)
    return new_df
