# Hiking time prediction from GPX track statistics
This repository provides files and notebooks for training simple models for predicting 
hiking times. More precisely, they predict the *Moving time*, *Stopped time* and duration of a hike.
The moving time does not include stopping or pausing. When using own records of GPX tracks for training,
the models can estimate personalized hiking times.

The estimates are based on simple statistics about GPX tracks, GPX tracks themselves or a combination of the two. The statistical features include the length of tracks, the total elevation gain and the total elevation loss. In order to be able to get good predictions based on a relatively small number of GPX tracks, the latter
are split into smaller pieces which are used as inputs for the model. The same preprocessing steps are applied during inference. A dataset of 40-50 GPX tracks allows to train models that predict hiking times better than standard formulas.

The repository includes files for extracting data from tracks, training models and making predictions.

## Install anaconda environment
Run

`conda env create -n hikingTimePredictor`

and activate environment `hikingTimePredictor` by typing

`source activate hikingTimePredictor`.

Install dependencies via

`pip install -r requirements.txt`.

## Prepare data
Run

`python prepare_data.py base_folder filter_key`

where `base_folder` is the folder in which the program searches recursively 
for GPX tracks (with file names ending on gpx). It filters for files that contain
`filter_key` in their path, which could for example be `Hiking`.

## Train the model
Open the notebook `hikingTimeRegression_v1.ipynb` (or `v2`, `v3`) and follow the steps described
there.

## Predict hiking time
Run

`python inference.py input_file model_type`

where `input_file` is the name of the GPX track for which hiking times should be estimated. `model_type` is 'simple' for v1, 'recurrent' for v2 and 'mixed' for v3.

## License

MIT, see LICENSE for more information
