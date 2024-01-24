# _At the Table_ Workflow

## Requirements

This workflow requires [Python 3.8+](https://www.python.org/downloads/)

```
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

## Steps

1. Download [Transcription dataset from the Mary Church Terrell Papers, Manuscript Division](https://www.loc.gov/item/2021387726/)

    ```
    python scripts/get_transcript_data.py -url "https://www.loc.gov/item/2021387726/"
    ```

    This will download and unzip the transcript data file to folder `./data/`

2. Download metadata from [Library JSON API](https://www.loc.gov/apis/json-and-yaml/) for each item in transcript dataset. Only do this for transcribed correspondence using the `-filter` parameter

    ```
    python scripts/get_item_data.py -in "data/2021387726/resources/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv" -filter "AssetStatus=completed"
    ```

    By default, the metadata will be downloaded to `./data/items/`

3. Add resource data to the transcript data. Only process and output transcribed correspondence using the `-filter` parameter

    ```
    python scripts/add_resource_data_to_transcript_data.py -in "data/2021387726/resources/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv" -filter "AssetStatus=completed" -out "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv"
    ```

4. Parse dates within the transcript data

    ```
    python scripts/parse_dates.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv" -out "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_with-dates.csv"
    ```

    Make a best-guess estimation of dates of documents given metadata and transcript dates

    ```
    python scripts/resolves_dates.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_with-dates.csv"
    ```

5. Detect language of transcripts

    ```
    python scripts/detect_languages.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_with-dates.csv"
    ```

6. Generate prompts from the transcripts, filtering by language and mediums

    ```
    python scripts/get_prompts.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_with-dates.csv" -filter "lang=en AND Project IN LIST Family letters|Speeches and writings|Diaries and journals: 1888-1951" -out "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_prompts.csv"
    ```

7. Publish the prompts to the user interface. Optionally pass in a list of "starred" prompts that you want to give weight to.

    ```
    python publish_prompts.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_with-dates.csv" -prompts "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_prompts.csv" -starred "data/mary-church-terrell-starred-prompts.txt" -out "public/data/mary-church-terrell/prompts.json"
    ```

## Some additional tasks for convenience

- Extract additional metadata (such as Correspondent and Relation) from the transcript data from previous step

    ```
    python scripts/transcript_data_to_metadata.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv"
    ```

- Generate a text file using the data from the previous steps.

    ```
    python scripts/transcript_data_to_text.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.txt"
    ```

- Create a subset of the data from previous steps.

    This will create a .csv file of only family correspondence

    ```
    python scripts/transcript_data_subset.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence.csv" -filter "Project=Family letters AND AssetStatus=completed" -out "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence_family.csv"
    ```

    And a .txt file sorted by date and correspondent

    ```
    python scripts/transcript_data_to_text.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence_family.text"
    ```

    And another .csv with only certain fields

    ```
    python scripts/transcript_data_subset.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence_family.csv" -include "Item,Tags,Date,Undated,Correspondent,Relation,ItemAssetCount,ItemAssetIndex,ResourceURL,Salutation,Recipient,Closing,Sender,IsContinuation,Notes" -out "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence_family_lite.csv"
    ```
