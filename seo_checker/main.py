import openai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_page_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)
    return None

def fetch_urls_from_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')  # Use 'lxml' as the parser
        return [url.text.strip() for url in soup.find_all('loc')]
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error while fetching sitemap:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting while fetching sitemap:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error while fetching sitemap:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong while fetching sitemap:", err)
    return None

def check_seo_for_url(url):
    html_content = get_page_html(url)

    if html_content:
        title = check_title(html_content)
        meta_description = check_meta_description(html_content)
        header_tags = check_header_tags(html_content)
        alt_texts = check_image_alt_tags(html_content)

        print(f"\nSEO Check Results for {url}:")
        print(f"Title: {title}")
        print(f"Meta Description: {meta_description}")
        print(f"Header Tags: {header_tags}")
        print(f"Image Alt Texts: {alt_texts}")

        # Combine existing SEO information for GPT-3 suggestions
        content_for_gpt3 = f"Title: {title}\nMeta Description: {meta_description}\nHeader Tags: {header_tags}\nImage Alt Texts: {alt_texts}"

        # Use GPT-3 to get additional improvement suggestions
        gpt3_suggestions = get_gpt3_suggestions(content_for_gpt3)

        print("\nAdditional Suggestions from GPT-3:")
        print(gpt3_suggestions)

        # Provide custom improvement suggestions
        improvements = suggest_improvements(title, meta_description, header_tags, alt_texts)
        if improvements:
            print("\nSuggestions for Improvement:")
            for suggestion in improvements:
                print(f"- {suggestion}")
        else:
            print("\nGreat! Your SEO is in good shape.")
    else:
        print(f"Failed to fetch HTML content for {url}")

def main():
    sitemap_url = input("Enter the sitemap URL to check SEO: ")

    urls = fetch_urls_from_sitemap(sitemap_url)

    if urls:
        for url in urls:
            check_seo_for_url(url)
    else:
        print("Failed to fetch URLs from the sitemap.")

if __name__ == "__main__":
    main()
