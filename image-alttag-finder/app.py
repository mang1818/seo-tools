from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

app = Flask(__name__)

def extract_image_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    image_data = []
    for img_tag in soup.find_all('img'):
        image_url = img_tag.get('src')
        alt_tag = img_tag.get('alt', '')
        if image_url:
            image_data.append({'Image URL': image_url, 'Alt Tag': alt_tag})
    
    return image_data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        image_data = extract_image_data(url)
        
        # Construct absolute path for Excel file
        excel_filename = os.path.join(os.getcwd(), 'image_alt_data.xlsx')
        
        # Create DataFrame from extracted image data
        df = pd.DataFrame(image_data)
        
        # Export DataFrame to Excel
        df.to_excel(excel_filename, index=False)
        
        # Send file to user for download
        return send_file(excel_filename, as_attachment=True)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
