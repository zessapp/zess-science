
class Blast:
    '''
    BLAST Schema
        Entity: protein-allergen - Atts: insert $query isa protein-allergen, has uniprot-id (qsedid);
        Entity: protein-allergen - Atts: insert $subject isa protein-allergen, has uniprot-id (sseqid);
        Repeat for entity protein-allergen B

        Relationship: insert $hss (protein-query: $query, protein-subject: $subject) isa has-similar-sequence;
        Rel-Entity: $hss - Atts: $hss isa has-similar-sequence, has blast "True", has percent-identical-matches (pident),
        has alignment-length (length) , has number-of-mismatches (mismatch), has number-of-gap-openings (gapopen), has query-alignment-start (qstart),
        has query-alignment-end (qend), has subject-alignment-start (sstart), has subject-alignment-end (send), has expected-value (evalue), has bit-score (bitscore);
    '''


    def __init__(self):
        ## instantiating the 'Inner' class
        self.entities = self.Entities()
        self.relationships = self.Relationships()


    class Entities:
        #  ENTITIES class
        def blast_protein_entity(q_or_s, action, dictionary):
            # For protein A
            graql_insert_query = f'{action}${q_or_s} isa protein-allergen, has uniprot-id "' + dictionary[f'{q_or_s}'] + '"; '
            return graql_insert_query

    class Relationships:
        # RELATIONSHIPS class
        def blast_interaction_rel_template(dictionary):
            # Match Pro A
            graql_insert_query = Blast.Entities.blast_protein_entity(q_or_s='qseqid', action='match ', dictionary=dictionary)
            # Match Pro B
            graql_insert_query += Blast.Entities.blast_protein_entity(q_or_s='sseqid', action=' ', dictionary=dictionary)
            # Insert Rel
            graql_insert_query += f' insert $hss (protein-query: $qseqid, protein-subject: $sseqid) isa has-similar-sequence;'
            graql_insert_query += f' $hss isa has-similar-sequence,has blast "True"'
            # Additiona atts
            graql_insert_query += f', has percent-identical-matches "' + dictionary['pident'] +  '"'
            graql_insert_query += f', has alignment-length "' + dictionary['length'] +  '"'
            graql_insert_query += f', has number-of-mismatches "' + dictionary['mismatch'] +  '"'
            graql_insert_query += f', has number-of-gap-openings "' + dictionary['gapopen'] +  '"'
            graql_insert_query += f', has query-alignment-start "' + dictionary['qstart'] +  '"'
            graql_insert_query += f', has query-alignment-end "' + dictionary['qend'] +  '"'
            graql_insert_query += f', has subject-alignment-start "' + dictionary['sstart'] +  '"'
            graql_insert_query += f', has subject-alignment-end "' + dictionary['send'] +  '"'
            if 'e' in dictionary['evalue']:
                graql_insert_query += f', has expected-value "' + str(dictionary['evalue'].split('e')[:4]) + 'E' + str(dictionary['evalue'].split('e')[1]) +  '"'
            else:
                graql_insert_query += f', has expected-value "' + dictionary['evalue'] + '"'
            graql_insert_query += f', has bit-score "' + dictionary['bitscore'] +  '"; '

            return graql_insert_query
