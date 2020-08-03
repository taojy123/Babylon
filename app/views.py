import json
import time

import requests
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render

from app.models import Photo


def index(request):
    photos = Photo.objects.filter(hidden=False).order_by('-created_at')[:100]
    return render(request, 'index.html', locals())


def get_photo(request):
    url = request.GET['url']
    r = requests.get(url)
    return HttpResponse(r.content, content_type='image/jpeg')


def hide_photo(request):
    id = request.POST['id']
    Photo.objects.filter(id=id).update(hidden=True)
    return HttpResponse('ok')


def fetch(request):
    photo_url = 'https://h5.qzone.qq.com/proxy/domain/u.photo.qzone.qq.com/cgi-bin/upp/qun_floatview_photo'

    headers = {
        'authority': 'h5.qzone.qq.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,fr;q=0.6,ja;q=0.5',
        'cookie': 'pgv_pvid=4119152231; pac_uid=0_b2f3f50ac2ac4; pgv_pvi=5449911296; RK=JKARy9moP9; ptcz=a97f621dfc45ed8cf56506caf87868df243eaeddd24f6e04ca3f523a1d6ffc5d; XWINDEXGREY=0; OUTFOX_SEARCH_USER_ID_NCOO=1343975863.6363242; uin=o0067114208; skey=@XwAbhMek6; pgv_si=s615862272; p_uin=o0067114208; pt4_token=zm523lLvuxKczCzBaDiM1IjoJYsmDVWscfxSPIVNPw0_; p_skey=KuJ8N1nrSgQZOBljSRZFDsZ0MdYN*zezTxoFgfLkyzE_; pgv_info=ssid=s7002569576',
    }

    params = {
        'g_tk': '1618183471',
        'qzonetoken': 'cb30df74421b4ecc85fd991694779e08850ba201429cb55fff501a0fb1aee6100ff817142c73162ce95b050d9b692bf15bdbf1',
        'callback': 'viewer_Callback',
        't': '790087113',
        'topicId': '1107775508_V53i2qLf1VK29s0cNm8C1WDsOh1Y9vDP',
        'picKey': 'V5bCgAxMTA3Nzc1NTA42rgnX96IrSw!',
        'shootTime': '',
        'cmtOrder': '1',
        'fupdate': '1',
        'plat': 'qzone',
        'source': 'qzone',
        'cmtNum': '10',
        'likeNum': '5',
        'inCharset': 'utf-8',
        'outCharset': 'utf-8',
        'callbackFun': 'viewer',
        'offset': '1',
        'number': '20',
        'uin': '67114208',
        'hostUin': '67114208',
        'appid': '421',
        'isFirst': '',
        'sortOrder': '3',
        'showMode': '1',
        'prevNum': '0',
        'postNum': '20',
        '_': '1596462612556',
    }

    photo = Photo.objects.order_by('-created_at').first()
    if photo:
        pkey = photo.key
    else:
        pkey = 'V5bCgAxMTA3Nzc1NTA42rgnX96IrSw!'

    count = 0
    for i in range(10):
        print(pkey)
        params['picKey'] = pkey
        r = requests.get(photo_url, headers=headers, params=params)

        res = r.text
        res = res.replace('viewer_Callback(', '')[:-2]
        # print(res)
        res = json.loads(res)

        data = res['data']
        if 'photos' not in data:
            break

        photos = data['photos']
        print(len(photos))

        for p in photos:
            url = p['url'].split('?')[0]
            pkey = p['picKey']
            print(url)
            photo, created = Photo.objects.get_or_create(url=url)
            if created:
                count += 1

        time.sleep(1)

    return HttpResponse(count)

