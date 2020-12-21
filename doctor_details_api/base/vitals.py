import json
import re

import requests
from scrapy.http import HtmlResponse


def get_lat_long(input_location):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'client_id': 'e4e3f73a-0ceb-4d37-939e-90ddb1238360',
        'enc_data': '06/SMHzCCDQZDTORbLw9LEGdCEL/uxVNhlHR+76PyQw=',
        'if-modified-since': 'Fri, 04 Sep 2020 10:43:59 GMT',
        'origin': 'https://doctor.webmd.com',
        'timestamp': 'Fri, 04 Sep 2020 10:44:16 GMT',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    }

    params = (
        ('cache2', 'true'), ('count', 20), ('q', input_location)
    )

    url = "https://www.webmd.com/search/2/api/lhd_geotypeahead"

    response = requests.get(url=url, headers=headers, params=params)

    data = json.loads(response.content)

    lat = data['types'][0]['references'][0]['lat']
    long = data['types'][0]['references'][0]['lon']

    return lat, long


def search_doctor(business_name=None, city=None, zip_code=None, phone=None):

    lat, long = get_lat_long(zip_code)

    match_count_list = list()
    match_list = list()
    all_doctors = list()

    start = 1
    next_page = True

    while next_page:

        headers = {
            'accept': 'application/json',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'client_id': 'e4e3f73a-0ceb-4d37-939e-90ddb1238360',
            'enc_data': 'Gv2otAMicIb0oV30Tag5F0v0ozME6A3xwsTfHXXfAec=',
            'if-modified-since': 'Fri, 11 Sep 2020 06:09:05 GMT',
            'origin': 'https://www.vitals.com',
            'timestamp': 'Fri, 11 Sep 2020 06:09:34 GMT',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        }

        url = "https://www.webmd.com/search/2/api/vitals_v_search"

        params = (
            ("pt", f"{lat},{long}"),
            ("page", str(start)),
            ("query", f"vitals_overall_average_f:[* TO *] AND {business_name}")
        )

        response = requests.get(url=url, headers=headers, params=params)
        json_data = json.loads(response.content)
        doctor_collection = json_data['data']['serp']

        if not doctor_collection:
            break
        all_doctors.extend(doctor_collection)
        start = start + 1

    if not all_doctors:
        return {"response_meta": {"total_search_result": 0, "total_pages": 0},
                "matched_attribute": list(), "result": {"error": "No result found with requested params"}}

    for doctor in all_doctors:
        matches = list()
        match_count = 0

        names = business_name.split()

        if names[0].lower() in doctor['firstname'].lower() or names[0].lower() in doctor['lastname'].lower():
            match_count += 1
            matches.append(names[0])

        if names[-1].lower() in doctor['lastname'].lower() or names[-1].lower() in doctor['firstname'].lower():
            match_count += 1
            matches.append(names[-1])

        if len(names) > 2 and "middlename" in doctor:
            m_name = names[1]
            if "." in m_name:
                m_name = m_name.split(".")[0]
            if doctor['middlename'].lower().startswith(m_name.lower()):
                match_count += 1
                matches.append(names[1])

        if 'location_nimvs' in doctor:
            details = str(doctor['location_nimvs'])
            if city:
                if city.lower() in details.lower():
                    match_count += 1
                    matches.append(city)

            if zip_code:
                if zip_code.lower() in details.lower():
                    match_count += 1
                    matches.append(zip_code)

            if phone:
                if phone.lower() in details.lower():
                    match_count += 1
                    matches.append(phone)

        match_count_list.append(match_count)
        match_list.append(matches)

    max_count = max(match_count_list)
    if max_count > 1:

        best_match = match_count_list.index(max_count)
        matched_doctor = all_doctors[best_match]

        if matched_doctor.get('firstname', '') in business_name or matched_doctor.get('lastname', '') in business_name:
            final_result = dict()
            final_result['suffix'] = matched_doctor.get('suffix', '')
            final_result['firstName'] = matched_doctor.get('firstname', '')
            final_result['lastName'] = matched_doctor.get('lastname', '')
            final_result['fullName'] = matched_doctor.get('fullname', '')
            final_result['bio'] = matched_doctor.get('bio_s', '')
            final_result['address'] = matched_doctor.get('deliveryaddress', '')
            final_result['city'] = matched_doctor.get('city', '')
            final_result['state'] = matched_doctor.get('state', '')
            final_result['postalCode'] = matched_doctor.get('postalcode', '')
            final_result['profileurl'] = "https://www.vitals.com" + matched_doctor.get('profileurl', '')

            return {"response_meta": {"total_search_result": len(match_count_list), "total_pages": start},
                    "matched_attribute": match_list[best_match],
                    "result": final_result}

    return {"response_meta": {"total_search_result": len(match_count_list), "total_pages": start},
            "matched_attribute": list(), "result": {"error": "No Result Found"}}


