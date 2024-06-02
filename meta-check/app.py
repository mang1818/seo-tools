import asyncio
import csv
from datetime import datetime
from io import StringIO

import aiohttp
from bs4 import BeautifulSoup
from flask import Flask, request, render_template, Response

app = Flask(__name__)

async def fetch_page_data(session, url):
    """Fetches meta title, description, h1 tag, and HTTP status from a URL asynchronously."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }
        async with session.get(url, headers=headers, allow_redirects=True) as response:
            http_status = response.status
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.find('title').text.strip() if soup.find('title') else ""
            description = soup.find('meta', attrs={'name': 'description'})
            description = description['content'].strip() if description else ""
            h1_tag = soup.find('h1').text.strip() if soup.find('h1') else ""
            return url, title, description, h1_tag, http_status
    except Exception as e:
        return url, "", "", "", f"Error: {e}"

async def process_urls(urls):
    """Processes a list of URLs asynchronously to fetch page data."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page_data(session, url) for url in urls]
        return await asyncio.gather(*tasks)

def generate_csv_response(data):
    """Generates a CSV response string from the extracted data."""
    output = StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(['URL', 'Meta Title', 'Meta Description', 'H1 Tag', 'HTTP Status'])
    csv_writer.writerows(data)
    csv_output = output.getvalue()
    output.close()
    return csv_output

@app.route('/', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'GET':
        return render_template('upload.html')
    else:
        uploaded_file = request.files['csv_file']
        if not uploaded_file:
            return "No file uploaded!", 400
        
        # Read the uploaded CSV file
        csv_data = uploaded_file.stream.read().decode('utf-8')
        reader = csv.reader(StringIO(csv_data))
        urls = [row[0].strip() for row in reader]
        
        # Process URLs asynchronously
        start_time = datetime.now()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(process_urls(urls))
        end_time = datetime.now()
        print(f"Total processing time: {end_time - start_time}")

        # Generate CSV response
        csv_output = generate_csv_response(results)
        return Response(csv_output, mimetype='text/csv', headers={'Content-Disposition': f'attachment;filename={get_filename()}.csv'})

def get_filename():
    """Generate a filename with current timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # Format timestamp as YYYYMMDDHHMMSS
    return f'page_data_{timestamp}'

if __name__ == '__main__':
    app.run(debug=True)
