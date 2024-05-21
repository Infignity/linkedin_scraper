import time
import csv, json
from requests import session

from utils import format_company, format_profile, find_username

timeout = 10

class Client():
    def __init__(self, cookies_filepath='cookies.json'):
        self.session = session()
        with open(cookies_filepath) as f:
            data = json.loads(f.read())
            self.session.cookies.update(data['cookies'])
            self.session.headers.update(data['headers'])

    def get_profile(self, username):
        res = self.session.get(f'https://linkedin.com/voyager/api/identity/profiles/{username}/profileView')
        if res.status_code not in [200, 404, 403]:
            print('** ERROR: Request failed, status code: ', res.status_code)
            raise Exception('Requst failed.')
        
        if res.status_code == 404:
            print(f'** WARN: "{username} not found.')
            return ""
        
        if res.status_code == 403:
            print(f'** WARN: "{username}" profile is forbidden.')
            return ""
        
        included = res.json()['included']
        return format_profile(included)

    def get_company(self, universal_name):
        params = {
            "decorationId": "com.linkedin.voyager.deco.organization.web.WebFullCompanyMain-12",
            "q": "universalName",
            "universalName": universal_name,
        }
        url = "https://www.linkedin.com/voyager/api/organization/companies"
        res = self.session.get(url, params=params)

        if res.status_code not in [200, 404, 403]:
            print('** ERROR: Request failed, status code: ', res.status_code)
            raise Exception('Requst failed.')
        
        if res.status_code == 404:
            print(f'** WARN: "{universal_name} not found.')
            return ""
        
        if res.status_code == 403:
            print(f'** WARN: "{universal_name}" profile is forbidden.')
            return ""
        
        return format_company(res.json()['included'], universal_name)


def get_input_profiles(input_filepath='profiles.txt', type_='person'):
    with open(input_filepath) as f:
        lines = f.readlines()
        profiles = list(filter(None, [find_username(l.strip(), type_)
                                      for l in lines]))
        return profiles


def scrape_profiles(profiles, output_filepath, type_='person'):
    client = Client()
    output_file = open(output_filepath, 'w+')
    writer = csv.DictWriter(output_file, fieldnames=['username', 'text'])
    writer.writeheader()
    for i, p in enumerate(profiles):
        print(f'#{i+1}. Scraping: {p}')
        text = client.get_profile(p)

        writer.writerow({'username': p, 'text': text})
        time.sleep(timeout)
    

if __name__ == '__main__':
    profiles = get_input_profiles(type_='person')

    print(f'Found {len(profiles)} linkedin profiles.')

    if len(profiles) > 80:
        print('** ERROR: Cannot scrape more than 80 profiles at a time.')
    elif len(profiles) == 0:
        print('** WARN: No linkedin profiles found.')
    else:
        scrape_profiles(profiles, output_filepath='profiles_output.csv')