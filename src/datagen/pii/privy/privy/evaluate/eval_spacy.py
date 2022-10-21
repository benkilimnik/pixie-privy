import argparse
from pathlib import Path
import spacy
import spacy_transformers
from presidio_evaluator.data_objects import InputSample
from presidio_evaluator.models import SpacyModel
from privy.evaluate.utils import PrivyEvaluator
from privy.evaluate.entity_mappings import PRIVY_ONTONOTES_TRANSLATOR


def parse_args():
    """Perform command-line argument parsing."""

    parser = argparse.ArgumentParser(
        description="""Evaluate Spacy with data from Privy""",
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
        default=["en_core_web_lg", "en_core_web_trf"],
        choices=["en_core_web_sm", "en_core_web_lg", "en_core_web_trf"],
        nargs='+',
        required=False,
        help="Presidio analyzer models to use. Defaults to spacy.",
    )

    return parser.parse_args()


class PrivyPresidioEvaluator:
    def __init__(self, input_file: str, output_folder: str):
        self.input_file = Path(input_file)
        self.output_folder = Path(output_folder) / "spacy-benchmark"
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def evaluate_presidio_analyzer(self, model_names) -> None:
        print(f"Reading presidio input samples...")
        dataset = InputSample.read_dataset_json(self.input_file)
        print(
            f"Frequency of entity types in dataset: {InputSample.count_entities(dataset)}")

        models = [SpacyModel(model=spacy.load(name), entity_mapping=PRIVY_ONTONOTES_TRANSLATOR)
                  for name in model_names]
        privy_evaluator = PrivyEvaluator(
            dataset, model_names, models, self.output_folder)
        privy_evaluator.evaluate()


def main(args):
    print(
        f"Evaluating Privy generated dataset on SpaCy NER models: {args.model_names}...")
    print(f"Downloading spacy model for tokenization")
    spacy.cli.download("en_core_web_sm")
    # spacy.cli.download("en_core_web_lg")
    # spacy.cli.download("en_core_web_trf")

    privy_converter = PrivyPresidioEvaluator(args.input, args.output_folder)
    privy_converter.evaluate_presidio_analyzer(args.model_names)


if __name__ == '__main__':
    args = parse_args()
    main(args)
