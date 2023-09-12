# RPA NYTimes Scrapper

## Project Structure Explanation

- nytimes_scrapper.py: Main class responsible for navigation and article data extraction.
- config_manager.py: class responsible to store initial parameters that could change over time.
- excel_manager.py: Class responsible to handle excel files and store information.
- Tasks.py: Initial trigger file.

## Dependencies

- RPA Framework
- Robocorp

## Robocorp Input Data Example

```
{
  "search_phrase": "ecuador",
  "sections": [
    "new york"
  ],
  "months_number": 1
}

```

