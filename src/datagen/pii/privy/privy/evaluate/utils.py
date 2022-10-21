from copy import deepcopy
from typing import List
from pathlib import Path
import plotly.express as px
import plotly
import pandas as pd
from presidio_evaluator.evaluation import Evaluator
from presidio_evaluator.evaluation import Evaluator, ModelError
from presidio_evaluator.experiment_tracking import get_experiment_tracker


class PrivyEvaluator:
    def __init__(self, dataset, model_names, models, output_folder):
        self.dataset = dataset
        self.model_names = model_names
        self.models = models
        self.output_folder = output_folder

    def evaluate(self, plot_results=True, save_errors=True) -> None:
        for model_name, model in zip(self.model_names, self.models):
            print("-----------------------------------")
            print(f"Evaluating model {model_name}")
            experiment = get_experiment_tracker()

            evaluator = Evaluator(model=model)
            evaluation_results = evaluator.evaluate_all(deepcopy(self.dataset))
            results = evaluator.calculate_score(evaluation_results)

            params = {"dataset_name": "privy_dataset",
                      "model_name": model_name}
            params.update(model.to_log())
            experiment.log_parameters(params)
            experiment.log_dataset_hash(self.dataset)
            experiment.log_metrics(results.to_log())
            entities, confmatrix = results.to_confusion_matrix()
            experiment.log_confusion_matrix(matrix=confmatrix, labels=entities)

            print("Confusion matrix:")
            print(pd.DataFrame(confmatrix, columns=entities, index=entities))
            print("Precision and recall")
            print(results)

            errors = results.model_errors
            error_analyzer = ErrorAnalyzer(
                model, results, errors, self.output_folder, model_name)
            if plot_results:
                error_analyzer.plot_recall_precision_f2()
            if save_errors:
                error_analyzer.save_errors()

            experiment.end()


class ErrorAnalyzer:
    def __init__(self, model, results, errors, output_folder, model_name):
        self.model = model
        self.results = results
        self.errors = errors
        self.output_folder = output_folder
        self.model_name = model_name.replace("/", "-")

    def plot_recall_precision_f2(self) -> None:
        """Plot per-entity recall and precision"""
        d = {}
        d['entity'] = deepcopy(list(self.results.entity_recall_dict.keys()))
        d['recall'] = deepcopy(list(self.results.entity_recall_dict.values()))
        d['precision'] = deepcopy(
            list(self.results.entity_precision_dict.values()))
        d['count'] = deepcopy(list(self.results.n_dict.values()))
        d['f2_score'] = [Evaluator.f_beta(precision=precision, recall=recall, beta=2.5)
                         for recall, precision in zip(d['recall'], d['precision'])]
        df = pd.DataFrame(d)
        df['model'] = self.model_name
        self._plot(df, plot_type="Recall")
        self._plot(df, plot_type="Precision")
        self._plot(df, plot_type="F2_Score")

        scores_output = self.output_folder / \
            f"scores-dict-{self.model_name}.json"
        df.to_csv(scores_output, index=False)

    def _plot(self, df, plot_type: str) -> None:
        fig = px.bar(df, text_auto=".2", x='entity',
                     y=f'{plot_type.lower()}', color='count', barmode='group', title=f"Per-entity {plot_type} for {self.model_name}")
        fig.update_layout(barmode='group', xaxis={
                          'categoryorder': 'total ascending'})
        fig.update_layout(yaxis_title=f"{plot_type}", xaxis_title="PII Entity")
        fig.update_traces(textfont_size=12, textangle=0,
                          textposition="outside", cliponaxis=False)
        fig.update_layout(
            plot_bgcolor="#FFF",
            xaxis=dict(
                title="PII entity",
                linecolor="#BCCCDC",  # Sets color of X-axis line
                showgrid=False  # Removes X-axis grid lines
            ),
            yaxis=dict(
                title=f"{plot_type}",
                linecolor="#BCCCDC",  # Sets color of X-axis line
                showgrid=False  # Removes X-axis grid lines
            ),
        )
        filename = self.output_folder / \
            f"{plot_type.lower()}_{self.model_name}.html"
        plotly.offline.plot(
            fig, filename=str(filename))
        filename = self.output_folder / \
            f"{plot_type.lower()}_{self.model_name}.png"
        fig.write_image(filename)

    def _plot_multiple_models(score_files: List[Path], model_name: str, plot_type: str) -> None:
        """Plot per-entity Recall, Precision or F2 Score for multiple models given dataframes saved to csv during evaluation"""
        df = pd.read_csv(score_files[0])
        # combine score dataframes
        for file in score_files[1:]:
            df = pd.concat([df, pd.read_csv(file)])

        fig = px.bar(df, text_auto=".2", x='entity',
                     y=f'{plot_type.lower()}', color='model', barmode='group', title=f"Per-entity {plot_type} for {model_name}")
        fig.update_layout(barmode='group', xaxis={
            'categoryorder': 'total ascending'})
        fig.update_layout(yaxis_title=f"{plot_type}", xaxis_title="PII Entity")
        fig.update_traces(textfont_size=12, textangle=0,
                          textposition="outside", cliponaxis=False)
        fig.update_layout(
            plot_bgcolor="#FFF",
            xaxis=dict(
                title="PII entity",
                linecolor="#BCCCDC",  # Sets color of X-axis line
                showgrid=False  # Removes X-axis grid lines
            ),
            yaxis=dict(
                title="Recall",
                linecolor="#BCCCDC",  # Sets color of X-axis line
                showgrid=False  # Removes X-axis grid lines
            ),
        )
        fig.show()

    def save_errors(self):
        ModelError.most_common_fp_tokens(self.errors)

        for entity in self.model.entity_mapping.values():
            fps_df = ModelError.get_fps_dataframe(self.errors, entity=[entity])
            if fps_df is not None:
                fps_df.to_csv(self.output_folder /
                              f"{self.model_name}-{entity}-fps.csv")
            fns_df = ModelError.get_fns_dataframe(self.errors, entity=[entity])
            if fns_df is not None:
                fns_df.to_csv(self.output_folder /
                              f"{self.model_name}-{entity}-fns.csv")
