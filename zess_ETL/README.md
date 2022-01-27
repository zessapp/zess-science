# Zess Science ETL

Welcome! This is the Zess Science ETL repo, designed to obtain the data sources deemed most useful for Zess' scientific work & overall mission. The datasources are transformed appropriately with their biological relevance and modelling in mind.

## Requirements

These scripts do require that you use Python 3+, so just download any variation of [Python 3](https://www.python.org/download/releases).
[Docker](https://www.docker.com/get-started) is also essential is you wish  to perform BLAST on the allergen proteins against an allergen database for similar sequences and potential homologus links

Ensembls biomart may be used in future (via rpy2, potentially) to obtain homology data, or OMA - whatever is best for our purposes. It's possible we can utilise BLAST on epitope data of the antigens too to find potential cross-reactivity between species i.e. Antigen Act 1 being similar to a hypothetical Antigen found in another food that wasn't identified before

All module dependencies are listed in the [requirements.txt](https://bitbucket.org/zess-new/zess-etl/src/master/requirements.txt) and can be very easily installed to your local environment. You could do the following:

**For pip**
```
pip install -r requirements.txt
```
**For conda**
```
conda install --file requirements.txt
```

Great, you're on your way.

## What's what?

The main components of this repo are the Extraction and Transformation components, which can be executed via the [zess_extraction.py](https://bitbucket.org/zess-new/zess-etl/src/master/zess_extraction.py) and [zess_transformation.py](https://bitbucket.org/zess-new/zess-etl/src/master/zess_transformation.py).

### Zess Extraction

The Zess Extraction script is design to of course download data in it's source of truth raw format and be pushed into a data lake. There are 9 arguments it can take, in total. As they are all booleans, you need only present the flag if you wish to perform that operation.

This includes the following:

1. **-mkdir** - this is for local use only. It will enable the creation of a local directory structure as manually configured in the [dir configuration](https://bitbucket.org/zess-new/zess-etl/src/master/configs/dir_names.py) and your base directory will be **$HOME/Zess_science_data/** unless changed in code. If you are doing your runs locally, use this for first time setup.
2. **-gmain** - this will fetch [GWAS catalog](https://www.ebi.ac.uk/gwas/) data
3. **-gmap** - this will fetch HGNC to Ensembl Mapping data so gene common names are present
4. **-unimain** - this will extract both [UniProtKB](https://www.uniprot.org/) (reviewed) fasta data and XML data that contains publication and gene ontology links. This is for the allergenome database.
5. **-ppim** - this will extract [IntAct](https://www.ebi.ac.uk/intact/) protein-protein interaction data.
6. **-ontg** - this will extract a range of ontology datasets that are in OWL format. This includes the [Human Phenotype Ontology](https://hpo.jax.org/app/), [Gene Ontology](http://geneontology.org/), and [Experimental Factor Ontology](https://www.ebi.ac.uk/efo/)
7. **-ontf** - this will extract the [Food Ontology](https://foodon.org/) dataset in an OWL format
8. **-fusda** - this will extract all the USDA food data
9. **-a** - this will extract (via webscraping) [AllergenOnline](http://www.allergenonline.org/databasebrowse.shtml) data and [allerbase](http://196.1.114.46:1800/AllerBase/) data for Allergen - Food relationships and Antigen-Antibody

Here is an example to download allergen and USDA data:

```
python3 zess_extraction.py -a -fusda
```

You may wish to create a python/BASH wrapper that will run your commands in parallel to speed up the Extraction phase

### Zess Transformation

The Zess Transformation script will transform the extracted data, obtaining it from the local file structure described. This is to be replaced in due course with having data pushed either via stream or obtained from an s3 bucket. It can be slower than the Extraction as some module functions will call REST API services that have to query data (of note: eutils for NCBI data, which can be found used in [module_allergens.py](https://bitbucket.org/zess-new/zess-etl/src/master/Transformation/main_methods/module_allergens.py)) one at a time, otherwise complications occur that affect the data output. This can be as long as 12-15 minutes if running everything. Again, parallelisation is ideal, but bear in mind that some functions depend upon having transformed Allergen data prior to being run.

Transformations ultimately result in tabular data that's transformed in such a manner to make it human and machine readable in addition to extracting and/or updating/annotating/appending the most relevant biological information and in a FAIR manner. This will make data modelling and schema creation significantly easier for later use.

Less arguments exist as not all of the data is Transformed (yet). OWL and XML data isn't transformed yet as parsers are required for this. They include the following:

1. **-mkdir** - this will create some local Transformation directories in a fashion coherent to the Extraction script. It's not necessary, again and may become deprecated and removed.
2. **-g** - this will transform the GWAS catalog data appropriately by getting the most important components from the data
3. **-ppint** - this transforms the Int Act data, and it does require you have the allergen data transformed and ready
4. **-b** - this will perform BLAST via docker (allergenome DB vs allergenOnline) but it does require that the allergen transformation was performed and a FASTA file was written out by the allergen transformation (please refer to [module_allergens.py](https://bitbucket.org/zess-new/zess-etl/src/master/Transformation/main_methods/module_allergens.py) line 150-157)
5. **-fusda** - this will transform the USDA data and match allergen food data to what's present, or the closest match. NER and NLP should be used in future to get the best matches. It will require allergen data to be transformed and ready.
6. **-a** - this will transform the allergen data (allerbase and allergenOnline)

This can be run in the same manner as the zess extraction script is run. Though, you will use *zess_transformation.py* instead.

### Other scripts
You may note that other scripts exist in the zess_food folder. This is for erudus and nutritionix testing. They can be built upon further if one wishes to improve querying agaisnt the erudus database and/or nutritionix via their API. They are not currently integral to Zess Science (yet).
