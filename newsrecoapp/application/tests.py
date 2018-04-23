# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase
from newsrecoapp.application.retrieval.data_retrieval import NewsRetrieval
from newsrecoapp.application.extractor.textrazor import Extraction
# Create your tests here.


class TestDataRetrieval(TestCase):
    """Test the access key."""

    def test_newsapi(self):
        """Check the connectivity using the newsapi key."""
        dataRetrieval = NewsRetrieval()
        print(dataRetrieval)
        self.assertTrue(dataRetrieval.check_connectivity_using_key())

class TestTextExtractor(TestCase):
    """Test the text razor keyword extraction"""

    def test_textrazorapi(self):
        """Check if the keyword extraction is happening using textrazor api"""
        extract = Extraction()
        self.assertTrue(extract.check_extraction_using_key())
