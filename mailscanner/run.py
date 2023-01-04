import os
import pytesseract
import time
import datetime
from PIL import Image
import fitz

# Define the path to the directory to be monitored
directory = '/root/mailscanner/input'

# Define the destination folder
destination = '/root/mailscanner/output'

# Get the current date and time
now = datetime.datetime.now()

# Format the date and time as a string in the desired format
date_string = now.strftime("%Y-%m-%d")

def extract_title_from_text(text, keywords):
    # Iterate over the keywords and check if any of them are contained in the text
    for key in keywords:
        if key in text.lower():
            # If a keyword is found, return it 
            return key
    
    # If no keyword is found, return the first line of the text
    return 'scan'


# Initialize the list of previous files
previous_files = []

#Define the list of keywords and corresponding destination folders

keywords = {
'octopus': 'Bills',
'coverdrone': 'Insurance',
'council tax': 'Council Tax',
'Legal & General': 'Insurance',
'oplo': 'Loans',
'nationwide': 'Mortgage',
'united utilities': 'Bills',
'nissan': 'Vehicles'
}



while True:
    # Get a list of the files in the directory
    files = os.listdir(directory)

    # Check for new files
    for file in files:
        if file not in previous_files:
            file_path = os.path.join(directory, file)
            file_extension = file.split('.')[-1]

            # Open the file using PIL
            if file_extension in ['jpg', 'jpeg', 'png']:
                image = Image.open(file_path)
                # Perform OCR on the image to extract the text
                text = pytesseract.image_to_string(image, lang='eng')

            elif file_extension == 'pdf':
                # Open the PDF file using PyMuPDF
                pdf_doc = fitz.open(file_path)
                # Extract the first page from the PDF file
                page = pdf_doc[0]
                # Perform OCR on the page to extract the text
                text = page.get_text('text')

                # If no text is found, try using a different OCR technique
                if not text:
                    # Convert the PDF page to an image
                    image = page.get_pixmap()
                    # Save the image to a temporary file
                    temp_file = 'temp.png'
                    image.save(temp_file)
                    # Open the image using PIL
                    image = Image.open(temp_file)
                    # Perform OCR on the image to extract the text
                    text = pytesseract.image_to_string(image, lang='eng')
                    # Delete the temporary file
                    os.remove(temp_file)

            else:
                continue
            
            # Extract the title from the text
            if text == '':
                print(f'no text found in document')
            else:
                print(text)

            title = extract_title_from_text(text, keywords)
            
            # Print the file name and the extracted title
            print(f'Processing file "{file}"...')
            print(f'Extracted title: "{title}"')
            
            # Determine the destination folder based on the title
            folder = 'Misc'
            for key, value in keywords.items():
                if key in title.lower():
                    folder = value
                    break
            
            # Create the destination folder if it doesn't exist
            destination_folder = os.path.join(destination, folder)
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            
            # Save the input file as a PDF in the destination folder using the extracted title as the file name
            if file_extension == 'pdf':
                # Initialize the output file name
                output_file = title + '_' + date_string + '.pdf'
                # Initialize the counter for the file name
                counter = 1
                # Check if the file already exists
                while os.path.exists(os.path.join(destination_folder, output_file)):
                    # If the file exists, append a number to the filename and try again
                    output_file = title + '_' + date_string + '_' + str(counter) + '.pdf'
                    counter += 1
                # Save the file
                pdf_doc.save(output_file)
            else:
                # Initialize the output file name
                output_file = title + '_' + date_string + '.' + file_extension
                # Initialize the counter for the file name
                counter = 1
                # Check if the file already exists
                while os.path.exists(os.path.join(destination_folder, output_file)):
                    # If the file exists, append a number to the filename and try again
                    output_file = title + '_' + date_string + '_' + str(counter) + '.' + file_extension
                    counter += 1
                # Save the file
                image.save(output_file)
            
            # Move the file to the destination folder
            os.rename(output_file, os.path.join(destination_folder, output_file))
            
            # Delete the original input file
            os.remove(os.path.join(directory, file))
            
            # Print a message to the console
            print(f'Output file "{output_file}" created and input file "{file}" deleted.')


    # Update the list of previous files
    previous_files = files
    print(previous_files)

    # Sleep for a while before checking for new files again
    print(f'Sleeping for 60 seconds before scanning again')
    time.sleep(10)
