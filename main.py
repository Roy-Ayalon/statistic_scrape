import time

import requests
import re
import get_info_of_url as info
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.request
from selenium.webdriver.common.by import By





import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

input_file = "urls.txt"

output_file = "urls_with_keywords.txt"


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}

"""
The function attempts to fetch the source code of a given URL, and if successful, it writes the source code
to a text file named based on the provided index. This allows for easy storage and analysis of web page
contents. In case of an error during the request, it prints an error message and returns None.
"""
def fetch_source_code(url, clean_url):
    try:

        driver = webdriver.Chrome()

        driver.get(f"https://hypestat.com/info/{clean_url}")

        #driver.refresh()
        #source = urllib.request.urlopen(f"https://hypestat.com/info/{clean_url}").read()
        button = driver.find_element(By.ID, "button")
        button.click()
        time.sleep(60)
        page_source = driver.page_source
        #driver.quit()
        #page_source = driver.find_element("//*").get_attribute("outerHTML")
    except requests.exceptions.RequestException as error:
        print(f"can't get url #{clean_url} because {error}")
        return None

    #response = requests.get(url, headers=headers, verify=False)
    filename = f"source_codes/source_code_{clean_url}.txt"
    with open(filename, 'w', encoding='utf-8') as source_code_file:
        source_code_file.write(page_source)
    return page_source



"""
The function searches for keywords in a specified file by reading the content of both the target file
and a dictionary file containing the keywords. If any of the keywords are found in the target file's content,
it returns True. If the provided file path is None or no keywords are found, it returns False.
"""
def search_keywords_in_file(file_path):
    if file_path is None:
        return False
    with open("dictionary.txt", 'r', encoding='utf-8') as dict:
        keywords = dict.read().splitlines()
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        for keyword in keywords:
            if keyword in content:
                return True
    return False

"""
The function opens the file specified by 'urls_file' in read ('r') mode, reads its contents, and splits
the data into separate lines. It then returns a list of these lines, making it easy to work with the
individual URLs or data from the file.
"""
def open_url_file(input_file):
    with open(input_file, 'r') as urls_file:
        file_data = urls_file.read()
        lines = file_data.splitlines()
    return lines

"""
The function exports a list of URLs that contain keywords to an output file. It iterates through the 'found_urls'
list and writes each URL to the specified output file, with one URL per line. This is useful for saving a list
of URLs that meet specific criteria for further reference or analysis.
"""
def export_urls_with_keywords(found_urls,output_file):
    # Write URLs with keywords to the output file
    with open(output_file, 'a') as output_urls_file:
        for url in found_urls:
            clean_url = re.sub(r'https?://([^/]+).*', r'\1', url)
            whois_info = info.get_whois_info(clean_url)
            new_text = info.get_text_between_phrases(whois_info, "person:", "registrar info:")
            ip_of_server = info.get_ip_address(clean_url)
            dictionary = info.create_dictionary(new_text, url, None, None, None, ip_of_server)
            output_urls_file.write(str(dictionary) +'\n')
    print("Process complete. URLs with keywords are saved in", output_file)


"""
The function processes a list of URLs by iterating through them, fetching their source code, and searching
for keywords in the source code. If keywords are found in the source code, the URL is added to the 'found_urls'
list. The function also provides feedback on the export process, indicating the successful export of each file.
"""
def process_urls(urls):
    results = []
    money = 0.0
    for url in urls:
        clean_url = re.sub(r'https?://([^/]+).*', r'\1', url)
        source_code_file = fetch_source_code(url, clean_url)
        print(f"file number {clean_url} has exported successfully")
        whois_info = info.get_whois_info(clean_url)
        #text = info.get_text_between_phrases(source_code_file, "Traffic Analysis", "backlinks")
        #whois_text = info.get_text_between_phrases(whois_info, "person:", "registrar info:")
        #dictionary = info.create_dictionary(whois_text,url)
        statistic = info.create_statistic_dictionary(source_code_file, url)
        results.append(statistic)
        try:
            num = statistic['Yearly Revenue:'].replace('$', '')
            num = num.replace(',', '')
            money += float(num)
        except KeyError:
            pass
        with open(output_file,'a') as output:
            output.write(statistic)
        print(f"money: {money}")
    return results



urls = open_url_file("urls.txt")
urls = process_urls(urls)
print(urls)
