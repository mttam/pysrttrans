# PySrtTrans
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub last commit](https://img.shields.io/github/last-commit/mttam/pysrttrans)](https://github.com/mttam/pysrttrans/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/mttam/pysrttrans)](https://github.com/mttam/pysrttrans/issues)

## Project Description

PySrtTrans is a Python tool for automatically translating SRT subtitle files.

## Main Features

- Automatic translation of SRT files using Google Generative AI API
- Intuitive graphical user interface based on CustomTkinter
- Support for selecting multiple SRT files
- Automatic handling of daily request limits
- Detailed logging of operations
- Ability to customize the translation prompt

## How to Use

1. Install required dependencies (`pip install -r requirements.txt`)
2. Configure API key and translation prompt in `config.py`
3. Run the script `py_srt_trans_ui.py`

## Project Structure

- `pysrttrans/`: Main project folder
  - `py_srt_trans.py`: Main class for handling translations
  - `py_srt_trans_ui.py`: Graphical User Interface
  - `config.py`: Project configuration
- `srt_raw/`: Folder for original SRT files
- `srt_trans/`: Folder for translated SRT files

## Dependencies

- `pysrt`: For handling SRT files
- `google-generativeai`: For integration with translation API
- `customtkinter`: For graphical user interface

## Contributing

Contributions are welcome! If you want to improve the project, follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

## License

This project is released under the MIT License. See the `LICENSE` file for details.


## Acknowledgments

Thanks to Google for the Generative AI API and the creators of the Python libraries used in the project.
