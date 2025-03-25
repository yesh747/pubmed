# PubMed API Wrapper for python
Pubmed documentation is less than ideal. Making this library to  help python researchers easily query PubMed.

## Create query
Example of creating a query. Note that because of pubmed api restrictions,  queries with many results are broken into chunks of 10,000 articles at a time with a delay between each request. If you attempt too many queries at once, you may get rate limited by pubmed itself. You should try again after a few minutes if this happen.


    from pubmedquery import PubMedQuery

    query_text = "randomized control trial of radiation vs surgery for oropharynx SCC"
    query = PubMedQuery(query_text) # an array of PubMedArticle objects

# Save to Pandas DF / CSV
Turn query result into a pandas data and save as csv

    def pubmed_query_to_df(query):
        df = {'pmid': [],
          'authors': [], #list of authors and their institutions
          'title': [],
          'abstract': [],
          'pubdate': [],
          'keywords': [],
          'meshheadings_major': [],
          'meshheadings_minor': [],
          'citedByPMIDs': [],
          'citation_count': [],
          'journal': [],
          'journal_abbr': [],
          'journal_volume': [],
          'journal_issue': [],
          'pubtypes': [],
        }
    
        # loop through query results and save to dataframe
        for i, article in enumerate(query.articles):
            print('\r{} : {}'.format(i, article.pmid), end='')
        
            df['pmid'].append(article.pmid)
            df['authors'].append(article.authors)                   
            df['title'].append(article.title)
            df['abstract'].append(article.abstract)
            df['pubdate'].append(article.pubdate)
            df['keywords'].append(article.keywords)
            df['meshheadings_major'].append(article.meshheadings_major)
            df['meshheadings_minor'].append(article.meshheadings_minor)
            df['citedByPMIDs'].append(article.citedByPMIDs)
            df['citation_count'].append(len(article.citedByPMIDs))
            df['journal'].append(article.journal)
            df['journal_abbr'].append(article.journal_abbr)
            df['journal_volume'].append(article.journal_volume)
            df['journal_issue'].append(article.journal_issue)
            df['pubtypes'].append(article.pubtypes)
            print('\n')
        return df

    df = pubmed_query_to_df(query)
    df.to_csv('pubmed_query.csv', index=False)



