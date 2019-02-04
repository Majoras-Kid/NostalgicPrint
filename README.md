# NostalgicPrint
This program aims to help reprinting manuals for your Nintendo games, distributed on the Nintendo website e.g.[1]

While these files are greate to use on your device, printing them can be a beautiful addition to your games collection. The problem with manual PDF files is that the page order is not correct for printing double sided.

NostalgicPrint will solve this problem by slicing a PDF file into single pages and merging them into a single file that can be directly printed.

# Usage

## Dependencies
See ./requirements.txt



## Linux
After installing all dependencies, start the program using:
```
python3 nostalgicprint.py -f FILENAME -d DPI_VALUE
```

Flags:
```
-f: defines filename of the manual PDF to be manipulated
-d: defines the DPI of the images extracted from the manual
```
# Links
[1] https://www.nintendo.de/Hilfe/Game-Boy-Advance/Game-Boy-Advance-Anleitung-und-zusatzliche-Dokumente/Bedienungsanleitungen-fur-Game-Boy-Advance-Spiele/Bedienungsanleitungen-fur-Game-Boy-Advance-Spiele-928652.html

[2] http://www.digitpress.com/library/manuals/nes/