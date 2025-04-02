# PubMed API Wrapper for python
Pubmed documentation is less than ideal. Making this library to  help python researchers easily query PubMed.

## Installation
    pip install pubmedquery

## Create query and save to csv
Example of creating a query. Note that because of pubmed api restrictions,  queries with many results are broken into chunks of 10,000 articles at a time with a delay between each request. If you attempt too many queries at once, you may get rate limited by pubmed itself. You should try again after a few minutes if this happen.


    from pubmedquery import PubMedQuery

    # get an array of PubMedArticle objects
    query_text = "randomized control trial of radiation vs surgery for oropharynx SCC"
    query = PubMedQuery(query_text,
                time_delay=0.34, # the minimum to avoid timing out. increase if timeout errors
                citedBy=False, # make True to get array of pmids that cite the current article, 
                chunk_size=100, # break up into miniqueuries of n=100. increase if getting errors from pubmed client
                ) 

    df = query.__getdataframe__() # create pandas dataframe
    df.to_csv('filepath.csv', index=Flase)


## PubMedArticle
PubMedQuery.articles returns a list of PubmedArticles with the following details:

    Class: PubMedArticle
    Represents a PubMed article parsed from XML data. This class extracts and organizes
    various metadata, authorship details, publication information, and other relevant
    attributes from the provided XML structure.
    
    Attributes:
        root (xml.etree.ElementTree.Element): The root XML element of the article.
        citedByPMIDs (list): A list of PMIDs that cite this article.
        pmid (str): The PubMed ID of the article.
        journal (str): The full title of the journal in which the article was published.
        journal_abbr (str): The abbreviated title of the journal.
        pubtypes (list): A list of publication types for the article.
        journal_issue (str or None): The issue number of the journal, if available.
        journal_volume (str or None): The volume number of the journal, if available.
        pubdate (datetime.date): The publication date of the article.
        title (str): The title of the article.
        abstract (str): The abstract text of the article.
        authors (list): A list of dictionaries containing author details, including:
            - lastname (str): The last name of the author.
            - firstname (str or None): The first name of the author, if available.
            - affiliation (str or None): The affiliation of the author, if available.
        keywords (list): A list of keywords associated with the article.
        meshheadings_major (list): A list of major MeSH (Medical Subject Headings) terms.
        meshheadings_minor (list): A list of minor MeSH terms.

