import csv
from tqdm import tqdm

class grakn_subroutines:
    '''
        Abstract methods class with the core grakn functions
        Including methods to query, delete, and insert data into grakn
    '''

    def query_graph(self, query, keyspace, var_name):
        with client.session(keyspace=keyspace) as session:
            with session.transaction().read() as read_transaction:
                answer_iterator = read_transaction.query(query).get()
                val_list = [ans.get(var_name) for ans in answer_iterator]
                for val in val_list:
                    print(f"retrieved item with id {val.id}")
        return val_list

    def delete_data(self, query, keyspace):
        with client.session(keyspace=keyspace) as session:
            with session.transaction().write() as delete_transaction:
                deletion_iterator = delete_transaction.query(query)
                delete_transaction.commit()
                print('Deleted data.')

    def insert_data(self, query, keyspace, entity, var_name):
        with client.session(keyspace=keyspace) as session:
            with session.transaction().write() as write_transaction:
                insert_iterator = write_transaction.query(query).get()
                concepts = [ans.get(var_name) for ans in insert_iterator]
                print(f"Inserted a {entity} with ID: {concepts[0].id}")
                ## to persist changes, write transaction must always be committed (closed)
                write_transaction.commit()

    def load_data_into_grakn(self, client, query, keyspace):
        with client.session(keyspace=keyspace) as session:
            with session.transaction().write() as write_transaction:
                insert_iterator = write_transaction.query(query)
                write_transaction.commit()

class generic_subroutines:
    '''
        Abstract methods class with more generic functions
        Including methods to parse data into a dictionary and load into grakn
    '''

    def parse_data_to_dictionaries(self, input):
        items = []
        with open(input) as data:
            for row in csv.DictReader(data, delimiter='\t', skipinitialspace = True):
                item = { key: value for key, value in row.items() }
                items.append(item)
        return items

    def load_grakn_data(self, query_list, ds_n, client, keyspace):
        '''
            Loads data into grakn via load_data_into_grakn function call
            Requires the query list, client, keyspace, and dataset name
        '''
        for query in tqdm(query_list):
            grakn_subroutines.load_data_into_grakn(self=self, client=client, query=query, keyspace=keyspace)
        print(f'Finished loading {ds_n} data\n\n')
