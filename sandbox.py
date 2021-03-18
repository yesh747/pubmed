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
import datetime 


BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
DB = 'pubmed'
RESULTS_PER_QUERY = 2000


query = 'eleanor gerhard'
retstart = 0
count = 999999999


# TODO:
    # - put in email into my request
    # - create a query class


class PubMedArticle():
    def __init__(self, root):
        self.root = root
        self.pmid = self.root.find('./PubmedArticle/MedlineCitation/PMID').text
        articlePath = './PubmedArticle/MedlineCitation/Article/'
        
        
        # METADATA
        self.journal = self.root.find(articlePath + 'Journal/Title').text
        self.journal_abbr = self.root.find(articlePath + 'Journal/ISOAbbreviation').text
        self.pubtype = self.root.find(articlePath + 'PublicationTypeList/PublicationType').text
        
        # DATE
        year = self.root.find(articlePath + 'Journal/JournalIssue/PubDate/Year').text
        month = self.root.find(articlePath + 'Journal/JournalIssue/PubDate/Month').text
        try:
            day = self.root.find(articlePath + 'Journal/JournalIssue/PubDate/Day').text
        except AttributeError:
            day = '1'
        
        self.pubdate = {'year': year, 'month': month, 'day': day}
        
        self.title = self.root.find(articlePath + 'ArticleTitle').text
        
        # abstract
        self.abstract = self.root.find(articlePath + 'Abstract/AbstractText')
        self.abstract = ''.join(self.abstract.itertext())
        
        # authors
        authorlist = self.root.findall(articlePath + '/AuthorList/Author')
        self.authors = []
        for author in authorlist:
            self.authors.append({
                'lastname': author.find('LastName').text,
                'firstname': author.find('ForeName').text,
                'initials': author.find('Initials').text,
                'affiliation': ''.join(author.find('AffiliationInfo/*').itertext())
                })
        
    def print_xml(self):
        print(xml.tostring(self.root, encoding='utf8').decode('utf8'))

    
idlist = []
while retstart < count:
    url = '{}esearch.fcgi?db={}&term={}&retmax={}&retmode=json&usehistory=y&retstart={}'.format(
        BASE_URL, DB, query, RESULTS_PER_QUERY, retstart)
    r = requests.get(url)
    r.raise_for_status()
    r = r.json()['esearchresult']
    r
    count = int(r['count'])
    retstart = retstart + RESULTS_PER_QUERY
    idlist = idlist + r['idlist']
    time.sleep(1)

print(r['idlist'])


articles = []
for pmid in idlist:
    url = '{}efetch.fcgi?db={}&id={}&retmode=xml'.format(BASE_URL, DB, pmid)
    r = requests.get(url)
    r.raise_for_status()
    root = xml.fromstring(r.text)
    
    article = PubMedArticle(root)
    articles.append(article)
    time.sleep(1)
    
articles[0].print_xml()
    
    
    
    
    
    
    
    
    