#!/usr/bin/env python3

""" Computer-based immigration office for Kanadia """

__author__ = 'Peymon'
__email__ = "peymon@peymon.com"

__copyright__ = "2014 Peymon"
__license__ = "MIT License"

__status__ = "Prototype"

# imports one per line
import re
import datetime
import json
from datetime import *


def decide(input_file, watchlist_file, countries_file):
    """
    Decides whether a traveller's entry into Kanadia should be accepted

    :param input_file: The name of a JSON formatted file that contains cases to decide
    :param watchlist_file: The name of a JSON formatted file that contains names and passport numbers on a watchlist
    :param countries_file: The name of a JSON formatted file that contains country data, such as whether
        an entry or transit visa is required, and whether there is currently a medical advisory
    :return: List of strings. Possible values of strings are: "Accept", "Reject", "Secondary", and "Quarantine"
    """

    with open(input_file, "r") as input_file_reader:
        traveller_information = input_file_reader.read()
        traveller_information_output = json.loads(traveller_information)
    with open(countries_file, "r") as countries_file_reader:
        countries_file_contents = countries_file_reader.read()
        countries_file_output = json.loads(countries_file_contents)
    with open(watchlist_file, "r") as watchlist_file_reader:
        watchlist_file_contents = watchlist_file_reader.read()
        watchlist_file_output = json.loads(watchlist_file_contents)
    # function beings testing
    decision = {"Quarantine": "", "Reject": "", "Secondary": ""}
    decision_list = []
    for traveller in traveller_information_output:
        if incompleteness(traveller):
            decision["Reject"] = True
        elif quarantine(traveller, countries_file_output):
            decision["Quarantine"] = True
        elif not valid_visa(traveller, countries_file_output):
            decision["Reject"] = True
        elif watchlist(traveller, watchlist_file_output):
            decision["Secondary"] = True

        if decision["Quarantine"]:
            decision_list.append("Quarantine")
        elif decision["Reject"]:
            decision_list.append("Reject")
        elif decision["Secondary"]:
            decision_list.append("Secondary")
        else:
            decision_list.append("Accept")

    return decision_list


def returning_home(traveller):
    home_state= False

    if traveller["home"]["country"].lower() == "kan":
        return True



def quarantine(q_traveller, q_countries_file):
    """check if the traveller needs to be quarantined
    :param traveller: dictionary of traveller info
    :param countries_file: the current watchlist dictionary from json file
    :return: quarantine_state; True if needs to be quarantined, False otherwise
    """
    quarantine_state = False
    if "via" in q_traveller:
        if q_countries_file[q_traveller["via"]["country"].upper()]["medical_advisory"]:
            quarantine_state = True
    elif "from" in q_traveller:
        if q_countries_file[q_traveller["from"]["country"].upper()]["medical_advisory"]:
            quarantine_state = True
    return quarantine_state


def incompleteness(traveller_info):
    """check if the traveller info has every required field
    :param traveller_info: list of traveller info
    :return: completeness_state; True if has everything, False otherwise
    """
    incomplete = False
    req_field = ["passport", "first_name", "last_name", "birth_date", "home",
                 "entry_reason", "from"]
    for field in req_field:
        if field not in traveller_info:
            incomplete = True
    print ("incomplete state before checking visa validity state is", incomplete)

    if not valid_date_format("birth_date") or \
            not valid_visa_date_format(traveller_info["visa"]["date"]) or \
            not valid_visa_code_format(traveller_info["visa"]["code"]) or \
            not valid_passport_format("passport"):
        incomplete = True
    print ("incomplete state is", incomplete)
    return incomplete


def valid_visa(traveller, countries_file):
    """check if the traveller has valid visa if need
    :param traveller: list of traveller info
    :param countries_file: the current countries file from json file
    :return: visa_state; True if visa is within 2 years, False otherwise
    """
    today = date.today()
    year = timedelta(days=365)
    cut_off_date = today - year * 2
    visa_state = False
    if returning_home(traveller):
        visa_state = True
    elif traveller["entry_reason"].lower() == "returning" and traveller["home"]["country"].upper() == "KAN":
        visa_state = True
        return
    elif traveller["entry_reason"].lower() == "visit":
        if countries_file[traveller["from"]["country"].upper()]["visitor_visa_required"] == "0":
            visa_state = True
        elif traveller["visa"]["date"] >= str(cut_off_date):
            visa_state = True
    elif traveller["entry_reason"].lower() == "transit":
        if countries_file[traveller["from"]["country"].upper()]["transit_visa_required"] == "0":
            visa_state = True
        elif traveller["visa"]["date"] >= str(cut_off_date):
            visa_state = True
    print ("valid visa is ", visa_state)
    return visa_state


def watchlist(traveller, watchlist_file):
    """check if the traveller is in watchlist
    :param traveller: list of traveller info
    :param watchlist_file: the current watchlist file from json file
    :return: watchlist_state; True if in watchlist, False otherwise
    """
    watchlist_state = False
    for watchlist_person in watchlist_file:
        if traveller["first_name"].lower() == watchlist_person["first_name"].lower() and traveller[
            "last_name"].lower() == watchlist_person["last_name"].lower():
            watchlist_state = True
        elif traveller["passport"].upper() == watchlist_person["passport"].upper():
            watchlist_state = True
    return watchlist_state

def valid_date_format(date_string):
    """
    Checks whether a date has the format YYYY-mm-dd in numbers
    :param date_string: date to be checked
    :return: Boolean True if the format is valid, False otherwise
    """
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

'''def valid_date_format(date_string):
    """
    Checks whether a date has the format YYYY-mm-dd in numbers
    :param date_string: date to be checked
    :return: Boolean True if the format is valid, False otherwise
    """
    date_format = re.compile('.{4}-.{2}-.{2}')
    if date_format.match(date_string):
        print("Birthdate is gooz")
        return True
    else:
        print("Birthdate no gooz")
        return False
'''
def valid_visa_date_format(visa_date):
    try:
        datetime.strptime(visa_date, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def valid_visa_code_format(visa_code):
    code_format = re.compile('.{5}-.{5}')
    if code_format.match(visa_code):
        return True
    else:
        return False

def valid_passport_format(passport_number):
    """
    Checks whether a passport number is five sets of five alpha-number characters separated by dashes
    :param passport_number: alpha-numeric string
    :return: Boolean; True if the format is valid, False otherwise
    """
    passport_format = re.compile('.{5}-.{5}-.{5}-.{5}-.{5}')

    if passport_format.match(passport_number):
        return True
    else:
        return False





