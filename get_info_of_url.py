import socket
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}

def get_ip_address(url):
    try:
        ip = socket.gethostbyname(url)
        IP = ip
        return IP
    except:
        pass


def remove_http_https_and_after_coil(url):
    """ Get a url and remove the http/https and everything after the .co.il"""
    parsed = urlparse(url)
    schemeless_url = parsed.netloc + parsed.path
    coil_index = schemeless_url.find('.co.il')
    if coil_index != -1:
        schemeless_url = schemeless_url[:coil_index + len('.co.il')]

    return schemeless_url


def create_dictionary(new_text, url):
    dictionary = {}
    dictionary = {'url': url}
    if new_text is None:
        return dictionary
    lines = new_text.split('\n')
    for line in lines:
        if line.startswith('person:'):
            dictionary['person'] = line.split(':', 1)[1].strip()
        elif line.startswith('phone:'):
            dictionary['phone'] = line.split(':', 1)[1].strip()
        elif line.startswith('e-mail:'):
            dictionary['email'] = (line.split(':', 1)[1].strip()).replace(' AT ', '@')
    return dictionary


def get_whois_info(url):
    response = requests.get(f'https://who.is/whois/{url}', headers=headers, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        return None


def get_text_between_phrases(text, start_phrase, end_phrase):
    start_index = text.find(start_phrase)
    end_index = text.find(end_phrase)
    if start_index != -1 and end_index != -1:
        return text[start_index:end_index + len(end_phrase)]
    else:
        return None


def get_contact(new_list):
    data = []
    for list in new_list:
        try:
            url = list[2]
            whois_info = get_whois_info(url)
            new_text = get_text_between_phrases(whois_info, "person:", "registrar info:")
            ip_of_server = get_ip_address(url)
            dictionary = create_dictionary(new_text, url, list[0], list[1], list[3], ip_of_server)
            if new_text is not None:
                data.append(dictionary)  # Add the dictionary to the list
                print(dictionary)
            else:
                pass
        except:
            pass

    return data

def create_statistic_dictionary(text, url):
    dictionary = {'url': url}
    clean_url = remove_http_https_and_after_coil(url)

    traffic_report_summary = get_text_between_phrases(text, "traffic_report_summary", '<div>Is this your site?')

    pattern = r'<div>(.*?)<span>(.*?)<\/span>'

    traffic_report_summary_dict = extract_data(traffic_report_summary,pattern)

    traffic_report = get_text_between_phrases(text, '<dt style="background-position:-6px -197px;">Global Reach:', '<span class="estimate_note">*All traffic values')

    pattern = r'<dt style="background-position:-?\d+px -?\d+px;">(.*?)</dt><dd>(.*?)</dd>'

    traffic_report_dict = extract_data(traffic_report, pattern)

    try:
        uniqe = get_text_between_phrases(text,"Monthly Unique Visitors (SEMrush):</dt><dd>","Monthly Visits (SimilarWeb)")
        uniqe = uniqe.split("<dd>", 1)[1]
        uniqe = uniqe.split("</dd>", 1)[0]
        dictionary["Monthly Uniqe Visitors"] = uniqe
    except:
        pass

    traffic_sources_report = get_text_between_phrases(text, '<h3>Desktop <span>vs Mobile</span></h3>', "Total Visits Last")

    sources_pattern = r'<dt.*?>(.*?)<\/dt><dd><span.*?>(.*?)<\/span><\/dd>'

    traffic_sources_dict = extract_data(traffic_sources_report, sources_pattern)

    earning = get_text_between_phrases(text, 'id="earning_m', '*All earnings')
    pattern = r'<dt>(.*?)</dt><dd>(.*?)</dd>'
    earning_dict = extract_data(earning, pattern)

    country_pattern = r'<dt class="flag flag-\w{2}">&nbsp;</dt>\s*<dd>\s*<a[^>]*>(.*?)<\/a>.*?<span[^>]*>(.*?)<\/span>'
    by_country = get_text_between_phrases(text,'<dl class="visitors_by_country">', '<section id="backlinks">')
    country_dict = extract_data(by_country,country_pattern)


    dict_list = [dictionary,country_dict, earning_dict, traffic_report_summary_dict, traffic_report_dict, traffic_sources_dict]
    result_dict = {key: value for d in dict_list if d for key, value in d.items()}


    return result_dict


def extract_data(text, pattern):
    try:
        matches = re.findall(pattern, text)
    except:
        return None

    data_dict = {}

    for match in matches:
        key, value= match
        data_dict[key.strip()] = value.strip()

    return data_dict
