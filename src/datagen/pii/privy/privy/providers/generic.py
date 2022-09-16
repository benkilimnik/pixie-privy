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

import logging
import yaml
import dataclasses
import random
import string
from abc import ABC
from typing import Union, Optional, Type, Callable, Set
from decimal import Decimal
import pandas as pd
from pathlib import Path
import baluhn
from faker.providers import BaseProvider
from faker.providers.lorem.en_US import Provider as LoremProvider
from presidio_evaluator.data_generator.faker_extensions.data_objects import FakerSpansResult


@dataclasses.dataclass()
class Provider:
    """Provider holds information related to a specific (non-)PII provider.
    each provider has a name, a set of aliases, and a faker generator."""

    template_name: str
    aliases: Set[str]
    type_: Union[Type[str], Type[int], Type[float],
                 Type[Decimal], Type[bool]] = str

    def __repr__(self):
        return str(vars(self))


class GenericProvider(ABC):
    """Parent class containing common methods shared by region specific providers"""

    def __init__(self):
        pass

    def get_pii_types(self) -> list[str]:
        """Return all pii types in the pii_label_to_provider dict"""
        return [provider.template_name for provider in self.pii_providers]

    def get_delimited(self, label: str) -> list[str]:
        """Return list of versions of input label with different delimiters"""
        label_delimited = [
            label,
            label.replace(" ", "-"),
            label.replace(" ", "_"),
            label.replace(" ", "__"),
            label.replace(" ", ""),
        ]
        return label_delimited

    def add_delimited_aliases(self, providers: list[Provider]) -> None:
        """Add copies of existing aliases for each provider with different delimiters"""
        for prov in providers:
            prov.aliases.add(prov.template_name)
            aliases_to_add = set()
            for alias in prov.aliases:
                for delimited_alias in self.get_delimited(alias):
                    aliases_to_add.add(delimited_alias)
            prov.aliases = prov.aliases.union(aliases_to_add)

    def get_pii_provider(self, name: str) -> Optional[Provider]:
        """Find PII provider that matches input name. Returns None if no match is found."""
        if not name:
            return
        for provider in self.pii_providers:
            if name.lower() == provider.template_name or name.lower() in provider.aliases:
                return provider

    def get_nonpii_provider(self, name: str) -> Optional[Provider]:
        """Find non-PII provider that matches input name. Returns None if no match is found."""
        if not name:
            return
        for provider in self.nonpii_providers:
            if name.lower() == provider.template_name or name.lower() in provider.aliases:
                return provider

    def get_random_pii_provider(self) -> Provider:
        """choose random PII provider and generate a value"""
        return random.choice(list(self.pii_providers))

    def sample_pii_providers(self, percent: float) -> list[Provider]:
        """Sample a random percentage of PII providers and associated values"""
        return random.sample(list(self.pii_providers), round(len(self.pii_providers) * percent))

    def filter_providers(self, pii_types: list[str]) -> None:
        """Filter out PII types not in the given list, marking them as non-PII"""
        if not pii_types:
            pii_types = self.get_pii_types()

    def get_faker(self, faker_provider: str):
        faker_generator = getattr(self.f.faker, faker_provider)
        return faker_generator

    # def add_provider_alias(self, provider: Callable, alias: str) -> None:
    #     """Add copy of an existing provider, but under a different name"""
    #     logging.getLogger("privy").debug(
    #         f"Adding alias {alias} for provider {provider}")
    #     new_provider = BaseProvider(self.f)
    #     setattr(new_provider, alias, provider)
    #     self.f.add_provider(new_provider)

    # def set_provider_aliases(self):
    #     """Set faker generator aliases for all providers to reduce mismatch between template_names and generators"""
    #     for pii in self.pii_providers:
    #         add_provider_alias(
    #             provider=getattr(self.f, pii.template_name), alias=pii.template_name)
    #     for nonpii in self.nonpii_providers:
    #         self.add_provider_alias(
    #             provider=nonpii.generator, alias=nonpii.template_name)

    def parse(self, template: str, template_id: int) -> FakerSpansResult:
        """Parse payload template into a span, using data providers that match the template_names e.g. {{full_name}}"""
        return self.f.parse(template=template, template_id=template_id)


class MacAddress(BaseProvider):
    def mac_address(self) -> str:
        pattern = random.choice(
            [
                "^^:^^:^^:^^:^^:^^",
                "^^-^^-^^-^^-^^-^^",
                "^^ ^^ ^^ ^^ ^^ ^^",
            ]
        )
        return self.hexify(pattern)


class IMEI(BaseProvider):
    def imei(self) -> str:
        imei = self.numerify(text="##-######-######-#")
        while baluhn.verify(imei.replace("-", "")) is False:
            imei = self.numerify(text="##-######-######-#")
        return imei


class Gender(BaseProvider):
    def gender(self) -> str:
        return random.choice(["Male", "Female", "Other"])


class Passport(BaseProvider):
    def passport(self) -> str:
        # US Passports consist of 1 letter or digit followed by 8-digits
        return self.bothify(text=random.choice(["?", "#"]) + "########")


