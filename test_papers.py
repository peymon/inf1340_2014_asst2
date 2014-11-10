#!/usr/bin/env python3

""" Module to test papers.py  """

__author__ = 'Peymon'
__email__ = "peymon@peymon.com"

__copyright__ = "2014 Peymon"
__license__ = "MIT License"

__status__ = "Prototype"

# imports one per line
import json
import pytest
from papers import decide


def test_basic():
    assert decide("test_returning_citizen.json", "watchlist.json", "countries.json") == ["Accept", "Accept"]
    assert decide("test_watchlist.json", "watchlist.json", "countries.json") == ["Secondary"]
    assert decide("test_quarantine.json", "watchlist.json", "countries.json") == ["Quarantine"]
    assert decide("test_invalid_visa.json", "watchlist.json", "countries.json") == ["Reject", "Reject"]
    assert decide("incomplete_entries.json", "watchlist.json", "countries.json") == ["Reject"]


def test_files():
    with pytest.raises(FileNotFoundError):
        decide("test_returning_citizen.json", "", "countries.json")


def test_files():
    with pytest.raises(FileNotFoundError):
        decide("test_returning_citizen.json", "watchlist.json", "")


test_basic()
test_files()
