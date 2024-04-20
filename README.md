![iCloud Photo Cleaner Logo](./logo.webp)

# iCloud Photo Cleaner

## Introduction
`icloud-photo-cleaner` is designed to simplify the task of managing and cleaning up your iCloud photo library. When thousands of photos accumulate in your phone's gallery, it becomes a daunting task to go through each one individually to decide whether to keep it or delete it. This tool enhances the process by displaying photos from the selected album one by one on your screen. Users can either keep the photo and move to the next by pressing the right arrow key, or delete the photo and proceed to the next by pressing the 'D' key. To minimize mistakes, a backup copy of each photo is saved in the specified folder before deletion. Although it still requires effort to review each photo individually, this tool makes the process more manageable with just two keystrokes, especially when dealing with large volumes, such as 15,000 photos.


## Installation

To get started with `icloud-photo-cleaner`, clone this repository and install the required dependencies.

```bash
git clone https://github.com/hlastras/icloud-photo-cleaner.git
cd icloud-photo-cleaner
pip install -r requirements.txt
```

## Usage

Run the script from the command line by providing necessary arguments. Here’s how you can use the tool:

```bash
python main.py -e your_email@example.com
```

### Command Line Arguments
* -e, --email: Required. Your iCloud account email.
* -p, --password: iCloud account password. If not provided, the tool will prompt for it.
* -o, --offset: Offset to start loading photos from. Default is 0.
* -a, --album: Album to load photos from. Default is 'All photos'.
* -l, --load: Number of photos to load into memory as buffer. Default is 10.
* -s, --save-dir: Directory to save backup photos before deletion. Default is ./backup.




>This project, including all its functionalities and code, has been created and developed by ChatGPT with human supervision.

