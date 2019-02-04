# NostalgicPrint
This program aims to help reprinting manuals for your Nintendo games, distributed on the Nintendo website e.g.[1]

While these files are greate to use on your device, printing them can be a beautiful addition to your games collection. The problem with manual PDF files is that the page order is not correct for printing double sided.

NostalgicPrint will solve this problem by slicing a PDF file into single pages and merging them into a single file that can be directly printed.

# Usage
As we are using threads in order to paralelize this program, other processes on your computer may be slowed down while execution.
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

# Output
The manipulated manual pdf is found at 
```
./final_manual.pdf
```

# Errors
When receiving a 
```
[-] Number of images no multiple of 2 - cannot merge

```
error, delete all .png files in the ./temp/ folder and try again
# Example
```
python3 nostalgicprint.py -f "./test.pdf" -d 150

```
will create a 
```
./final_manual.pdf
```
with a DPI of 150 created from the test.pdf manual that is located in the current folder
# Links
[1] https://www.nintendo.de/Hilfe/Game-Boy-Advance/Game-Boy-Advance-Anleitung-und-zusatzliche-Dokumente/Bedienungsanleitungen-fur-Game-Boy-Advance-Spiele/Bedienungsanleitungen-fur-Game-Boy-Advance-Spiele-928652.html

[2] http://www.digitpress.com/library/manuals/nes/