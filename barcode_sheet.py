import os
import pandas as pd 
from PIL import Image, ImageDraw, ImageFont
from barcode import EAN13
from barcode.writer import ImageWriter

cwd = os.path.dirname(os.path.realpath(__file__))

def create_barcode(number, file_name):
    my_barcode = EAN13(number) # Can be adjusted to your preferred barcode type
    my_barcode.writer = ImageWriter()
     
    # ensure no invalid characters in the file name
    file_name = file_name.replace('/', '')

    file_path = os.path.join(cwd, file_name)
    my_barcode.save(file_path)


def arrange_barcodes():
    # read in all .png files in the directory
    files = [f for f in os.listdir(cwd) if f.endswith('.png')]
    
    # iterate through the files
    for file in files:
        # get name of the file without the extension
        name = file.split('.')[0]
        
        # create image with the name of the product using pillow
        img = Image.new('RGB', (500, 300), color=(255, 255, 255))
        name_path = os.path.join(cwd, name + '_.png')
        
        # open the file
        img.save(name_path)
        img = Image.open(name_path)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('arial.ttf', 22)
        
        # add the name of the product to the top of the image
        draw.text((40, 10), name, (0, 0, 0), font=font)
        
        # place the barcode on the image
        file_path = os.path.join(cwd, file)
        barcode = Image.open(file_path)
        img.paste(barcode, (0, 35))  # Adjust the position of the barcode as needed
        img.save(name_path)
        
        # delete the original barcode
        os.remove(file_path)


def arrange_one_page():
    A4_WIDTH = 2480
    A4_HEIGHT = 3508
    BARCODE_WIDTH = 500
    BARCODE_HEIGHT = 300
    MARGIN = 55
    # read in all .png files in the directory
    files = [f for f in os.listdir(cwd) if f.endswith('_.png')]
    
    # initialise variables for A4 page
    current_x = MARGIN
    current_y = MARGIN
    current_page = 1
    new_img = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), color=(255, 255, 255))
    
    # iterate through the files
    for file in files:        
        # open the barcode image
        barcode_path = os.path.join(cwd, file)
        barcode = Image.open(barcode_path)
        
        # check if the image can fit on the current page
        if current_x + BARCODE_WIDTH + MARGIN > A4_WIDTH:
            current_x = MARGIN
            current_y += BARCODE_HEIGHT + MARGIN
        
        # check if the image can fit on the current page
        if current_y + BARCODE_HEIGHT + MARGIN > A4_HEIGHT:
            # Save the current page and initialize a new one
            new_img.save(os.path.join(cwd, f'barcodes_page_{current_page}.png'))
            current_page += 1
            new_img = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), color=(255, 255, 255))
            current_y = MARGIN
        
        # paste the barcode onto the page
        new_img.paste(barcode, (current_x, current_y))
        
        # update current position for the next barcode
        current_x += BARCODE_WIDTH + MARGIN

        # delete the original barcode
        os.remove(barcode_path)
    
    # Save the last page
    if current_y != MARGIN:
        new_img.save(os.path.join(cwd, f'barcodes_page_{current_page}.png'))

if __name__ == '__main__':
    # read in the data
    csv = 'product_list.csv'
    csv_path = os.path.join(cwd, csv)
    df = pd.read_csv(csv_path)
    # iterate through the rows
    for index, row in df.iterrows():
        # pad number with 0 to make it 12 digits for EAN13 standards
        if len(str(row['Barcode'])) < 12:
            number = str(row['Barcode']).zfill(12)
            create_barcode(number, row['Description'])
        elif len(str(row['Barcode'])) > 12:
            print(f"Barcode for {str(row['Description'])} is too long")
        else:
            create_barcode(str(row['Barcode']), row['Description'])
    arrange_barcodes()
    arrange_one_page()
    print('Done')
