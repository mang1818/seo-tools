import csv
import os
from flask import Flask, render_template, request, redirect, url_for, send_file
import requests
import codecs
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder='../frontend/templates')

# Define the absolute path to the uploads directory
UPLOAD_FOLDER = os.path.abspath('backend/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_meta_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get meta description
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_tag['content'] if meta_tag else ''

        # Get title
        title_tag = soup.find('title')
        title = title_tag.string if title_tag else ''

        return title, meta_description
    except Exception as e:
        print(f"Error fetching metadata for {url}: {e}")
        return '', ''

def process_csv_file(csv_file_path):
    result_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.csv')

    with open(csv_file_path, 'r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        fieldnames = ['URL', 'Meta Title', 'Meta Description']

        # Open the result CSV file with codecs.open to specify encoding
        with codecs.open(result_file_path, 'w', encoding='utf-8', errors='replace') as result_file:
            csv_writer = csv.DictWriter(result_file, fieldnames=fieldnames)
            csv_writer.writeheader()

            for idx, row in enumerate(csv_reader, start=1):
                # Clean up row: remove empty keys and strip whitespace from keys
                cleaned_row = {key.strip(): value for key, value in row.items() if key.strip()}

                # Check for the presence of 'URL' key in the cleaned row
                if 'URL' in cleaned_row:
                    url = cleaned_row['URL']

                    # Fetch metadata for the URL
                    meta_title, meta_description = get_meta_data(url)

                    # Write metadata to the result CSV file
                    csv_writer.writerow({'URL': url, 'Meta Title': meta_title, 'Meta Description': meta_description})
                else:
                    print(f"Row {idx}: 'URL' key not found in row")
                    # Handle missing URL key (skip or log error)

    return result_file_path

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload_form.html', message='No file part')

        file = request.files['file']

        if file.filename == '':
            return render_template('upload_form.html', message='No selected file')

        if file and file.filename.endswith('.csv'):
            # Ensure the uploads directory exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            # Define the full file path
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

            # Save the file to the upload directory
            file.save(file_path)

            return redirect(url_for('download_result', filename=file.filename))

        else:
            return render_template('upload_form.html', message='Please upload a valid CSV file')

    return render_template('upload_form.html', message=None)

@app.route('/download-result/<filename>', methods=['GET'])
def download_result(filename):
    result_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(result_file_path, as_attachment=True, attachment_filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
