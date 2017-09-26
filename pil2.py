from PIL import Image
import subprocess

def cleanFile(filepath, newfilepath):
    image = Image.open(filepath)

    image = image.point(lambda x: 0 if x < 143 else 255)
    image.save(newfilepath)

    subprocess.call(['tesseract', newfilepath, 'output'])

    outputfile = open('output.txt', 'r')
    print(outputfile.read())
    outputfile.close()

cleanfile('ocr_test.jpg', 'ocr_test_clean.jpg')