import argparse
from pathlib import Path
import spacy
from presidio_evaluator.data_objects import InputSample
from presidio_evaluator.models import FlairModel
from privy.evaluate.utils import PrivyEvaluator
from privy.evaluate.entity_mappings import PRIVY_CONLL_TRANSLATOR, PRIVY_ONTONOTES_TRANSLATOR


def parse_args():
    """Perform command-line argument parsing."""

    parser = argparse.ArgumentParser(
        description="""Evaluate Flair with data from Privy""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Absolute path to input data. Must be tokenwise-labeled presidio input samples.",
    )

    parser.add_argument(
        "--output_folder",
        "-o",
        required=False,
        help="Absolute path to output folder to store error analysis files in. Defaults to bazel cache for this runtime",
    )

    parser.add_argument(
        "--model_names",
        "-m",
        default=["flair/ner-english-ontonotes-large", "flair/ner-english-large"],
        choices=["flair/ner-english-fast", "flair/ner-english-large",
                 "flair/ner-english-ontonotes-fast", "flair/ner-english-ontonotes-large"],
        nargs='+',
        required=False,
        help="Presidio analyzer models to use. Defaults to spacy.",
    )

    return parser.parse_args()


class PrivyFlairEvaluator:
    def __init__(self, input_file: str, output_folder: str):
        self.input_file = Path(input_file)
        self.output_folder = Path(output_folder) / "flair-benchmark"
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def evaluate_presidio_analyzer(self, model_names) -> None:
        print(f"Reading presidio input samples...")
        dataset = InputSample.read_dataset_json(self.input_file)
        print(
            f"Frequency of entity types in dataset: {InputSample.count_entities(dataset)}")

        models = []
        for name in model_names:
            if "ontonotes" in name:
                models.append(FlairModel(model_path=name,
                              entity_mapping=PRIVY_ONTONOTES_TRANSLATOR))
            else:
                models.append(FlairModel(model_path=name,
                              entity_mapping=PRIVY_CONLL_TRANSLATOR))
        privy_evaluator = PrivyEvaluator(
            dataset, model_names, models, self.output_folder)
        privy_evaluator.evaluate()


def main(args):
    print(
        f"Evaluating Privy generated dataset on Flair NER models: {args.model_names}...")
    print(f"Downloading spacy model for tokenization")
    spacy.cli.download("en_core_web_sm")

    privy_converter = PrivyFlairEvaluator(args.input, args.output_folder)
    privy_converter.evaluate_presidio_analyzer(args.model_names)


if __name__ == '__main__':
    args = parse_args()
    main(args)
