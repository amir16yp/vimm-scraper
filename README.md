# README for Standalone Vimm.net Downloader

## Introduction

This README provides instructions on how to set up and use the standalone Vimm.net downloader. This tool is designed to download a single ROM from a Vimm.net URL.

## Prerequisites

Before running the script, ensure that you have Python 3 installed on your system. Additionally, you'll need to install some third-party libraries. The instructions below assume that you are familiar with Python and the command-line interface.

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/amir16yp/vimm-scraper/
cd vimm-scraper
```

2. **Set up a virtual environment (optional but recommended):**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. **Install the required libraries:**

```bash
pip install requests beautifulsoup4 tqdm
```

## Usage

To use the script, run it from the command line with the URL of the ROM as an argument.

```bash
python vimm-dl.py <URL>
```

Replace `<URL>` with the actual URL of the ROM you want to download from Vimm.net.

### Example

```bash
python vimm-dl.py https://vimm.net/vault/12345
```

This command would attempt to download the ROM associated with the provided URL.

## Features

- **Automatic Retry:** The script will automatically retry the download if an error occurs, with a default of 2 attempts and a 3-second delay between attempts.
- **Progress Bar:** A progress bar will be displayed in the terminal, indicating the download progress.
- **Error Handling:** The script provides clear error messages if the download fails or if the media ID cannot be found.

## Troubleshooting

If you encounter any issues:

- Make sure the URL is correct and accessible in your web browser.
- Check your internet connection.
- Ensure that all required libraries are installed and up to date.
- Confirm that Python 3 is correctly installed on your system.

## Disclaimer

This tool is for educational purposes only. Always make sure to comply with Vimm.net's terms of service when using this downloader.

## Contributing

Contributions to the repository are welcome. Please fork the repository and submit a pull request with your changes.

## License

The code is released under the [Unlicense](https://opensource.org/licenses/unlicense). Please refer to the `LICENSE` file in the repository for more information.

Please note that downloading ROMs for games that you do not own a physical copy of may be illegal in your country. Use this script responsibly.
