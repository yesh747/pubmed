# PubMed API Wrapper for python
Pubmed documentation is less than ideal. Making this library to  help python researchers easily query PubMed.

## Create query and save to csv
Example of creating a query. Note that because of pubmed api restrictions,  queries with many results are broken into chunks of 10,000 articles at a time with a delay between each request. If you attempt too many queries at once, you may get rate limited by pubmed itself. You should try again after a few minutes if this happen.


    from pubmedquery import PubMedQuery

    query_text = "randomized control trial of radiation vs surgery for oropharynx SCC"
    query = PubMedQuery(query_text) # an array of PubMedArticle objects
    df = query.__getdataframe__() # create pandas dataframe
    df.to_csv('filepath.csv', index=Flase)
