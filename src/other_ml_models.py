import numpy as np
import pandas as pd
from comet_ml import Experiment
from comet_ml.integration.sklearn import log_model
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.base import BaseEstimator
from sklearn.metrics import PrecisionRecallDisplay, roc_curve, auc
from sklearn.calibration import calibration_curve, CalibrationDisplay
import matplotlib.pyplot as plt
import seaborn as sns

def create_pipeline(classifier: BaseEstimator, feature_selection: BaseEstimator = None, encoder: str = 'Label') -> Pipeline:
    """
    This Helper Function creates a pipeline with a given classifier, an optional feature selection step, and a specified encoder for categorical features
    """
    encoders = {
        'Label': OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1),
        'OneHot': OneHotEncoder(handle_unknown='ignore')
    }

    numeric_transformer = Pipeline([
        ('Impt', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ('Impt', SimpleImputer(strategy='most_frequent')),
        ('encoder', encoders[encoder])
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("Numerical_transform", numeric_transformer, make_column_selector(dtype_include="number")),
        ("Categorical_transform", categorical_transformer, make_column_selector(dtype_exclude="number"))
    ])

    steps = [('preprocessor', preprocessor)]
    if feature_selection:
        steps.append(('feature_select', feature_selection))
    steps.append(('classifier', classifier))

    return Pipeline(steps=steps)

def generate_goal_rate_plot(model_name, binned_data, curr_experiment):
    """
    Helper Function to generate Goal Rate Plot
    """
    plt.figure(figsize=(10, 5))
    plt.title("Analysis of Goal Rate by Model")
    sns.lineplot(x='goal_perc_bins', y='goal_rate', data=binned_data, linewidth=2.5, label=model_name)
    plt.xlabel('Model Probability Percentile')
    plt.ylabel('Goal Rate')
    plt.xticks(np.arange(0, 120, 20))
    plt.legend(loc="best")
    curr_experiment.log_figure(figure_name='Goal Rate Plot', step=None)
    plt.show()

def prepare_bin_data(y_test, predictions, prediction_probabilities):
    """
    Helper to create bin data
    """
    bins = list(np.arange(0, 105,  5))
    bin_centers = list(np.arange(2.5, 100,  5.0))
    df_prob = pd.DataFrame(list(zip(predictions ,y_test ,prediction_probabilities[:,1]*100)), columns = ['goal_pred', 'goal','goal_probability'])
    df_prob['shot'] = 1
    sum_goal = df_prob['goal'].sum()
    df_prob['percentile'] = df_prob['goal_probability'].rank(pct=True) * 100
    df_prob['goal_perc_bins'] = pd.cut(df_prob['percentile'], bins, labels = bin_centers)
    df_prob_bined = df_prob[['goal_perc_bins', 'shot', 'goal' ]].groupby(['goal_perc_bins']).sum().reset_index()
    df_prob_bined['goal_rate'] = (df_prob_bined['goal']/df_prob_bined['shot'])
    df_prob_bined['goal_cum'] = (df_prob_bined['goal']/sum_goal)
    df_prob_bined['goal_cumsum'] = 1-df_prob_bined['goal_cum'].cumsum()
    return df_prob_bined

def plot_roc_curve(y_test, preds_proba, model_name, curr_experiment):
    plt.figure(figsize=(10, 6))
    line_width = 2

    false_positive_rate, true_positive_rate, _ = roc_curve(y_test.ravel(),preds_proba[:,1].ravel())
    area_under_curve = auc(false_positive_rate, true_positive_rate)
    plt.plot(false_positive_rate, true_positive_rate, lw=line_width, label=f"Model {model_name} - AUC: {area_under_curve:.2f}")

    plt.plot([0, 1], [0, 1], color="grey", lw=line_width, linestyle='--', label="Baseline (Random)")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve Comparison")
    plt.legend(loc="lower right")
    curr_experiment.log_figure(figure_name='ROC-AUC', step=None)
    plt.show()

def plot_precision_recall(model, X_test, y_test, experiment):
    display = PrecisionRecallDisplay.from_estimator(model, X_test, y_test)
    display.ax_.set_title("Precision-Recall curve")
    plt.grid(color='gray', linestyle='--', linewidth=0.5)
    experiment.log_figure(figure_name='Precision-Recall Curve', step=None)

def plot_calibration_curve(y_test, prediction_probabilities, experiment):
    _, ax = plt.subplots(figsize=(10, 10))
    display = CalibrationDisplay.from_predictions(y_test, prediction_probabilities[:,1].ravel(), n_bins=10, ax=ax)
    display.ax_.set_title("Calibration Curve")
    plt.grid(color='gray', linestyle='--', linewidth=.5)
    plt.legend(loc="center right")
    experiment.log_figure(figure_name='Calibration Curve', step=None)

def visualize_cumulative_goals(model_name, binned_data, curr_experiment):
    plt.figure(figsize=(10, 5))
    plt.title("Cumulative Goals Analysis")
    sns.lineplot(x='goal_perc_bins', y='goal_cumsum', data=binned_data, linewidth=2.5, label=model_name)
    plt.xlabel('Percentile of Model Predictions')
    plt.ylabel('Cumulative Goal Ratio')
    plt.xticks(np.arange(0, 120, 20))
    plt.legend(loc="lower right")
    curr_experiment.log_figure(figure_name='Cumulative Goal Analysis Plot', step=None)
    plt.show()