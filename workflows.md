# Command workflows

These will be automated once workflows are finalized/stablized.

1. Download [Transcription dataset from the Mary Church Terrell Papers, Manuscript Division](https://www.loc.gov/item/2021387726/)

    ```
    python scripts/get_transcript_data.py -url "https://www.loc.gov/item/2021387726/"
    ```

    This will download and unzip the transcript data file to folder `./data/`

2. Download metadata from [Library JSON API](https://www.loc.gov/apis/json-and-yaml/) for each item in transcript dataset. Only do this for transcribed correspondence using the `-filter` parameter

    ```
    python scripts/get_item_data.py -in "data/2021387726/resources/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv" -filter "Project=Letters between friends, allies, and others AND AssetStatus=completed OR Project=Family letters AND AssetStatus=completed"
    ```

    By default, the metadata will be downloaded to `./data/items/`

3. Add resource data to the transcript data. Only process and output transcribed correspondence using the `-filter` parameter

    ```
    python scripts/add_resource_data_to_transcript_data.py -in "data/2021387726/resources/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv" -filter "Project=Letters between friends, allies, and others AND AssetStatus=completed OR Project=Family letters AND AssetStatus=completed" -out "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence.csv"
    ```

4. Extract additional metadata (such as Correspondent and Relation) from the transcript data from previous step

    ```
    python scripts/transcript_data_to_metadata.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence.csv"
    ```

5. Generate a text file using the data from the previous steps.

    ```
    python scripts/transcript_data_to_text.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence.csv"
    ```

6. Generate a json file using the data from the previous steps for use in the search UI

    ```
    python scripts/transcript_data_to_json.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence.csv" -out "public/data/mary-church-terrell-correspondence/transcripts.json"
    ```

7. Create a subset of the data from previous steps.

    This will create a .csv file of only family correspondence

    ```
    python scripts/transcript_data_subset.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence.csv" -filter "Project=Family letters AND AssetStatus=completed" -out "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence_family.csv"
    ```

    And a .txt file sorted by date and correspondent

    ```
    python scripts/transcript_data_to_text.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence_family.csv"
    ```

    And another .csv with only certain fields

    ```
    python scripts/transcript_data_subset.py -in "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence_family.csv" -include "Item,Tags,Date,Undated,Correspondent,Relation,ItemAssetCount,ItemAssetIndex,ResourceURL,Salutation,Recipient,Closing,Sender,IsContinuation,Notes" -out "data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence_family_lite.csv"
    ```
