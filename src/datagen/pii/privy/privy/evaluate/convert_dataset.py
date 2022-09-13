import argparse
import ast
from pathlib import Path
from typing import List
from datetime import date
from copy import deepcopy
import spacy
from privy.evaluate.entity_mappings import PRIVY_ENTITIES
from presidio_evaluator.data_objects import InputSample
from presidio_evaluator.validation import split_dataset, save_to_json
from presidio_evaluator.data_generator.faker_extensions.data_objects import FakerSpansResult
from presidio_evaluator.evaluation import Evaluator


def parse_args():
    """Perform command-line argument parsing."""

    parser = argparse.ArgumentParser(
        description="""Convert Privy-generated dataset to common formats used in Named Entity Recognition NLP pipelines, including 
        InputSample (by presidio-research), Spacy Doc, CoNLL, and Flair.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Absolute path to input data. Must be tokenwise-labeled spans-{data_format}.json",
    )

    parser.add_argument(
        "--output_folder",
        "-o",
        required=False,
        help="Absolute path to output folder to store conversions in. Defaults to bazel cache for this runtime",
    )

    parser.add_argument(
        "--convert_to",
        "-c",
        default=["presidio"],
        choices=[
            "presidio",
            "conll",
            "spacy",
            "flair",
        ],
        nargs='+',
        required=False,
        help="Formats to convert to. Defaults to Presidio InputSample.",
    )

    parser.add_argument(
        "--split",
        "-s",
        action="store_true",
        required=False,
        default=False,
        help="Split converted data into train, validation, and test sets.",
    )

    parser.add_argument(
        "--ratios",
        "-r",
        required=False,
        default="[0.7, 0.2, 0.1]",
        nargs='+',
        help="Ratios to split data into train, validation, and test. Only used if --split is set.",
    )

    parser.add_argument(
        "--filter_out_entities",
        "-f",
        action="store_true",
        required=False,
        help="Whether to mark unsupported entities as non-entities 'O' or filter them out.",
    )

    return parser.parse_args()


class PrivyConverter:
    def __init__(self, input_file: str, output_folder: str):
        self.input_file = Path(input_file)
        self.output_folder = Path(output_folder)

    def convert_to_presidio(self, filter_out_entities) -> None:
        """Convert Privy dataset to Presidio InputSample format"""

        print(f"Reading privy dataset...")
        fake_records = FakerSpansResult.load_privy_dataset(self.input_file)

        print(f"Frequency of entity types in dataset: ")
        print(FakerSpansResult.count_entities(fake_records))

        print(f"Tokenizing and transforming fake samples to list of InputSample objects (data structure in presidio-research)")
        self.input_samples = InputSample.convert_faker_spans(fake_records)

        if filter_out_entities:
            # filter out unsupported entities 
            InputSample.remove_unsupported_entities(self.input_samples, entity_mapping=PRIVY_ENTITIES)
        print(
        f"Translating tags to PII entities defined in PRIVY_ENTITIES\n {PRIVY_ENTITIES}")
        # translate raw faker labels to privy entity types, marking unsupported entities as
        # non-entities 'O' (if not filtered out previously)
        self.input_samples = Evaluator.align_entity_types(deepcopy(self.input_samples),
                                                        entities_mapping=PRIVY_ENTITIES,
                                                        allow_missing_mappings=True)

        # frequency of new entity types after translation
        InputSample.count_entities(self.input_samples)

        # save presidio input_samples to json
        output_presidio_samples = self.output_folder / "input-samples.json"
        InputSample.to_json(dataset=self.input_samples,
                            output_file=output_presidio_samples)

    def convert_to_conll(self) -> None:
        """Convert Privy dataset to CoNLL format"""
        output_conll = self.output_folder / "conll.tsv"
        conll = InputSample.create_conll_dataset(self.input_samples)
        conll.to_csv(output_conll, sep="\t")

    def convert_to_spacy_doc(self) -> None:
        """Convert Privy dataset to Spacy Doc format"""
        output_spacy = self.output_folder / "doc.spacy"
        InputSample.create_spacy_dataset(
            self.input_samples, output_path=output_spacy)

    def convert_to_flair(self) -> None:
        """Convert Privy dataset to Flair format"""
        output_flair = self.output_folder / "flair.csv"
        flair_dataset = InputSample.create_flair_dataset(self.input_samples)
        with open(output_flair, "w") as file:
            for row in flair_dataset:
                file.write(f"{row}\n")

    def split_dataset(self, ratios, convert_to) -> None:
        """Split converted dataset into train, validation, and test sets"""
        TRAIN_TEST_VAL_RATIOS = ast.literal_eval(ratios)
        if sum(TRAIN_TEST_VAL_RATIOS) > 1:
            raise argparse.ArgumentTypeError(
                f"Ratios {ratios} must add up to 1.")
        train, test, validation = split_dataset(
            self.input_samples, TRAIN_TEST_VAL_RATIOS)
        print(
            f"Train, test, validation sizes: {len(train)}, {len(test)}, {len(validation)}")

        print("Saving split presidio input_samples to json")
        date_ = date.today().strftime("%b-%d-%Y")
        save_to_json(train, self.output_folder / f"train_{date_}.json")
        save_to_json(test, self.output_folder / f"test_{date_}.json")
        save_to_json(validation, self.output_folder /
                     f"validation_{date_}.json")

        if "conll" in convert_to:
            # save conll to json
            train_conll = InputSample.create_conll_dataset(train)
            test_conll = InputSample.create_conll_dataset(test)
            validation_conll = InputSample.create_conll_dataset(validation)

            train_conll.to_csv(self.output_folder /
                               f"train_{date_}.tsv", sep="\t")
            test_conll.to_csv(self.output_folder /
                              f"test_{date_}.tsv", sep="\t")
            validation_conll.to_csv(
                self.output_folder / f"validation_{date_}.tsv", sep="\t")

        if "spacy" in convert_to:
            # convert split data to spacy format
            InputSample.create_spacy_dataset(
                train, output_path=self.output_folder / f"train_{date_}.spacy")
            InputSample.create_spacy_dataset(
                test, output_path=self.output_folder / f"test_{date_}.spacy")
            InputSample.create_spacy_dataset(
                validation, output_path=self.output_folder / f"validation_{date_}.spacy")


def main(args):
    print(
        f"Converting Privy dataset from {args.input} to {args.convert_to} format(s)...")
    print(f"Downloading spacy model for tokenization")
    spacy.cli.download("en_core_web_sm")

    privy_converter = PrivyConverter(args.input, args.output_folder)
    privy_converter.convert_to_presidio(args.filter_out_entities)

    if "conll" in args.convert_to:
        privy_converter.convert_to_conll()
    if "spacy" in args.convert_to:
        privy_converter.convert_to_spacy_doc()
    if "flair" in args.convert_to:
        privy_converter.convert_to_flair()

    if args.split:
        print("Splitting dataset into train, validation, and test sets...")
        privy_converter.split_dataset(args.ratios, args.convert_to)


if __name__ == '__main__':
    args = parse_args()
    main(args)
