#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sandboxing with pubmed api

Created on Wed Mar 17 19:08:14 2021

@author: yesh
"""
import time
import requests
import xml.etree.ElementTree as xml



# TODO:
    # - put in email into my request


class PubMedArticle():
    def __init__(self, pmid, BASE_URL, DB, print_xml=False):
        # get article
        url = '{}efetch.fcgi?db={}&id={}&retmode=xml'.format(BASE_URL, DB, pmid)
        r = requests.get(url)
        r.raise_for_status()
        root = xml.fromstring(r.text)
        

        self.root = root
        if print_xml:
            self.print_xml()
            
            
        self.pmid = pmid
        articlePath = './PubmedArticle/MedlineCitation/Article/'
            
        # METADATA
        self.journal = self.root.find(articlePath + 'Journal/Title').text
        self.journal_abbr = self.root.find(articlePath + 'Journal/ISOAbbreviation').text
        self.pubtype = self.root.find(articlePath + 'PublicationTypeList/PublicationType').text
        
        # DATE
        pubdate = self.root.find('./PubmedArticle/PubmedData/History/PubMedPubDate[@PubStatus="pubmed"]')
        year = pubdate.find('Year').text
        month = pubdate.find('Month').text
        day = pubdate.find('Day').text
        
        self.pubdate = {'year': year, 'month': month, 'day': day}
        
        self.title = self.root.find(articlePath + 'ArticleTitle').text
        
        # abstract
        self.abstract = self.root.findall('.//AbstractText')
        # need this step for when there are multiple abstract text objects
        self.abstract = ' '.join([''.join(section.itertext()) for section in self.abstract])
        
        # authors
        authorlist = self.root.findall(articlePath + '/AuthorList/Author')
        self.authors = []
        for author in authorlist:        
            affiliation_xml = author.find('AffiliationInfo/*')
            if affiliation_xml is not None:
                affiliation = ''.join(author.find('AffiliationInfo/*').itertext())
            else:
                affiliation = ''
            self.authors.append({
                'lastname': author.find('LastName').text,
                'firstname': author.find('ForeName').text,
                'initials': author.find('Initials').text,
                'affiliation': affiliation,
                })
        
    def print_xml(self):
        print(xml.tostring(self.root, encoding='utf8').decode('utf8'))



class PubMedQuery():
    def __init__(self, query,
                 BASE_URL='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/', 
                 DB='pubmed',
                 RESULTS_PER_QUERY=1000,
                 limit = 100,
                 print_xml=False):
        self.BASE_URL = BASE_URL
        self.DB = DB
        self.RESULTS_PER_QUERY = RESULTS_PER_QUERY
        self.query = query
        
        # query
        self.pmids, self.count, self.querytranslation, self.max_results = self.__query_pmids__(self.query, limit)
        print('{}/{} results for: {}'.format(self.count, self.max_results, self.querytranslation))

        self.articles = self.__query_articles__(self.pmids, limit, print_xml)
        
        
    def __query_pmids__(self, query, limit):
        pmids = []
        retstart = 0
        if limit:
            count = limit
        else:
            count = 999999
        
        while retstart < count:  
            url = '{}esearch.fcgi?db={}&term={}&retmax={}&retmode=json&usehistory=y&retstart={}'.format(
                    self.BASE_URL, self.DB, self.query, self.RESULTS_PER_QUERY, retstart)
            r = requests.get(url)
            r.raise_for_status()
            r = r.json()['esearchresult']
            querytranslation = r['querytranslation']
            retstart = retstart + self.RESULTS_PER_QUERY
            pmids = pmids + r['idlist']
            time.sleep(0.34)     
            if not limit:
                count = int(r['count'])
            
        max_results = r['count']
            
        return pmids, count, querytranslation, max_results
             
    
    def __query_articles__(self, pmids, limit, print_xml):
        articles = []
        for pmid in pmids:
            if len(articles) > limit:
                break
            
            article = PubMedArticle(pmid, self.BASE_URL, self.DB, print_xml)
            articles.append(article)
            time.sleep(0.34)
            

        return articles
    
    
if __name__ == '__main__':
    
    
    query = PubMedQuery('"(Head Neck"[Journal]) AND ("2018"[Date - Publication] : "2019"[Date - Publication])',
                        limit=10) 
    
    
    for article in query.articles:
        print('-'*200)
        print(article.title)
        print(article.abstract)
        print(article.pubdate)
        print(article.authors)

    
    
    
    
    
    
    
    
    
    