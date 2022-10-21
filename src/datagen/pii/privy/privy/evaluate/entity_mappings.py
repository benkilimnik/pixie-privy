PRIVY_ENTITIES = {
    "person": "PERSON",
    "name_male": "PERSON",
    "name_female": "PERSON",
    "first_name": "PERSON",
    "first_name_male": "PERSON",
    "first_name_female": "PERSON",
    "first_name_nonbinary": "PERSON",
    "last_name": "PERSON",
    "last_name_male": "PERSON",
    "last_name_female": "PERSON",

    "address": "STREET_ADDRESS",
    "street_address": "STREET_ADDRESS",
    "zipcode": "STREET_ADDRESS",
    "building_number": "STREET_ADDRESS",
    "street_name": "STREET_ADDRESS",
    "airport_name": "STREET_ADDRESS", #
    # "airport_iata": "STREET_ADDRESS", #
    # "airport_icao": "STREET_ADDRESS", #

    "nationality": "NRP",
    "nation_woman": "NRP",
    "nation_man": "NRP",
    "nation_plural": "NRP",
    "religion": "NRP", #

    "country": "GPE",
    "country_code": "GPE",
    "state": "GPE",
    "state_abbr": "GPE", #
    "city": "GPE",

    "date": "DATE_TIME",
    "date_time": "DATE_TIME",
    "date_of_birth": "DATE_TIME",
    "day_of_week": "DATE_TIME",
    "year": "DATE_TIME",
    "month": "DATE_TIME",

    "url": "URL",
    "domain_name": "URL",

    "credit_card_number": "CREDIT_CARD",
    "credit_card_expire": "DATE_TIME",

    "iban": "IBAN_CODE",
    # "bban": "US_BANK_NUMBER", #
    "phone_number": "PHONE_NUMBER",
    "ssn": "US_SSN",
    # "passport": "US_PASSPORT", #
    "driver_license": "US_DRIVER_LICENSE",
    "ip_address": "IP_ADDRESS",
    "itin": "US_ITIN",
    "email": "EMAIL_ADDRESS",

    "organization": "ORGANIZATION",
    "company": "ORGANIZATION",
    "airline": "ORGANIZATION",

    "job": "TITLE",
    "prefix": "TITLE",
    "prefix_male": "TITLE",
    "prefix_female": "TITLE",
    "gender": "TITLE",

    "coordinate": "COORDINATE",
    "longitude": "COORDINATE",
    "latitude": "COORDINATE",

    "imei": "IMEI",
    "password": "PASSWORD",
    "license_plate": "LICENSE_PLATE",
    "currency_code": "CURRENCY",
    "aba": "ROUTING_NUMBER",
    "swift": "SWIFT_CODE",
    "mac_address": "MAC_ADDRESS",
    "age": "AGE",
}

PRIVY_CUSTOM_ENTITIES = {
    "person": "PERSON",
    "name_male": "PERSON",
    "name_female": "PERSON",
    "first_name": "PERSON",
    "first_name_male": "PERSON",
    "first_name_female": "PERSON",
    "first_name_nonbinary": "PERSON",
    "last_name": "PERSON",
    "last_name_male": "PERSON",
    "last_name_female": "PERSON",

    "address": "STREET_ADDRESS",
    "street_address": "STREET_ADDRESS",
    "zipcode": "STREET_ADDRESS",
    "building_number": "STREET_ADDRESS",
    "street_name": "STREET_ADDRESS",
    "airport_name": "STREET_ADDRESS", #
    "airport_iata": "STREET_ADDRESS", #
    "airport_icao": "STREET_ADDRESS", #

    "nationality": "NRP",
    "nation_woman": "NRP",
    "nation_man": "NRP",
    "nation_plural": "NRP",
    "religion": "NRP", #

    "country": "GPE",
    "country_code": "GPE",
    "state": "GPE",
    "state_abbr": "GPE", #
    "city": "GPE",

    "date": "DATE_TIME",
    "date_time": "DATE_TIME",
    "date_of_birth": "DATE_TIME",
    "day_of_week": "DATE_TIME",
    "year": "DATE_TIME",
    "month": "DATE_TIME",

    # "url": "URL",
    # "domain_name": "URL",

    # "credit_card_number": "CREDIT_CARD",
    "credit_card_expire": "DATE_TIME",

    # "iban": "IBAN_CODE",
    # "bban": "US_BANK_NUMBER", #
    # "phone_number": "PHONE_NUMBER",
    # "ssn": "US_SSN",
    # "passport": "US_PASSPORT", #
    # "driver_license": "US_DRIVER_LICENSE",
    # "ip_address": "IP_ADDRESS",
    # "itin": "US_ITIN",
    # "email": "EMAIL_ADDRESS",

    "organization": "ORGANIZATION",
    "company": "ORGANIZATION",
    "airline": "ORGANIZATION",

    "job": "TITLE",
    "prefix": "TITLE",
    "prefix_male": "TITLE",
    "prefix_female": "TITLE",
    "gender": "TITLE",

    # "coordinate": "COORDINATE",
    # "longitude": "COORDINATE",
    # "latitude": "COORDINATE",

    # "imei": "IMEI",
    # "password": "PASSWORD",
    # "license_plate": "LICENSE_PLATE",
    # "currency_code": "CURRENCY",
    # "aba": "ROUTING_NUMBER",
    # "swift": "SWIFT_CODE",
    # "mac_address": "MAC_ADDRESS",
    # "age": "AGE",
}

PRIVY_PRESIDIO_TRANSLATOR = {
    "PERSON": "PERSON",
    "NRP": "NRP",
    "STREET_ADDRESS": "LOCATION",
    "GPE": "LOCATION",
    "DATE_TIME": "DATE_TIME",
    "CREDIT_CARD": "CREDIT_CARD",
    "URL": "URL",
    "DOMAIN_NAME": "URL",
    "IBAN_CODE": "IBAN_CODE",
    "US_BANK_NUMBER": "US_BANK_NUMBER",
    "PHONE_NUMBER": "PHONE_NUMBER",
    "US_SSN": "US_SSN",
    "US_PASSPORT": "US_PASSPORT",
    "US_DRIVER_LICENSE": "US_DRIVER_LICENSE",
    "IP_ADDRESS": "IP_ADDRESS",
    "EMAIL_ADDRESS": "EMAIL_ADDRESS",
}

PRIVY_ONTONOTES_TRANSLATOR = {
    "PERSON": "PERSON",
    "NRP": "NORP",
    "STREET_ADDRESS": "LOC",
    "GPE": "GPE",
    "DATE_TIME": "DATE",
    "ORGANIZATION": "ORG",
}

PRIVY_CONLL_TRANSLATOR = {
    "PERSON": "PERSON",
    "NRP": "MISC",
    "STREET_ADDRESS": "LOC",
    "GPE": "LOC",
    "ORGANIZATION": "ORG",
}
