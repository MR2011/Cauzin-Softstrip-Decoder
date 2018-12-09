# Cauzin Softstrip Decoder
The Cauzin Softstrip is a two-dimensional bar code developed by Cauzin Systems. It was used to encode all kind of digital data such as software, text files or graphics. Unfortunately, the Cauzin Softstrip was not as successful as anticipated and disappeared a few years later after its release. 
It is already difficult to obtain a working Softstrip Reader and it will probably be impossible in a few years. Therefore, a digital Softstrip decoder was created so people without access to an optical reader can decode the Cauzin Softstrip. 

### Installation

This project requires [Python](https://www.python.org/) 3.6 to run.

Install the dependencies:

```sh
$ pip install -r requirements.txt
```
The GUI can be started with:
```sh
$ python QtGui.py
```
However, it is recommended to extract Softstrips with an image manipulation program such as [Gimp](https://www.gimp.org/) and start the decoding with the command line:

```sh
$ python SoftstripDecoder.py Softstrips/icons/glyphicons-social-9-tumblr.png
```
### Configuration

The following configuration options exist

| Option | Description |
| ------ | ------ |
| row_decoder | Choose 0 for the algorithmic row decoding approach and 1 for the CNN approach. |
| row_extractor | Choose 0 for the algorithmic row decoding approach and 1 for the CNN approach. |
| timeout | The decoding process will be stopped after N minutes. |

It is recommended to use the algorithmic row extractor and the CNN approach for the row decoding.
**Important: the CNN row extractor does ONLY work with the CNN row decoder**

## Training 
### Row Decoding
In order to generate training data for the row decoder CNN first run:
```sh
$ python nn/generate_trainings_data.py
```
This will generate the rows with labeled dibits. Please inspect following files to see how the input data is structured:
- textfiles/qwiksort1_reduced.txt
- textfiles/qwiksort1_gray_rows.txt

The *reduced* file contains all rows as a simple text file. Each color is as a binary value represented. A black pixel is noted as **1** and a white pixels as **0**. The *gray_rows* file contains each row as an array with one byte **grayscale** values.

In the next step, the dibits can be extracted from the labeled rows:
```sh
$ python nn/extract_blocks.py
```
**Important: Please set the correct paths for the input and output data in both files.**

Once the training data is generated, the CNN can be trained:
```sh
$ python nn/train_cauzin_model.py
```
**Important: Please set the correct paths for the input and output data.**

### Row Extraction
The training data can be generated with:
```sh
$ python nn/generate_coordinate_train_data.py
```
**Important: Please set the correct paths for the input and output data.**
Please inspect following files to see how the input data is structured:
- textfiles/qwiksort1_rows_by_hand.txt
- textfiles/textfiles/qwiksort1_gray_matrix.txt

The file *qwiksort_rows_by_hand* contains the binary values of each row. Rows are separated from eatch other with an empty line. The file *qwiksort1_gray_matrix* contains the corresponding grayscale values.

Once the training data is generated, the CNN can be trained:
The training data can be generated with:
```sh
$ python nn/train_cauzin_row_model.py
```
**Important: Please set the correct paths for the input and output data.**