class DriversLicense(BaseProvider):
    def __init__(self, generator):
        super().__init__(generator=generator)
        self.us_driver_license_formats = Path(
            Path(__file__).parent, "us_driver_license_format.yaml"
        ).resolve()
        with open(self.us_driver_license_formats, "r") as stream:
            try:
                formats = yaml.safe_load(stream)
                self.formats = formats['en']['faker']['driving_license']['usa']
            except yaml.YAMLError as exc:
                logging.getLogger("privy").warning(exc)

    def driver_license(self) -> str:
        # US driver's licenses patterns vary by state. Here we sample a random state and format
        us_state = random.choice(list(self.formats))
        us_state_format = random.choice(self.formats[us_state])
        return self.bothify(text=us_state_format)


class Alphanum(BaseProvider):
    def alphanum(self) -> str:
        alphanumeric_string = "".join(
            [random.choice(["?", "#"])
                for _ in range(random.randint(1, 15))]
        )
        return self.bothify(text=alphanumeric_string)


class ITIN(BaseProvider):
    def itin(self) -> str:
        # US Individual Taxpayer Identification Number (ITIN).
        # Nine digits that start with a "9" and contain a "7" or "8" as the 4 digit.
        return f"9{self.numerify(text='##')}{random.choice(['7', '8'])}{self.numerify(text='#####')}"


class String(LoremProvider):
    def string(self) -> str:
        """generate a random string of characters, words, and numbers"""
        def sample(text, low, high, space=False):
            """sample randomly from input text with a minimum length of low and maximum length of high"""
            space = " " if space else ""
            return space.join(random.sample(text, random.randint(low, high)))

        characters = sample(string.ascii_letters, 1, 10)
        characters_and_numbers = sample(
            string.ascii_letters + string.digits, 1, 10)
        combined = [characters, characters, characters_and_numbers]
        return sample(combined, 0, 3, space=True)


class OrganizationProvider(BaseProvider):
    def __init__(self, generator):
        super().__init__(generator=generator)
        # company names assembled from stock exchange listings (aex, bse, cnq, ger, lse, nasdaq, nse, nyse, par, tyo),
        # US government websites like https://www.sec.gov/rules/other/4-460list.htm, and other sources
        self.orgs_and_companies_file = Path(
            Path(__file__).parent, "companies_and_organizations.csv"
        ).resolve()
        self.orgs_and_companies = self.load_organizations()

    def load_organizations(self):
        return pd.read_csv(self.orgs_and_companies_file)

    def company(self):
        return self.organization()

    def organization(self):
        return self.random_element(self.orgs_and_companies.companyName.tolist())


class Religion(BaseProvider):
    def religion(self) -> str:
        """Return a random (major) religion."""
        return random.choice([
            'Atheism',
            'Atheist',
            'Christianity',
            'Christian',
            'Islam',
            'Islamic',
            'Hinduism',
            'Hindu',
            'Buddhism',
            'Buddhist',
            'Sikhism',
            'Sikh',
            'Judaism',
            'Jewish',
            'Bahaism',
            'Baha',
            'Confucianism',
            'Confucian',
            'Jainism',
            'Jain',
            'Shintoism',
            'Shinto',
        ])


class Race(BaseProvider):
    def race(self) -> str:
        """Return a random race."""
        return random.choice([
            'Alien/Unknown',
            'Aboriginal/Australian, South Pacific',
            'Aborigine',
            'African',
            'African/African-American/Black',
            'African-American',
            'African-American/Black',
            'American',
            'American Indian',
            'Arabian',
            'Arabic',
            'Arab/Middle Eastern',
            'Asian',
            'Asian/-American',
            'Asian/Indian',
            'Asian/Oriental',
            'Asian/Other than American',
            'Asian/Mongoloid',
            'Asian/Subcontinent',
            'Asian/Pacific',
            'Bi/multiracial',
            'Black',
            'Black/African',
            'Black/African descent',
            'Black/African-American',
            'Black/American',
            'Black/Central-Southern African',
            'Black/Other than American',
            'Brown/Hispanic',
            'Caucasion',
            'Caucasion/White',
            'Chinese',
            'Combination',
            'Eastern Indian',
            'Eskimo',
            'Eskimo/Aleutian',
            'European',
            'Filipino',
            'Hispanic',
            'Hispanic/American',
            'Hispanic/Latin',
            'Hispanic/Latino',
            'Hispanic/Other than American',
            'Human',
            'Indian',
            'Indian/Middle Asian',
            'Indian/Native American or otherwise',
            'Indian/Pakistani',
            'Islander',
            'Japanese',
            'Jewish',
            'Korean',
            'Latina',
            'Latino',
            'Latino/a',
            'Latino/Hispanic',
            'Mestiza/Mixed',
            'Mexican',
            'Middle Eastern',
            'Middle Eastern/American',
            'Middle Eastern/Arabic',
            'Middle Eastern/Other than American',
            'Mixed',
            'Mixes',
            'Mix of some',
            'Native American',
            'Native American/Aborigine',
            'Native American/Indian',
            'Native American/Indigenous People',
            'Oriental',
            'Pacific Islander',
            'Pacific Islander/East Asian',
            'Polynesian/Pacific Islander',
            'South American/Latin American descent',
            'Vietnamese',
            'White',
            'White/American',
            'White/Caucasian',
            'White/European',
            'White/Northern European',
            'White/Other than American',
            'Yellow/Asian/Pacific Islander/Native American',
        ])
