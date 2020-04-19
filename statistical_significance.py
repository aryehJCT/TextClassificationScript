import json
import os
import pickle
from os import path
from pathlib import Path

import numpy as np


def corrected_paired_students_ttest(new_score, baseline_score, k_fold, sig_level=0.05):
    """
    Calculate Corrected Paired Student's t-test according to Nadeau and Bengio's theory
    Based on the article at
    https://medium.com/analytics-vidhya/using-the-corrected-paired-students-t-test-for-comparing-the-performance-of-machine-learning-dc6529eaa97f
    :param new_score: Iterable, All results (in percentages) of the new classification that should be examined
    :param baseline_score: Iterable, All results (in percentages) of the baseline
    :param k_fold: The number of folds made in the K-fold cross-validation for the new results and for the baseline
    :param sig_level: The level of statistical significance it needs to examine
    :return: "*" If the new results are significantly smaller than the baseline, "V" if they are large and nothing if
            there is no significant difference between them
    """
    # Compute the difference between the results
    diff = [y - x for y, x in zip(new_score, baseline_score)]
    # Comopute the mean of differences
    d_bar = np.mean(diff)
    # compute the variance of differences
    sigma2 = np.var(diff)
    # compute the number of data points used for training
    n1 = int(len(new_score) * ((k_fold - 1) / k_fold))
    # compute the number of data points used for testing
    n2 = int(len(new_score) / k_fold)
    # compute the total number of data points
    n = len(new_score)
    # compute the modified variance
    sigma2_mod = sigma2 * (1 / n + n2 / n1)
    # compute the t_static
    t_static = d_bar / np.sqrt(sigma2_mod)
    # compute p-value
    from scipy.stats import t
    p_value = (1 - t.cdf(np.abs(t_static), n - 1)) * 2
    # determine whether the results are significantly different, and whether they are smaller or larger
    differences_significance = ""
    if p_value <= sig_level:
        if np.mean(new_score) > np.mean(baseline_score):
            differences_significance = "V"
        else:
            differences_significance = "*"
    return differences_significance


def differences_significance(baseline_path, results, measure, k_folds, significance_level=0.05):
    if baseline_path == "":
        return ""

    if path.isdir(baseline_path):
        files = list(sorted(Path(baseline_path).iterdir(), key=os.path.getmtime))
        baseline_path = baseline_path + "\\" + files[-1].name

    with open(baseline_path, "r", encoding="utf8", errors="replace") as f:
        baseline = json.load(f)

    if len(baseline["best_score"][measure]) != len(results):
        raise Exception("Results with different lengths cannot be compared to the baseline")

    results = [x * 100 for x in results] if np.mean(results) < 1 else results
    baseline = [x * 100 for x in baseline["best_score"][measure]] if np.mean(baseline["best_score"][measure]) < 1 else \
    baseline["best_score"][measure]

    return corrected_paired_students_ttest(results, baseline, k_folds, significance_level)


def open_pickle_content(pickle_file_path):
    with open(pickle_file_path, "rb") as file:
        return pickle.load(file)


if __name__ == "__main__":
    # path = r"C:\\Users\\natan\\OneDrive\\\u05de\u05e1\u05de\u05db\u05d9\u05dd\\test\\baseline"
    x = [85, 90, 98, 95, 100]
    y = [70, 70, 68, 50, 60]
    print(corrected_paired_students_ttest(x, y, 5, 0.05))
    print(corrected_paired_students_ttest(y, x, 5, 0.05))
