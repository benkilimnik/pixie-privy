import argparse
from pathlib import Path
import spacy
from presidio_evaluator.data_objects import InputSample
from presidio_evaluator.models import PresidioAnalyzerWrapper
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from privy.evaluate.utils import PrivyEvaluator
from privy.evaluate.entity_mappings import PRIVY_PRESIDIO_TRANSLATOR


def parse_args():
    """Perform command-line argument parsing."""

    parser = argparse.ArgumentParser(
        description="""Evaluate Presidio Analyzer with data from Privy""",
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
        default=["presidio_spacy", "presidio_transformers"],
        choices=[
            "spacy",
            "transformers",
        ],
        nargs='+',
        required=False,
        help="Presidio analyzer models to use. Defaults to spacy.",
    )

    return parser.parse_args()


class PrivyPresidioEvaluator:
    def __init__(self, input_file: str, output_folder: str):
        self.input_file = Path(input_file)
        self.output_folder = Path(output_folder) / "presidio-benchmark"
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def evaluate_presidio_analyzer(self, model_names) -> None:
        print(f"Reading presidio input samples...")
        dataset = InputSample.read_dataset_json(self.input_file)
        print(
            f"Frequency of entity types in dataset: {InputSample.count_entities(dataset)}")

        models = []
        if "presidio_spacy" in model_names:
            models.append(PresidioAnalyzerWrapper(
                entity_mapping=PRIVY_PRESIDIO_TRANSLATOR))
        if "presidio_transformers" in model_names:
            nlp_configuration = {
                "nlp_engine_name": "transformers",
                "models": [
                    {
                        "lang_code": "en",
                        "model_name": {
                            "spacy": "en_core_web_sm",
                            "transformers": "dslim/bert-base-NER",
                        },
                    }
                ],
            }
            # Create NLP engine based on configuration
            engine = NlpEngineProvider(
                nlp_configuration=nlp_configuration).create_engine()
            # Pass the created NLP engine and supported_languages to the AnalyzerEngine
            analyzer = AnalyzerEngine(
                nlp_engine=engine, supported_languages=["en"]
            )
            models.append(PresidioAnalyzerWrapper(
                entity_mapping=PRIVY_PRESIDIO_TRANSLATOR, analyzer_engine=analyzer))

        privy_evaluator = PrivyEvaluator(
            dataset, model_names, models, self.output_folder)
        privy_evaluator.evaluate()


def main(args):
    print(
        f"Evaluating Privy generated dataset on Presidio analyzer with models: {args.model_names}...")
    print(f"Downloading spacy model for tokenization")
    # spacy.cli.download("en_core_web_sm")
    # spacy.cli.download("en_core_web_lg")

    privy_converter = PrivyPresidioEvaluator(args.input, args.output_folder)
    privy_converter.evaluate_presidio_analyzer(args.model_names)


if __name__ == '__main__':
    args = parse_args()
    main(args)
