---
title: "Wiki data extraction"
summary: "Data extraction from Wikimedia dump"
toc: true
comments: true
categories: [data-cleaning, language-model]
---


# Extracting data from wikipedia for language model

This post explains how I downloaded and extracted wiki dump archive using [wikiextractor](https://github.com/attardi/wikiextractor).

This code was used on a kaggle environment, which can be found [here](https://www.kaggle.com/manimaranp/tamil-wiki-data-extraction). You can fork and change as per your needs.

    # For JSON data extraction
    import json
    # For path manipulations
    from pathlib import Path
    # For preprocessing
    import string
    # For deleting files and folders
    import shutil

    # To clone necessary files
    import git
    # To download the dump
    import requests as req
    # To use wikiextractor
    import subprocess
    # To clean and process data
    import pandas as pd

# Setup output paths
    DATA_PATH = Path('/kaggle/working/')
    EXTRACTED_PATH = DATA_PATH/'extracted'
    EXTRACTED_PATH.mkdir()

# Request file from wikipedia
You can use a different link here

    bzip_file = req.get('https://dumps.wikimedia.org/tawiki/latest/tawiki-latest-pages-articles.xml.bz2')

# Save request content to a file
    with open(DATA_PATH/'tawiki-latest-pages-articles.xml.bz2', 'wb') as f:
        f.write(bzip_file.content)

# Clone wiki extractor from github
Thanks to [attardi](https://github.com/attardi) and GitPython

    git.Git(str(DATA_PATH)).clone("https://github.com/attardi/wikiextractor.git")

# Use wikiextractor to get data from the dump
This runs the wikiextractor cloned from github.

    run_stat = subprocess.run(
        ['python',
        # File to run
        str(DATA_PATH/'wikiextractor/WikiExtractor.py'),
        # Processing parameters get as json
        '-s', '--json',
        # Directory to store Extracted text
        '-o', str(DATA_PATH/'extracted'),
        # Archive file to extract from
        str(DATA_PATH/'tawiki-latest-pages-articles.xml.bz2')]
    )

# Get list of files extracted from the extraction folder
    files_extracted = [str(f) for f in EXTRACTED_PATH.rglob("*/*")]

# Load json data from the files
Since all files are stored as json we can load them like below, This gives us a list of dictionaries

    lang_text = [json.loads(line) 
                 for _file in files_extracted 
                 for line in open(_file)]

or this

    lang_text = []
    for _file in files_extracted:
        with open(_file, 'r') as f:
            file_lines = f.readlines() 
        for line in file_lines:
            lang_text.append(json.loads(line))

# Preprocessing
You can use any of the following, or skip the preprocessing altogether if you wish so.


## Filter English words from text

Check each word after removing their punctuations, if it is an english word

    filter_english = lambda text: ' '.join([word for word in text.split() if word.translate(str.maketrans('', '', string.punctuation)).isalpha() is False])

or

    def filter_english(text):
        words = []
        # Spltting words
        for word in text.split():
            # Replace symbols
            word = word.translate(str.maketrans('', '', string.punctuation))
            if not word.isalpha():
                words.append(word)
        return ' '.join(words)

## Form dataframe and apply preprocessing
    # Since we have a list of dictionaries.
    lang_df = pd.DataFrame(lang_text)
    lang_df['text'] = lang_df['text'].apply(filter_english)

# Store the output in compressed format
    lang_df.to_csv(DATA_PATH/'filtered_data.csv.tar.gz', header=True)

The above saved file can be loaded with `pd.read_csv`. 

You can find the full code for this in [Github gist](https://gist.github.com/mani2106/97c0af61c9fde6e6cd7f6304f1b593af) or with the output in [kaggle](https://www.kaggle.com/manimaranp/tamil-wiki-data-extraction).

# Clean up the downloaded files, (if required)

    shutil.rmtree(str(EXTRACTED_PATH))
    shutil.rmtree(str(DATA_PATH/'wikiextractor'))
    Path(DATA_PATH/'tawiki-latest-pages-articles.xml.bz2').unlink()