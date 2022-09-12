# Copyright 2018- The Pixie Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
import datetime
from decimal import Decimal
from faker_airtravel import AirTravelProvider
import pandas as pd
from presidio_evaluator.data_generator import PresidioDataGenerator
from presidio_evaluator.data_generator.faker_extensions.providers import NationalityProvider, AgeProvider, AddressProviderNew, PhoneNumberProviderNew, IpAddressProvider
from presidio_evaluator.data_generator.faker_extensions import RecordsFaker
from privy.providers.generic import GenericProvider, OrganizationProvider, Provider
from privy.providers.generic import MacAddress, IMEI, Gender, Passport, DriversLicense, String, TaxID, Religion, Race


# English United States - inherits standard, region-agnostic methods
class English_US(GenericProvider):
    def __init__(self, pii_types=None, locale="en_US"):
        # initialize standard, region-agnostic methods
        super().__init__()
        # read name df if present
        fake_name_generator_file = Path(
            __file__).parent / "america.csv"
        fake_name_generator_file2 = Path(
            __file__).parent / "names_us_misc.csv"
        a = pd.read_csv(fake_name_generator_file)
        b = pd.read_csv(fake_name_generator_file2)
        # fake_name_generator_df = pd.read_csv(fake_name_generator_file)
        fake_name_generator_df = pd.concat([a, b])
        # a = fake_name_generator_df[fake_name_generator_df.CountryFull == "United States"]
        # b = fake_name_generator_df[fake_name_generator_df.CountryFull == "Canada"]
        # c = fake_name_generator_df[fake_name_generator_df.CountryFull == "United Kingdom"]
        # d = fake_name_generator_df[fake_name_generator_df.CountryFull == "Australia"]
        # e = fake_name_generator_df[fake_name_generator_df.CountryFull == "New Zealand"]
        # fake_name_generator_df = pd.concat([a, b, c, d, e])
        print("df has len: ", len(fake_name_generator_df))
        fake_name_generator_df = PresidioDataGenerator.update_fake_name_generator_df(
            fake_name_generator_df)

        # initialize Faker instance with specific Faker locale
        # f = SpanGenerator(locale=locale)
        # sample names, addresses etc. from one person-record for realism
        records_faker = RecordsFaker(
            records=fake_name_generator_df, locale=locale)
        # extend faker with custom providers
        records_faker.add_provider(AirTravelProvider)
        records_faker.add_provider(MacAddress)
        records_faker.add_provider(IMEI)
        records_faker.add_provider(Gender)
        records_faker.add_provider(Passport)
        records_faker.add_provider(DriversLicense)
        records_faker.add_provider(String)
        records_faker.add_provider(TaxID)
        records_faker.add_provider(OrganizationProvider)
        records_faker.add_provider(Religion)
        records_faker.add_provider(Race)
        records_faker.add_provider(DriversLicense)
        # providers by presidio-research
        records_faker.add_provider(NationalityProvider)
        records_faker.add_provider(AgeProvider)
        records_faker.add_provider(AddressProviderNew)
        records_faker.add_provider(PhoneNumberProviderNew)
        records_faker.add_provider(IpAddressProvider)

        f = PresidioDataGenerator(
            custom_faker=records_faker, lower_case_ratio=0.05)
        self.f = f
        # define language/region-specific providers
        self.pii_providers = [
            # ------ Names ------
            Provider(
                template_name="person",
                aliases=set([
                    "full name",
                    "account name",
                    "artist name",
                    "contact name",
                    "login name",
                    "user name",
                    "customer",
                    "user",
                    "target user name",
                    "buyer user name",
                    "shareholder",
                    "owner",
                ])),
            Provider(
                "name_male",
                set([
                    "full name male",
                ]),
            ),
            Provider(
                "name_female",
                set([
                    "full name female",
                ]),
            ),
            Provider(
                "first_name",
                set([
                    "given name",
                    "middle name",
                ]),
            ),
            Provider(
                "first_name_nonbinary",
                set([
                    "given name nonbinary",
                ]),
            ),
            Provider(
                "first_name_male",
                set([
                    "given name male",
                ]),
            ),
            Provider(
                "first_name_female",
                set([
                    "given name female",
                ]),
            ),
            Provider(
                "last_name",
                set([
                    "family name",
                ]),
            ),
            Provider(
                "last_name_male",
                set([
                    "family name male",
                ]),
            ),
            Provider(
                "last_name_female",
                set([
                    "family name female",
                ]),
            ),
            Provider(
                "prefix",
                set(),
            ),
            Provider(
                "prefix_male",
                set(),
            ),
            Provider(
                "prefix_female",
                set(),
            ),
            Provider(
                "organization",
                set([
                    "company",
                    "company name",
                    "department",
                    "manufacturer",
                    "client",
                    "dba",
                    "doing business as",
                    "business name",
                    "business",
                ])),
            Provider(
                "nationality",
                set(),
            ),
            Provider(
                "nation_woman",
                set(),
            ),
            Provider(
                "nation_man",
                set(),
            ),
            Provider(
                "nation_plural",
                set(),
            ),
            Provider(
                "religion",
                set(),
            ),
            # Provider(
            #     "race",
            #     set(),
            # ),
            # ------ Location ------
            Provider(
                "address",
                set([
                    "home",
                    "work",
                    "venue",
                    "place",
                    "spot",
                    "facility",
                ]),
            ),
            Provider(
                "secondary_address",
                set([
                    "home",
                    "work",
                    "venue",
                    "place",
                    "spot",
                    "facility",
                ]),
            ),
            Provider(
                "street_address",
                set([
                    "street",
                    "avenue",
                    "alley",
                ]),
            ),
            Provider(
                "country",
                set([
                    "destination",
                    "origin",
                ]),
            ),
            Provider(
                "country_code",
                set([
                    "to country code",
                    "from country code",
                    "phone country code",
                ]),
            ),
            Provider(
                "state",
                set([
                    "province",
                    "region",
                    "federal state",
                ]),
            ),
            Provider(
                "state_abbr",
                set([
                    "state abbreviation",
                ]),
            ),
            Provider(
                "city",
                set([
                    "bank city",
                    "municipality",
                    "urban area",
                ]),
            ),
            Provider(
                "zipcode",
                set([
                    "post code",
                    "postal code",
                    "zip",
                ]),
            ),
            Provider(
                "building_number",
                set([
                    "house",
                    "building",
                    "apartment",
                ]),
            ),
            Provider(
                "street_name",
                set([
                    "road",
                    "lane",
                    "drive",
                ]),
            ),
            Provider(
                "coordinate",
                set([
                    "location",
                    "position",
                ]),
                Decimal),
            Provider(
                "latitude",
                set([
                    "lat",
                ]),
                Decimal),
            Provider(
                "longitude",
                set([
                    "lon",
                ]),
                Decimal),
            Provider(
                "airport_name",
                set([
                    "airport",
                ]),
            ),
            Provider(
                "airport_iata",
                set([
                    "airport code",
                    "origin airport code",
                    "arrival airport code",
                    "destination airport code",
                ]),
            ),
            Provider(
                "airport_icao",
                set(),
            ),
            Provider(
                "airline",
                set(["arline name"]),
            ),
            # ------ Financial ------
            Provider(
                "bban",
                set([
                    "bank_account_number",
                    "bank account",
                    "bic",
                ]),
            ),
            Provider(
                "aba",
                set([
                    "routing_transit_number",
                    "routing number",
                ]),
            ),
            Provider(
                "iban",
                set([
                    "international_bank_account_number",
                ]),
            ),
            Provider(
                "credit_card_number",
                set([
                    "credit card",
                    "debit card",
                    "master card",
                    "visa",
                    "american express",
                ]),
            ),
            Provider(
                "credit_card_expire",
                set([
                    "credit_card_expiration_date",
                    "expiration date",
                    "expiration",
                    "expires",
                ]),
            ),
            Provider(
                "swift",
                set([
                    "swift code",
                ]),
            ),
            Provider(
                "currency_code",
                set([
                    "fare currency",
                    "currency",
                ]),
            ),
            # ------ Time ------
            Provider(
                "age",
                set(),
            ),
            Provider(
                "day_of_week",
                set([
                    "week day",
                ]),
            ),
            Provider(
                "date_of_birth",
                set([
                    "birth day",
                    "birth date",
                ]),
                datetime.date),
            Provider(
                "date",
                set([
                    "modified date",
                    "from booking date",
                    "to booking date",
                    "open date",
                    "to date",
                    "published",
                    "day",
                    "departure date",
                    "return date",
                    "start date",
                    "end date",
                    "travel date",
                    "from date",
                    "install date",
                ]),
            ),
            Provider(
                "year",
                set([
                    "birth year",
                ]),
            ),
            Provider(
                "month",
                set([
                    "birth month",
                ]),
            ),
            Provider(
                "date_time",
                set([
                    "from statement date time",
                    "to statement date time",
                    "time stamp",
                    "last timestamp",
                    "last modified",
                    "modified after",
                    "modified before",
                    "from timestamp",
                    "to timestamp",
                    "end time",
                    "start time",
                    "last updated",
                    "created",
                    "unix time",
                    "start",
                    "end",
                ]),
            ),
            # ------ Identification ------
            Provider(
                "ssn",
                set([
                    "social_security_number",
                    "id number",
                    "id card",
                ]),
            ),
            Provider(
                "passport",
                set([
                    "passport",
                    "passport number",
                    "document number",
                    "identity document",
                    "national identity",
                ]),
            ),
            Provider(
                "driver_license",
                set([
                    "driving license",
                    "driver's license",
                    "drivers license",
                    "driver license",
                ]),
            ),
            Provider(
                "license_plate",
                set([
                    "lic plate",
                ]),
            ),
            Provider(
                "itin",
                set([
                    "tax identification number",
                    "taxpayer identification number",
                    "tax id",
                ])
            ),
            # ------ Contact Info ------
            Provider(
                "email",
                set([
                    "email address",
                    "contact email",
                    "to contact",
                ]),
            ),
            Provider(
                "phone_number",
                set([
                    "phone",
                    "contact phone",
                    "associate phone number",
                ]),
            ),
            # ------ Demographic ------
            Provider(
                "gender",
                set([
                    "sexuality",
                    "sex",
                ]),
            ),
            Provider(
                "job",
                set([
                    "occupation",
                    "profession",
                    "employment",
                    "vocation",
                    "career",
                ]),
            ),
            # ------ Internet / Devices ------
            Provider(
                "domain_name",
                set([
                    "domain",
                ]),
            ),
            Provider(
                "url",
                set([
                    "website",
                    "repository",
                    "url",
                    "site",
                    "host name",
                ]),
            ),
            Provider(
                "ip_address",
                set([
                    "ipv4",
                    "ipv6",
                ]),
            ),
            Provider(
                "mac_address",
                set([
                    "device mac",
                    "mac_address__nie",
                ]),
            ),
            Provider(
                "imei",
                set([
                    "international mobile equipment identity"
                ]),
            ),
            Provider(
                "password",
                set([
                    "key password",
                    "key store password",
                    "current password",
                ]),
            ),
        ]
        self.nonpii_providers = [
            Provider(
                template_name="string",
                aliases=set(["string", "text", "message"]),
                type_=str,
            ),
            Provider(
                "boolean",
                set(["bool"]),
                bool,
            ),
            Provider(
                "color",
                set(["hue", "colour"]),
            ),
            Provider(
                "random_number",
                set(["integer", "int", "number", "to number", "from number"]),
                int,
            ),
            Provider(
                "sha1",
                set(["signature sha1", "serial", "app key",
                    "id", "org id", "statement id", "device id",
                    "item uuid", "vault uuid"]),
            ),
        ]
        # filter providers, marking providers matching given pii_types as pii
        self.filter_providers(pii_types)
        # insert versions of aliases with different delimiters
        self.add_delimited_aliases(self.pii_providers)
        self.add_delimited_aliases(self.nonpii_providers)
        # add aliases for all providers
        self.f.add_provider_alias(provider_name="name", new_name="person")
        self.f.add_provider_alias(
            provider_name="credit_card_number", new_name="credit_card"
        )
        self.f.add_provider_alias(
            provider_name="date_of_birth", new_name="birthday"
        )

        # self.set_provider_aliases()
