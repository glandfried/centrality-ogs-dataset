#  Replication of the results of the manuscript "Exploring the effect of network structure on individual learning: a longitudinal study of an online Go game community"

Author: Gustavo Landfried
Author: Esteban Mocskos

1. Setup
1. Makefile
1. Data

## 1. Setup

This folder was created using Ubuntu 22.04 and python3.10.6.
To replicate the figures you must install the listed packages inside the file `requirements.txt`.

If you want to use a virtualenv, first you must create it

```
python3 -m venv myenv
```

Then activate it

```
source myenv/bin/activate
```

Install the packages

```
pip install -r requirements.txt
```

You will also need the `pdfcrop` to create the images.
To install it on a Linux system, you can use your package manager to install the `texlive-extra-utils` package which includes `pdfcrop`, as well as other utilities for working with LaTeX documents.

```
sudo apt install texlive-extra-utils
```

## 2. Makefile

When the Setup procedure is complete, you can replicate the figures by running the root makefile

```
make
```

If you read this file, you will see that you are just calling the makefile inside the `4-figures/` folder.

### 2.1. make -C 4-figures/

This makefile executes all the python scripts inside `4-figures/` folder.
If the dependency `3-results/results.zip` do not exist, this makefile will call another makefile, inside the `3-results/` folder.

### 2.2 make -C 3-results/

This makefile will download and unzip results.zip from github.
This file has all the needed data to create the figures.
And was created using scripts in folder `2-analysis/`


## Data

Folder `2-analysis/` has all the scripts needed to replicate the analysis.
The whole research process is summaryzed in the file `2-analysis/dispatcher.sh
But you can download the output by executing the makefile.

```
make -C 1-data/
```

Finally, if you want the original database, you can download it by executing

```
make -C 0-origin/
```

This will give you the `neo4j-backup-OGS.zip` file.
