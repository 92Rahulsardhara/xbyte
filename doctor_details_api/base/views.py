import datetime
import hashlib
import json

import pymongo
import pytz
from django.db.models import F
from django.http import JsonResponse
from django.urls import resolve

from base import vitals
from base import webmd_data
from base.models import TrackingInfo, KeyTable

# client = pymongo.MongoClient('mongodb://deep.b:Deep%40123@51.161.13.140:27017/?authSource=admin')
# db = client["xbyte_doctor_details_api"]
# collection = db["api_tracking_info"]


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def doctor_search(request):
    requests_url = request.get_raw_uri()
    request_time = datetime.datetime.now(tz=pytz.utc)
    request_ip = get_client_ip(request)
    request_id = hashlib.md5(bytes(requests_url + str(request_time), "utf8")).hexdigest()

    response = dict()
    response['request_log'] = dict()
    response['request_log']['requests_url'] = requests_url
    response['request_log']['request_time'] = str(request_time)
    response['request_log']['request_id'] = request_id

    endpoint_name = resolve(request.path_info).url_name

    is_authorised = False
    api_key_table = None

    key = request.GET.get('x-api-key')
    if not key:
        key = request.POST.get('x-api-key')

    if key:
        if KeyTable.objects.filter(api_key=key).exists():
            is_authorised = True
            # api_key_table = KeyTable.objects.get(api_key=key)
            # if api_key_table.usage_limit >= api_key_table.total_usage:
            #     is_authorised = True
            # else:
            #     response.update(msg=f"API-KEY({key}) limit exceeded ...")
        else:
            response.update(msg=f"API-KEY({key}) is wrong. Request received from IP address {request_ip}")
    else:
        response.update(msg=f"Missing API-KEY, Request received from IP address {request_ip}")

    status = 401
    if is_authorised:
        try:
            business_name = request.GET.get('business_name', '')
            city = request.GET.get('city', '')
            zip_code = request.GET.get('zip_code', '')
            phone = request.GET.get('phone', '')

            errors = dict(missing_params=list(), errors=list())

            if not business_name:
                missing_param = dict(param="", msg="")
                missing_param['msg'] = "business_name not found in request ... "
                missing_param['param'] = "business_name"
                errors['missing_params'].append(missing_param)

            if not zip_code:
                missing_param = dict(param="", msg="")
                missing_param['msg'] = "zip_code not found in request ... "
                missing_param['param'] = "zip_code"
                errors['missing_params'].append(missing_param)

            if not errors['missing_params'] and not errors['errors']:
                if "Vitals" in endpoint_name:
                    response.update(
                        vitals.search_doctor(business_name=business_name, city=city, zip_code=zip_code, phone=phone)
                    )
                else:
                    response.update(
                        webmd_data.search_doctor(business_name=business_name, city=city, zip_code=zip_code, phone=phone, request_id=request_id)
                    )
                status = 200
            else:
                status = 400
                response['errors'] = errors
        except Exception as e:
            print(e)
            status = 500
            response['msg'] = "Request blocked by the target Website... \nplease try again later..."
            open(f"C:/HTMLs/doctor_api/logs/{request_id}.txt", "a").write(f"{e}\n")

    response_time = datetime.datetime.now(tz=pytz.utc)
    track = TrackingInfo()
    track.request_received_time = request_time
    track.api_key = api_key_table
    track.request_url = requests_url
    track.response_code = status
    track.request_sent_time = response_time
    track.response_json = json.dumps(response, default=str)
    track.request_id = request_id
    track.request_ip = request_ip
    track.endpoint_name = endpoint_name
    track.save()

    # if status == 200:
    #     try:
    #         api_key_table.total_usage = F('total_usage') + 1
    #         api_key_table.save()
    #     except Exception as e:
    #         print(e)

    # try:
    #     mongo_insert = response.copy()
    #     mongo_insert['request_log']['x-api-key'] = key
    #     collection.insert_one(mongo_insert)
    # except:
    #     pass

    response['request_log']['response_time'] = str(response_time)
    response['request_log']['request_process_time'] = str(response_time - request_time)
    return JsonResponse(response, status=status)


def profile_data(request):
    requests_url = request.get_raw_uri()
    request_time = datetime.datetime.now(tz=pytz.utc)
    request_id = hashlib.md5(bytes(requests_url + str(request_time), "utf8")).hexdigest()
    request_ip = get_client_ip(request)

    response = dict()
    response['request_log'] = dict()
    response['request_log']['requests_url'] = requests_url
    response['request_log']['request_time'] = str(request_time)
    response['request_log']['request_id'] = request_id
    response['request_log']['request_ip'] = request_ip

    endpoint_name = resolve(request.path_info).url_name

    is_authorised = False
    api_key_table = None

    key = request.GET.get('x-api-key')
    if not key:
        key = request.POST.get('x-api-key')

    if key:
        if KeyTable.objects.filter(api_key=key).exists():
            api_key_table = KeyTable.objects.get(api_key=key)
            if api_key_table.usage_limit >= api_key_table.total_usage:
                is_authorised = True
            else:
                response.update(msg=f"API-KEY({key}) limit exceeded ...")
        else:
            response.update(msg=f"API-KEY({key}) is wrong. Request received from IP address {request_ip}")
    else:
        response.update(msg=f"Missing API-KEY, Request received from IP address {request_ip}")

    status = 401
    if is_authorised:
        try:
            url = request.GET.get('url', '')

            errors = dict(missing_params=list(), errors=list())

            if not url:
                missing_param = dict(param="", msg="")
                missing_param['msg'] = "url not found in request ... "
                missing_param['param'] = "url"
                errors['missing_params'].append(missing_param)

            if not errors['missing_params'] and not errors['errors']:
                if "Vitals" in endpoint_name:
                    response.update(
                        vitals.get_profile_data(url=url)
                    )
                else:
                    response.update(
                        webmd_data.get_profile_data(url=url)
                    )
                status = 200
            else:
                status = 400
                response['errors'] = errors
        except Exception as e:
            print(e)
            status = 500
            response['msg'] = "Request blocked by the target Website... \nplease try again later..."
            open(f"C:/HTMLs/doctor_api/logs/{request_id}.txt", "a").write(f"{e}\n")

    response_time = datetime.datetime.now(tz=pytz.utc)
    track = TrackingInfo()
    track.api_key = api_key_table
    track.request_received_time = request_time
    track.request_url = requests_url
    track.response_code = status
    track.request_sent_time = response_time
    track.response_json = json.dumps(response, default=str)
    track.request_id = request_id
    track.request_ip = request_ip
    track.endpoint_name = endpoint_name
    track.save()

    # if status == 200:
    #     try:
    #         api_key_table.total_usage = F('total_usage') + 1
    #         api_key_table.save()
    #     except Exception as e:
    #         print(e)

    # try:
    #     mongo_insert = response.copy()
    #     mongo_insert['request_log']['x-api-key'] = key
    #     collection.insert_one(mongo_insert)
    # except:
    #     pass

    response['request_log']['response_time'] = str(response_time)
    response['request_log']['request_process_time'] = str(response_time - request_time)
    return JsonResponse(response, status=status)
