from typing import Union

import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path


def compute_standard_walking_time(
    length_m: float, elevation_gain_m: float, elevation_loss_m: float
) -> float:
    """Estimate the hiking time in seconds

    Parameters
    ----------
    :param: length_m:           Length of the hike in meters
    :param: elevation_gain_m:   Elevation gain of the hike in meters
    :param: elevation_loss_m:   Elevation loss of the hike in meters

    :return: Walking time (= moving time) for the hike in seconds
    """
    walking_time_length_s = 0.9 * length_m  # assumed speed: 4 km/h
    walking_time_up_s = elevation_gain_m * 12  # assumed speed: +300 m/h
    walking_time_down_s = elevation_loss_m * 7.2  # assumed speed: -500 m/h
    walking_time_up_down_s = walking_time_up_s + walking_time_down_s
    return max(walking_time_length_s, walking_time_up_down_s) + 0.5 * min(
        walking_time_length_s, walking_time_up_down_s
    )


def scatter_plot(
    ground_truth: np.array, predictions: np.array, label_text: str
) -> None:
    """
    Plot scatter plot of predictions vs. ground truth values.

    :param: ground_truth:   Array containing ground truth data
    :param: predictions:    Array containing predicted values
    :param: label_text:     Label text for plot
    """
    plt.scatter(ground_truth, predictions, label="{} scatter plot".format(label_text))
    max_val: float = max([max(ground_truth), max(predictions)])
    plt.xlabel("True Values [{}]".format(label_text))
    plt.ylabel("Predictions [{}]".format(label_text))
    plt.axis("square")
    plt.legend()
    plt.xlim([0, max_val])
    plt.ylim([0, max_val])
    _ = plt.plot([0, max_val], [0, max_val])
    plt.show()


def plot_error_hist(
    ground_truth: np.array, predictions: np.array, label_text: str
) -> None:
    """
    Plot historgram of errors.

    :param: ground_truth:   Array containing ground truth data
    :param: predictions:    Array containing predicted values
    :param: label_text:     Label text for plot
    """
    error = ground_truth - predictions
    plt.xlabel("Prediction Error [{}]".format(label_text))
    plt.ylabel("Count")
    _, _, _ = plt.hist(error, bins=25, range=(-100, 100))
    plt.show()


def plot_history(history, mse_column_name: str, mae_column_name: str):
    """
    Plot learning curve.

    :param: history: Keras History object
    """
    hist = pd.DataFrame(history.history)
    hist["epoch"] = history.epoch

    plt.figure()
    plt.xlabel("Epoch")
    plt.ylabel("Mean Absolute Error [MovingTime]")
    plt.plot(hist["epoch"], hist[mae_column_name], label="Train Error")
    plt.plot(hist["epoch"], hist["val_" + mae_column_name], label="Val Error")
    plt.yscale("log")
    plt.legend()

    plt.figure()
    plt.xlabel("Epoch")
    plt.ylabel("Mean Squared Error [$MovingTime^2$]")
    plt.plot(hist["epoch"], hist[mse_column_name], label="Train Error")
    plt.plot(hist["epoch"], hist["val_" + mse_column_name], label="Val Error")
    plt.yscale("log")
    plt.legend()
    plt.show()

    if "lr" in hist.columns:
        plt.figure()
        plt.xlabel("Epoch")
        plt.ylabel("Learning rate")
        plt.plot(hist["epoch"], hist["lr"], label="Learning rate")
        plt.yscale("log")
        plt.legend()
        plt.show()


def get_pseudo_probability_for_path(
    path: Union[str, Path], max_int: int = 4096
) -> float:
    """Create pseudo probability for dataset split assignment of files.

    Parameters
    ----------
    path
        Path to file
    max_int
        Maximal integer number that should be allowed for modulo operations

    Returns
    -------
    Pseudo-probability score that is useful for unique and reproducible assignment of files to dataset split
    """
    if isinstance(path, Path):
        path = str(Path)

    encoded_path = str.encode(path)

    hash_as_int = int(hashlib.sha256(encoded_path).hexdigest(), 16)

    return (hash_as_int % max_int) / (max_int - 1)
