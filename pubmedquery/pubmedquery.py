#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PubMed API

Created on Wed Mar 17 19:08:14 2021

@author: yesh
"""
import os

import time
import numpy as np
import pandas as pd
import requests
import xml.etree.ElementTree as xml

from datetime import date


class PubMedArticle():
    def __init__(self, article_xml, print_xml=False):
        # get article

        self.root = article_xml
        
        # initialize citedByPMIDs
        self.citedByPMIDs = []
        
        if print_xml:
            self.print_xml(self.root)
        try:
            self.pmid = self.root.find('./MedlineCitation/PMID').text
            articlePath = './MedlineCitation/Article/'
                
            # METADATA
            self.journal = self.root.find(articlePath + 'Journal/Title').text
            self.journal_abbr = self.root.find(articlePath + 'Journal/ISOAbbreviation').text
            self.pubtypes = [pubtype.text for pubtype in self.root.findall(articlePath + 'PublicationTypeList/PublicationType')]

            journal_issue_xml = self.root.find(articlePath + 'Journal/JournalIssue/Issue')
            if journal_issue_xml is not None:
                self.journal_issue = self.root.find(articlePath + 'Journal/JournalIssue/Issue').text
            else:
                self.journal_issue = None
                
            journal_volume_xml = self.root.find(articlePath + 'Journal/JournalIssue/Volume')
            if journal_volume_xml is not None:
                self.journal_volume = self.root.find(articlePath + 'Journal/JournalIssue/Volume').text
            else:
                self.journal_volume = None
            
            # DATE
            pubdate = self.root.find('./PubmedData/History/PubMedPubDate[@PubStatus="pubmed"]')
            year = pubdate.find('Year').text
            month = pubdate.find('Month').text
            day = pubdate.find('Day').text
            self.pubdate = date(int(year), int(month), int(day))
            
            self.title = self.root.find(articlePath + 'ArticleTitle').text
            
        
            # abstract
            self.abstract = self.root.findall('.//AbstractText')
            # need this step for when there are multiple abstract text objects
            self.abstract = ' '.join([''.join(section.itertext()) for section in self.abstract])
            
            # authors
            authorlist = self.root.findall(articlePath + 'AuthorList/Author')
            self.authors = []
            for author in authorlist:        
                affiliation_xml = author.find('AffiliationInfo/*')
                if affiliation_xml is not None:
                    affiliation = ''.join(author.find('AffiliationInfo/*').itertext())
                else:
                    affiliation = None
                    
                # A Group or Collective is sometimes included in author lists instead of an author
                collective_name = author.find('CollectiveName')
                if collective_name is not None:
                    self.collective_name = collective_name.text
                else:
                    
                    # check if they have firstname
                    firstname_xml = author.find('ForeName')
                    if firstname_xml is not None:
                        firstname = firstname_xml.text
                    else:
                        firstname = None
                    
                    self.authors.append({
                        'lastname': author.find('LastName').text,
                        'firstname': firstname,
                        'affiliation': affiliation,
                        })
                    
            # Keywords
            keywordlist = self.root.findall(articlePath + '../KeywordList/Keyword')
            self.keywords = []
            for keyword in keywordlist:
                self.keywords.append(keyword.text)
                
                
            # MAJOR Mesh headings
            meshheading_major_list = self.root.findall(articlePath + '../MeshHeadingList/MeshHeading/*[@MajorTopicYN="Y"]')
            self.meshheadings_major = []
            for meshheading_major in meshheading_major_list:
                self.meshheadings_major.append(meshheading_major.text)    
            # - remove duplicates
            self.meshheadings_major = list(dict.fromkeys(self.meshheadings_major))


            # MINOR mesh headings
            meshheading_minor_list = self.root.findall(articlePath + '../MeshHeadingList/MeshHeading/*[@MajorTopicYN="N"]')
            self.meshheadings_minor = []
            for meshheading_minor in meshheading_minor_list:
                self.meshheadings_minor.append(meshheading_minor.text) 
            # - remove duplicates
            self.meshheadings_minor = list(dict.fromkeys(self.meshheadings_minor))
            
        except AttributeError:
            self.print_xml(self.root)
            print(self.title)
            print(self.journal)
            print(self.pmid)
            raise(AttributeError)
            
    def add_citedByData(self, citedByPMIDs):
        self.citedByPMIDs = citedByPMIDs
        return
        
    def print_xml(self, xml_item=None):
        if xml_item==None:
            xml_item = self.root
        print(xml.tostring(xml_item, encoding='utf8').decode('utf8'))


class PubMedArticleList():
    """
    - Input: list of pmids     
    - Creates Object that is a list of PubMedArticles
    """
    def __init__(self, pmids, BASE_URL, DB, citedBy, time_delay, print_xml=False, api_key=None):
        self.api_key = api_key

        # A. Get articles
        url = '{}efetch.fcgi?db={}&id={}&retmode=xml'.format(BASE_URL, DB, pmids)
        if self.api_key:
                url += '&api_key={}'.format(self.api_key)
        r = requests.get(url)
        r.raise_for_status()
        root = xml.fromstring(r.text)
        time.sleep(time_delay)
        

        self.root = root
        self.articles_xml = root.findall('./PubmedArticle')
        self.articles = []
        for article_xml in self.articles_xml:
            self.articles.append(PubMedArticle(article_xml, print_xml=print_xml))
          
        # B. Get articles that cite the queried articles.
        if citedBy:
            linkname =  '{}_pubmed_citedin'.format(DB)
            link_url = '{}/elink.fcgi?dbfrom={}&linkname={}&id={}&retmode=json'.format(
                BASE_URL, 
                DB, 
                linkname,
                '&id='.join(pmids))
            r_link = requests.get(link_url)
            r_link.raise_for_status()
            r_link = r_link.json()
            linksets = r_link['linksets']
            time.sleep(0.34)     
            
            # looping through nonsense to get to the IDs for articles that cite the PMID articles
            for linkset in linksets:
                linkset_pmid = linkset['ids'][0]
                assert(len(linkset['ids']) == 1)
                if 'linksetdbs' in linkset.keys():
                    for linksetdb in linkset['linksetdbs']:
                        if (linksetdb['linkname'] == linkname) and ('links' in linksetdb.keys()):
                            links = linksetdb['links']
                            citedByPMIDs = links
                            for article in self.articles:
                                if article.pmid == linkset_pmid:
                                    article.add_citedByData(citedByPMIDs)
                                    


class PubMedQuery():
    def __init__(self, query,
                 BASE_URL='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/', 
                 DB='pubmed',
                 RESULTS_PER_QUERY=100000, #pubmed  hard limit is 9999 pmids at a time
                 citedBy=True, # get articles that cite the queried articles - will slow down queries 
                 print_xml=False,
                 chunk_size=100, #chunk size - larger batches/chunks will cause pubmed to crash
                 time_delay=0.34, # time delay between queries - increase if you get rate limit errors
                 api_key = None, # NCBI API key - optional, but recommended to avoid rate limits
                 ): 
        self.BASE_URL = BASE_URL
        self.DB = DB
        self.RESULTS_PER_QUERY = RESULTS_PER_QUERY
        self.query = query
        self.citedBy=citedBy
        self.time_delay = time_delay
        self.api_key = api_key

        # query
        self.pmids, self.count, self.querytranslation = self.__query_pmids__(self.query)
        print('{} results for: {}'.format(self.count, self.querytranslation))
        
        if self.count > 9999:
            raise Exception("TOO LARGE QUERY, BREAK DOWN INTO SMALLER =<9999 results per query")

        self.articles = self.__query_articles__(self.pmids, print_xml, chunk_size)
        
        
    def __query_pmids__(self, query):
        pmids = []
        retstart = 0
        count = 999999
        
        while retstart < count:  
            url = '{}esearch.fcgi?db={}&term={}&retmax={}&retmode=json&retstart={}'.format(
                    self.BASE_URL, self.DB, self.query, self.RESULTS_PER_QUERY, retstart)
            if self.api_key:
                url += '&api_key={}'.format(self.api_key)
            r = requests.get(url)
            r.raise_for_status()
            r = r.json()['esearchresult']
                
            querytranslation = r['querytranslation']
            retstart = retstart + self.RESULTS_PER_QUERY
            count = int(r['count'])
            pmids = pmids + r['idlist']
            time.sleep(self.time_delay)    
            
                        
        return pmids, count, querytranslation
             
    def __chunk__(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        return [lst[i:i + n] for i in range(0, len(lst), n)]
    
    def __query_articles__(self, pmids, print_xml, chunk_size):
        articles = []
        pmid_chunks = self.__chunk__(pmids, min(chunk_size, self.RESULTS_PER_QUERY))
        print('{} chunks of pmids'.format(len(pmid_chunks)))
        i = 0
        for pmid_chunk in pmid_chunks:
            i += len(pmid_chunk)
            print('\rGetting data on {}/{} articles'.format(i, len(pmids)), end='')
            
            articleList = PubMedArticleList(pmid_chunk, self.BASE_URL, self.DB, self.citedBy, self.time_delay, print_xml, self.api_key)
            articles = articles + articleList.articles
            
        return articles
    
    def __getdataframe__(self):
        df = {'pmid': [],
          'authors': [],
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
    
        for i, article in enumerate(self.articles):
            #print('\r{} : {}'.format(i, article.pmid), end='')
        
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
            #print('\n')
        return pd.DataFrame(df)
    
    
if __name__ == '__main__':
    print('PubMedQuery API')
    
    
    query_text = """
            ("the laryngoscope"[Journal]) AND 
            (("2024/01/01"[Date - Publication] : "2024/12/31"[Date - Publication]))
            """
    query = PubMedQuery(query_text)
    query_df = query.__getdataframe__()
    print(query_df.head())
    print('size: {}'.format(query_df.shape))
    
    
    
    
    
    
