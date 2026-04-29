# Blockfront Tablist Scan
This program uses OCR to read the tablist and strip the info out of it. This makes Blockfront experiances crowdsourcing data extraction easier.

## Usage
```sh
python script.py image.png -gpu #if you have dedicated gpu
```
If your on windows you might need to add the argument `-load-tesseract` to load the OCR model.