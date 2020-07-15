import numpy as np               # type: ignore
import pandas as pd              # type: ignore
import matplotlib.pyplot as plt  # type: ignore


def compute_standard_walking_time(length_m: float, elevation_gain_m: float, elevation_loss_m: float) -> float:
    """Estimate the hiking time in seconds

    Parameters
    ----------
    :param: length_m:           Length of the hike in meters
    :param: elevation_gain_m:   Elevation gain of the hike in meters
    :param: elevation_loss_m:   Elevation loss of the hike in meters

    :return: Walking time (= moving time) for the hike in seconds
    """
    walking_time_length_s = 0.9 * length_m          # assumed speed: 4 km/h
    walking_time_up_s = elevation_gain_m * 12       # assumed speed: +300 m/h
    walking_time_down_s = elevation_loss_m * 7.2    # assumed speed: -500 m/h
    walking_time_up_down_s = walking_time_up_s + walking_time_down_s
    return max(walking_time_length_s, walking_time_up_down_s) + \
        0.5 * min(walking_time_length_s, walking_time_up_down_s)


def scatter_plot(ground_truth: np.array, predictions: np.array, label_text: str) -> None:
    """
    Plot scatter plot of predictions vs. ground truth values.

    :param: ground_truth:   Array containing ground truth data
    :param: predictions:    Array containing predicted values
    :param: label_text:     Label text for plot
    """
    plt.scatter(ground_truth, predictions, label='{} scatter plot'.format(label_text))
    max_val = max([max(ground_truth), max(predictions)])
    plt.xlabel('True Values [{}]'.format(label_text))
    plt.ylabel('Predictions [{}]'.format(label_text))
    plt.axis('square')
    plt.legend()
    plt.xlim([0, max_val])
    plt.ylim([0, max_val])
    _ = plt.plot([0, max_val], [0, max_val])
    plt.show()


def plot_error_hist(ground_truth: np.array, predictions: np.array, label_text: str) -> None:
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


def plot_history(history):
    """
    Plot learning curve.

    :param: history: Keras History object
    """
    hist = pd.DataFrame(history.history)
    hist['epoch'] = history.epoch

    plt.figure()
    plt.xlabel('Epoch')
    plt.ylabel('Mean Abs Error [MovingTime]')
    plt.plot(hist['epoch'], hist['mean_absolute_error'], label='Train Error')
    plt.plot(hist['epoch'], hist['val_mean_absolute_error'], label='Val Error')
    plt.yscale('log')
    plt.legend()

    plt.figure()
    plt.xlabel('Epoch')
    plt.ylabel('Mean Square Error [$MovingTime^2$]')
    plt.plot(hist['epoch'], hist['mean_squared_error'], label='Train Error')
    plt.plot(hist['epoch'], hist['val_mean_squared_error'], label='Val Error')
    plt.yscale('log')
    plt.legend()
    plt.show()
