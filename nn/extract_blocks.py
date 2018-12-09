import os
import os.path
import cv2
import glob

IMG_FOLDER = 'data/input'
OUTPUT_FOLDER = 'data/output'


def extract_single_blocks(img_file):
    filename = os.path.basename(img_file)
    label = os.path.splitext(filename)[0]

    gray = cv2.imread(img_file, cv2.IMREAD_GRAYSCALE)

    img_height, img_width = gray.shape
    block_width = (img_width / len(label))

    for index, block_text in enumerate(label):
        x_start = int(round(index * block_width))
        x_end = int(round(x_start + block_width))
        block_image = gray[0:img_height, x_start:x_end]
        save_path = os.path.join(OUTPUT_FOLDER, block_text)

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        p = OUTPUT_FOLDER + '/' + block_text + "/" + block_text + "_" + str(index) + "_" + label +  ".png"
        cv2.imwrite(p, block_image)


def extract_dibit_blocks(img_file):
    filename = os.path.basename(img_file)
    correct_text = os.path.splitext(filename)[0].split('_')[1]
    gray = cv2.imread(img_file, cv2.IMREAD_GRAYSCALE)

    img_height, img_width = gray.shape
    block_width = (img_width / len(correct_text))

    correct_text = correct_text[5:-5]
    skipped = block_width * 5
    i = 0
    old_correct_text = correct_text
    while correct_text:
        dibit = correct_text[0:2]
        x_start = int(round(skipped + i * block_width * 2))
        x_end = int(round(x_start + block_width * 2))
        block_image = gray[0:img_height, x_start:x_end]

        save_path = os.path.join(OUTPUT_FOLDER, dibit)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        p = OUTPUT_FOLDER + '/' + dibit + "/" + dibit + "_" + str(i) + "_" + old_correct_text +  ".png"
        cv2.imwrite(p, block_image)
        i += 1
        correct_text = correct_text[2:]


img_files = glob.glob(os.path.join(IMG_FOLDER, "*"))
counts = {}


for (i, img_file) in enumerate(img_files):
    print("[INFO] processing image {}/{}".format(i + 1, len(img_files)))
    extract_dibit_blocks(img_file)
