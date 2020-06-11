# Hiking time prediction from GPX track statistics
This repository provides files for training a simple algorithm for predicting 
hiking times. More precisely, it predicts the *Moving time* without estimating 
time for stopping or pausing. When using own records of GPX tracks, this leads
to personalized predictions of hiking times.

The estimates are based on simple statistics about GPX tracks, which include the
length of tracks, the total elevation gain and the total elevation loss. 

The repository includes files for extracting data from tracks, training a model 
and making predictions. 

## Install anaconda environment
Run

`conda env create -f environment.yml`

and activate environment `hikingTimePredictor` by typing 

`source activate hikingTimePredictor`

## Prepare data
Run

`python prepareData.py base_folder filter_key`

where `base_folder` is the folder in which the program searches recursively 
for GPX tracks (with file names ending on gpx). It filters for files that contain
`filter_key` in their path, which could for example be `Hiking`.

## Train the model
Open the notebook `hikingTimeRegression.ipynb` and follow the steps described
there.

## Predict hiking time
Run

`python inference.py input_file`

where `input_file` is the name of the GPX track for which you would like to get 
an estimate for the hiking time.

**Note:** The predicted hiking time (or moving time) is *not* equal to the time 
needed for a hike! In order to get an estimate for the total duration, you need 
to add the estimated time for stopping and pausing.

## License

MIT, see LICENSE for more information
