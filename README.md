shellhackathon
==============================

Solution attempt for shell hackathon 2022


Getting Started
---------------
We assume you have python3.6, `pip`, and `pipenv` installed.

Pretty much everything it done with the Makefile.
Just have a look and see what you can do:
```
➤ make
Available rules:

clean               Delete all compiled Python files
clean_data          Delete all data
data                Make data 
dep.png             Create dependency visualization from Makefile
enable_hooks        Enable flake8 and nbstripout hooks
env_create          Set up an environment with pipenv
lint                Lint using flake8 and mypy
sync_data_from_s3   Download Data from S3
sync_data_to_s3     Upload Data to S3
test                Run the unit tests
testwatch           Run tests on every file change
```

To setup the project do the following:
```
➤ make env_create
➤ pipenv shell
➤ make data
➤ make test
```


Project Structure
--------------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention:
    │                         - date (for ordering),
    │                         - the creator's initials,i
    │                         - a short `_` delimited description
    │                         e.g. `2018-01-23_SO_explorative_data_exploration`.
    │                         Create new notebooks from the template `notebooks/TEMPLATE.ipynb`
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── shellhackathon
    │   ├── __init__.py    <- Makes src a Python module
    │   ├── utils.py       <- Put your utility function here
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
