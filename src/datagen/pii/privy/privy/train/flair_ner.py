import os
import argparse
import ast
from presidio_evaluator.models import FlairTrainer
from presidio_evaluator.data_objects import InputSample
from presidio_evaluator.validation import split_dataset, save_to_json
from datetime import date
from pathlib import Path


class FlairDataset:
    def __init__(self, dataset_path, out_folder):
        self.dataset = InputSample.read_dataset_json(dataset_path)
        self.output_folder = Path(out_folder)

    def train_test_val_split(self, ratios):
        """Split converted dataset into train, validation, and test sets"""
        TRAIN_TEST_VAL_RATIOS = ast.literal_eval(ratios)
        if sum(TRAIN_TEST_VAL_RATIOS) > 1:
            raise argparse.ArgumentTypeError(
                f"Ratios {ratios} must add up to 1.")
        train, test, validation = split_dataset(
            self.dataset, TRAIN_TEST_VAL_RATIOS)
        print(
            f"Train, test, validation sizes: {len(train)}, {len(test)}, {len(validation)}")

        print("Saving split presidio input_samples to json")
        date_ = date.today().strftime("%b-%d-%Y")
        train_path = self.output_folder / f"train_{date_}.json" 
        test_path = self.output_folder / f"test_{date_}.json" 
        val_path = self.output_folder / f"validation_{date_}.json" 
        save_to_json(train, train_path)
        save_to_json(test, test_path)
        save_to_json(validation, val_path)
        return train_path, test_path, val_path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train Flair Named Entity Recognition (NER) model for token-wise PII classification",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="""Absolute path to full input data. Must be in presidio InputSample format. See evaluate/convert_dataset.py 
        for conversion script from Privy generated spans.""",
    )

    parser.add_argument(
        "--ratios",
        "-r",
        required=False,
        default="[0.7, 0.2, 0.1]",
        nargs='+',
        help="Ratios to split data into train, validation, and test.",
    )

    parser.add_argument(
        "--out_folder",
        "-o",
        required=False,
        default=os.path.join(os.path.dirname(__file__), os.pardir),
        help="""Absolute path to where trained flair model(s) will be stored.
        By default, saves to bazel cache for this runtime.""",
    )

    return parser.parse_args()


def main(args):
    # load dataset
    dataset = FlairDataset(args.input, args.out_folder)
    train, test, val = dataset.train_test_val_split(args.ratios)

    # train Flair
    trainer = FlairTrainer()
    trainer.create_flair_corpus(train, test, val)
    corpus = trainer.read_corpus(args.out_folder)

    # GloVe embeddings
    trainer.train_with_flair_embeddings(corpus)
    
    # BERT embeddings
    # ! todo: add method to presidio fork
    # trainer.train_with_bert_embeddings(corpus)

    # Transformer
    trainer.train_with_transformers(corpus)


if __name__ == "__main__":
    args = parse_args()
    main(args)
