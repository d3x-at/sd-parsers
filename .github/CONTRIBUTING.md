# Contributing to SD-Parsers

Bug fixes, additional parser modules, feature improvements and more are very welcome!

The optimal way of contributions are [pull requests](https://github.com/d3x-at/sd-parsers/pulls), although [issues](https://github.com/d3x-at/sd-parsers/issues) may be preferred for simple matters.

## General
Pull requests are accepted in the form of squash merges to the `main` branch. Please include tests for additions and code documentation where appropriate. Feel free to ask questions via [issues](https://github.com/d3x-at/sd-parsers/issues) if necessary.
* Fork the sd-parsers repository.
* Create a development branch with a name of your liking.
* To verify your changes, run tests and linting checks.
* Add new tests where needed.
* Create a pull request to merge your changes into SD-Parser's `main` branch.

## Preparing the dev environment

Clone the forked repository and change into the project directory:
  ```
  > git clone https://github.com/<your-repo-here>/sd-parsers.git
  > cd sd-parsers
  ```

Then, prepare the virtual environment and install the requirements.
### using [pdm](https://github.com/pdm-project/pdm)
  * With pdm installed (```pip install pdm```), execute:
      ```
      > pdm install -d
      ```
### using pip
  * Create & activate a virtual environment:
      ```
      > python3 -m venv .venv
      > source .venv/bin/activate
      ```
  * Install the requirements for sd-parsers using:
      ```
      > pip3 install -e .
      ```
      If this step fails, upgrade pip and try again. (using ```pip install --upgrade pip```)
      
  * Install the development tools using:
      ```
      > pip3 install pytest ruff types-Pillow
      ```

  ### run linting with:
  ```
  > (pdm run) ruff check src
  ```

  ### run tests with:
  ```
  > (pdm run) pytest
  ```

## Adding/Modifying a parser module
See the [DummyParser](../src/sd_parsers/parsers/_dummy_parser.py) module on how to structure a basic parser module.

Add the new parser to `__init__.py` inside the parsers package.

When creating a new parser module, be sure to add tests following the existing folder structure.

> [!IMPORTANT]  
> When adding test images, never add full-size images!

A script to crop images to a size of 1x1 pixels for inclusion in tests can be found in `tests/tools/`.

Use as follows:
```
python3 crop_image.py image.png
```
This creates an `image_cropped.png` next to the original file.

