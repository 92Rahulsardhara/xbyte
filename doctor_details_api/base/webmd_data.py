import json
import re

import requests


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


def search_doctor(business_name=None, city=None, zip_code=None, phone=None, request_id=None):
    lat, long = get_lat_long(zip_code)

    all_doctors = list()
    match_count_list = list()
    match_list = list()

    start = 0
    next_page = True
    while next_page:
        params = [
            ("sortby", "bestmatch"), ("distance", 40), ("newpatient", ""), ("isvirtualvisit", ""), ("minrating", "0"),
            ("start", start), ("q", business_name), ("pt", f"{lat}%2C{long}"), ("specialtyid", ""), ("insuranceid", "")
        ]

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

        url = "https://www.webmd.com/search/2/api/lhd_v_search"
        while True:
            try:
                response = requests.get(url=url, headers=headers, params=params)
                json_data = json.loads(response.content)
                doctors = json_data['data']['response']
                break
            except Exception as e:
                open(f"C:/HTMLs/doctor_api/logs/{request_id}.txt", "a").write(f"{e}\n")
        if not doctors:
            next_page = False
            break
        all_doctors.extend(doctors)
        start += 10

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
            details = "".join(doctor['location_nimvs'])
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

        location_data = matched_doctor.get('location_nimvs', '[{}]')
        location_data = json.loads(location_data[0])

        if matched_doctor.get('firstname', '') in business_name or matched_doctor.get('lastname', '') in business_name:

            final_result = dict()
            final_result['suffix'] = matched_doctor.get('suffix', '')
            final_result['firstName'] = matched_doctor.get('firstname', '')
            final_result['lastName'] = matched_doctor.get('lastname', '')
            final_result['fullName'] = matched_doctor.get('fullname', '')
            final_result['bio'] = matched_doctor.get('bio_s', '')
            final_result['address'] = location_data.get('address', '')
            final_result['city'] = location_data.get('city', '')
            final_result['state'] = location_data.get('state', '')
            final_result['postalCode'] = location_data.get('zipcode', '')
            final_result['profileurl'] = matched_doctor.get('providerurl', '')

            # open("matched_webMD.json", "w").write(json.dumps(doctors[best_match]))

            return {"response_meta": {"total_search_result": len(match_count_list), "total_pages": int(start/10)},
                    "matched_attribute": match_list[best_match],
                    "result": final_result}

    return {"response_meta": {"total_search_result": len(match_count_list), "total_pages": int(start/10)},
            "matched_attribute": list(), "result": {"error": "No Result Found"}}


def get_profile_data(url):
    final_response = dict()

    response = requests.get(url)
    json_data = json.loads("".join(re.findall(r"window\.__INITIAL_STATE__=(.*?);\(function", response.text)).strip())
    json_data = json_data['profile']
    final_response["profileUrl"] = url
    final_response["name"] = dict()
    final_response["name"]['fullName'] = json_data.get('fullname', '')
    final_response["name"]['suffix'] = json_data.get('suffix', '')
    final_response["name"]['firstName'] = json_data.get('firstname', '')
    final_response["name"]['middleName'] = json_data.get('middlename', '')
    final_response["name"]['lastName'] = json_data.get('lastname', '')
    final_response["jobTitle"] = json_data.get('jobtitledesc', '')
    final_response["professionType"] = "".join(json_data.get('professiontype_mvs', ''))
    final_response["specialtyNames"] = json_data.get('specialtynames', '')
    final_response["overview"] = json_data.get('bio_s', '')
    final_response["degree"] = json_data.get('degreeabbr', '')
    final_response["overallRating"] = json_data.get('c1_avg_f', '')
    final_response["reviewsCount"] = json_data.get('review_count_d', '')
    final_response["education"] = json_data.get('education', '')
    final_response["locations"] = list()
    final_response["reviews"] = list()
    reviews_count = json_data.get("review_count_d", '')
    entity_id = json_data.get('entityid', '')
    int_id = json_data.get('intid', '')

    for location in json_data['locations']:
        loc = dict()
        loc['practiceName'] = location.get('PracticeName', '')
        loc['locationName'] = location.get('LocationName', '')
        loc['locationPhone'] = location.get('formattedPhone', '')
        loc['address'] = location.get('address', '')
        loc['city'] = location.get('city', '')
        loc['state'] = location.get('state', '')
        loc['zipcode'] = location.get('zipcode', '')
        loc['geolocation'] = location.get('geolocation', '')
        loc['practiceWebsite'] = location.get('PracticeWebsite', '')
        loc['hours'] = location.get('formattedhours', '')
        final_response["locations"].append(loc)
    try:
        for review in json_data['reviews_mvs']:
            review_dict = dict()
            review_dict['rating'] = review['rating']
            review_dict['title'] = ''
            review_dict['user'] = review['user']
            review_dict['text'] = review['text']
            review_dict['date'] = review['date']
            final_response["reviews"].append(review_dict)
    except:
        pass

    if reviews_count:
        reviews_url = "https://www.webmd.com/search/2/api/lhd_v_profile_reviews"
        reviews_params = (
            ('entityid', entity_id),
            ('id', int_id),
            ('count', 1000),
        )
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
        reviews_response = requests.get(url=reviews_url, headers=headers, params=reviews_params)
        reviews_data = json.loads(reviews_response.content)
        for review in reviews_data['results']['ddcreviews']:
            review_dict = dict()
            review_dict['rating'] = review['overallrating_f']
            review_dict['title'] = review['headline_s']
            review_dict['user'] = ''
            review_dict['text'] = review['review_s']
            review_dict['date'] = review['added_at_dt']
            final_response["reviews"].append(review_dict)

    return {"result": final_response}
