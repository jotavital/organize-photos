This script gets the metadata of a file (video, picture) and renames the file to the "Date Taken" attribute of the metadata. If the metadata doesn't exist, I try to get the date of the file from it's name, using some patterns.

This is to organize my picture library.

To build:
```pyinstaller --onefile .\main.pyw```
