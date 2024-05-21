import textwrap, calendar
import re


def format_profile(included):
    # name, position, about and area
    profile = ""
    for item in included:
        if item['$type'] == "com.linkedin.voyager.identity.profile.Profile":
            profile = textwrap.dedent(f"""
                Name: {item.get('firstName')} {item.get('lastName')}
                Headline: {item.get('headline')}
                Industry name: {item.get('industry')}
                Location: {item.get('geoLocationName')} {item.get('geoCountryName')}
                Summary: {item.get('summary')}
            """)

    # experience
    experience = "Experiences:"
    for item in included:
        if item['$type'] == "com.linkedin.voyager.identity.profile.Position":
            company_name = item.get('companyName')
            description = item.get('description')
            location = item.get('locationName')
            title = item.get('title')
            time_period = item['timePeriod']
            time_period_str = format_time_period(time_period)

            experience += textwrap.dedent(f"""
                {title} at {company_name}
                {time_period_str}
                Location: {location}
            """)
            if description:
                experience += f"Job description: {description}\n"

    # education
    education = "Education:"
    for item in included:
        if item["$type"] == "com.linkedin.voyager.identity.profile.Education":
            degree = item.get("degreeName")
            school = item.get("schoolName")
                
            time_period = item['timePeriod']
            time_period_str = format_time_period(time_period)
            mini_edu = textwrap.dedent(f"""
                {school}
                Degree: {degree}
                {time_period_str}
            """)
            if item.get('activities'):
                mini_edu += f"Activities: {item.get('activities')}"

            if item.get('fieldOfStudy'):
                mini_edu += f"Field: {item.get('fieldOfStudy')}"
            
            if item.get('honors'):
                mini_edu += f"Honors: {item.get('honors')}"
                
            education += mini_edu + "\n"

    # skills
    skills = []
    for item in included:
        if item['$type'] == 'com.linkedin.voyager.identity.profile.Skill':
            skills.append(item.get('name'))
    skills = 'Skills:\n' + ', '.join(skills)

    return "\n".join([profile, experience, education, skills])


def format_time_period(time_period):
    start_date, end_date = None, None
    if time_period:
        if time_period.get('startDate'):
            start_date = str(time_period['startDate']['year'])
            if time_period['startDate'].get('month'):
                start_date = calendar.month_name[time_period['startDate']['month']] + ',' + start_date
        if time_period.get('endDate'):
            end_date = str(time_period['endDate']['year'])
            if time_period['endDate'].get('month'):
                end_date = calendar.month_name[time_period['endDate']['month']] + ',' + end_date
    
    date_str = ""
    if start_date: date_str += f"From {start_date} "
    if end_date: date_str += f"to {end_date}"
    return date_str

def format_company(included, public_name):
    about = ""
    industries = []
    for item in included:
        if item['$type'] == "com.linkedin.voyager.organization.Company" and item['universalName'] == public_name:
            name = item.get('name')
            if name:
                about += name + '\n'

            tagline = item.get('tagline')
            if tagline: about += f"Tagline: {tagline}" + "\n"

            description = item.get('description')
            if description: about += f"Description: {description}\n"
            
            company_page_url = item.get('companyPageUrl')
            if company_page_url: about += f"Company page url: {company_page_url}\n"

            company_type = item.get('companyType')
            if company_type and company_type.get('localizedName'):
                about += f"Company type: {item['companyType']['localizedName']}\n"

            confirmed_locations = item.get('comfirmedLocations')
            if confirmed_locations:
                about += "Locations:\n"
                for location in confirmed_locations:
                    location.pop('$type')
                    about += str(location)

            founded_on = item.get('foundedOn')
            if founded_on and founded_on.get('year'): about += f"Founded on: {founded_on['year']}\n"

            headquarter = item.get('headquarter')
            if headquarter:
                about += (f"Headquarter:"
                    f" {headquarter.get('city')}, {headquarter.get('geographicArea')}, {headquarter.get('country')}\n")

            staff_range = item.get('staffCountRange')
            if staff_range:
                about += "Staff range: "
                if staff_range.get('start'):
                    about += f"{staff_range.get('start')}"
                if staff_range.get('end'):
                    about += f"-{staff_range.get('end')}\n"
                else:
                    about += "+\n"

            members = item.get('staffCount')
            if members:
                about += f"Associated members: {members}"
        
        if item['$type'] == "com.linkedin.voyager.common.Industry":
            if item.get('localizedName'):
                industries.append(item['localizedName'])

    if industries:
        about += "\nIndustries: " + ', '.join(industries)

    return about


def get_username_from_included(included):
    for item in included:
        if item['$type'] == "com.linkedin.voyager.identity.shared.MiniProfile":
            return item.get("publicIdentifier")
        

def find_username(url, type_="person"):
    if type_ == "company":
        match = re.search(r'linkedin.com\/company\/.*?(\?|$)', url)
        if match:
            return match.group(0).replace(r'linkedin.com/company/', '').replace('?', '').strip()
        
        return match

    match = re.search(r'linkedin.com\/in\/.*?(\?|$)', url)
    if match:
        return match.group(0).replace(r'linkedin.com/in/', '').replace('?', '').strip()
    
    match = re.search(r'\/people\/([^,]+)', url)
    if match:
        return match.group(0).replace('/people/', '').strip()

    return match