def get_profile_data(url):
    api_response = dict()
    try:
        session = requests.session()
        session.proxies.update({
            "https": "https://lum-customer-xbyte-zone-unblocker-unblocker:hgn3xkt4juz6@zproxy.lum-superproxy.io:22225",
            "http": "http://lum-customer-xbyte-zone-unblocker-unblocker:hgn3xkt4juz6@zproxy.lum-superproxy.io:22225"
        })
        session.headers.update({
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        })
        response = session.get(url, verify=False)

        response = HtmlResponse(url=url, body=response.content)

        api_response['Doctor_name'] = response.xpath('//div[@class="webmd-card__header"]/meta[@itemprop="name"]/@content').get()

        api_response['Doctor_description'] = response.xpath('//p[@itemprop="description"]//text()').get()

        office_address = list()
        for add in response.xpath('//div[@temprop="address"]'):
            add_title = add.xpath('normalize-space(.//span[@itemprop="name"]/text())').get()
            street_address = add.xpath('normalize-space(.//span[@itemprop="streetAddress"]/text())').get()
            locality = add.xpath('normalize-space(.//span[@itemprop="addressLocality"]/text())').get()
            address_region = add.xpath('normalize-space(.//span[@itemprop="addressRegion"]/text())').get()
            postal_code = add.xpath('normalize-space(.//span[@itemprop="postalCode"]/text())').get()

            office_address.append({
                'Address_Title': add_title,
                'Street_address': street_address,
                'Locality': locality,
                'Address_region': address_region,
                'Postal_code': postal_code

            })

        api_response['Doctor_Office_address'] = office_address

        json_data = json.loads(
            "".join(re.findall(r"window\.__INITIAL_STATE__=(.*?);\(function", response.text)).strip())
        json_data = json_data['profile']
        api_response["profileUrl"] = url
        api_response["name"] = dict()
        api_response["name"]['fullName'] = json_data.get('fullname', '')
        api_response["name"]['suffix'] = json_data.get('suffix', '')
        api_response["name"]['firstName'] = json_data.get('firstname', '')
        api_response["name"]['middleName'] = json_data.get('middlename', '')
        api_response["name"]['lastName'] = json_data.get('lastname', '')
        api_response["jobTitle"] = json_data.get('jobtitledesc', '')
        api_response["professionType"] = "".join(json_data.get('professiontype_mvs', ''))
        api_response["specialtyNames"] = json_data.get('specialtynames', '')
        overview = json_data.get('bio_s', '')
        api_response["overview"] = overview.replace("\n", "")

        api_response["degree"] = json_data.get('degreeabbr', '')
        api_response["overallRating"] = json_data.get('rating_score', '')
        api_response["reviewsCount"] = json_data.get('review_count_d', '')
        api_response["locations"] = list()

        for location in json_data['location_nimvs']:
            loc = dict()
            loc['practiceName'] = location.get('PracticeName', '')
            loc['locationName'] = location.get('LocationName', '')
            loc['locationPhone'] = location.get('LocationPhone', '')
            loc['address'] = location.get('address', '')
            loc['city'] = location.get('city', '')
            loc['state'] = location.get('state', '')
            loc['zipcode'] = location.get('zipcode', '')
            loc['geolocation'] = location.get('geolocation', '')
            loc['practiceWebsite'] = location.get('PracticeWebsite', '')
            loc['hours'] = location.get('hours', '')
            api_response["locations"].append(loc)

        review_url = url.replace(".html", "/write-review")
        response = session.get(review_url)

        # CONVERTING THE RESPONSE INTO THE HTML-RESPONSE, SO THAT WE CAN USE XPATH ON THEM FOR EXTRACTING THE DATA
        response = HtmlResponse(url=url, body=response.content)

        reviews = list()
        for review in response.xpath('//div[@itemprop="review"]'):
            rating = review.xpath('.//div[@class="star-rating"]/div/div/@style').get('')
            rating = "".join(re.findall(r'\d', rating))
            rating = int(rating) / 20
            username = review.xpath('normalize-space(.//h2[@class="card-title"]/span/text())').get('')
            body = review.xpath('.//p[@itemprop="reviewBody"]/text()').get('')
            date = review.xpath('.//meta[@itemprop="datePublished"]/@content').get('')
            reviews.append({
                'ratings': rating,
                'title': username,
                'user': "",
                'text': body,
                'date': date,

            })
        api_response['reviews'] = reviews

        return {"result": api_response}

    except Exception as e:
        print(e)

        return {"error": {"msg": "requests block by the target website... please try after sometime..."}}
