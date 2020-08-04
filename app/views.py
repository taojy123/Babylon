import json
import time

import requests
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render

from app.models import Photo, Cache


def index(request):
    after = request.GET.get('after')
    photos = Photo.objects.filter(hidden=False).order_by('-id')
    if after:
        photos = photos.filter(id__lt=after)

    next_url = ''
    if photos.count() > 50:
        photos = photos[:50]
        next_url = '/?after=%d' % photos[49].id

    return render(request, 'index.html', locals())


def detail(request, pid):
    photo = Photo.objects.get(id=pid)
    prev_photo = Photo.objects.filter(id__gt=pid).order_by('id').first()
    next_photo = Photo.objects.filter(id__lt=pid).order_by('-id').first()
    back_url = '/?after=%d' % (photo.id + 3)
    return render(request, 'detail.html', locals())


def get_photo(request):
    url = request.GET['url']
    r = requests.get(url)
    return HttpResponse(r.content, content_type='image/jpeg')


def hide_photo(request):
    id = request.POST['id']
    Photo.objects.filter(id=id).update(hidden=True)
    return HttpResponse('ok')


def fetch(request):
    if request.method == 'POST':

        albums = (
            # topicId, picKey, t
            ('1107775508_V53i2qLf1VK29s0cNm8C1WDsOh1Y9vDP', 'V5bCgAxMTA3Nzc1NTA42rgnX96IrSw!', '790087113'),
            ('1107775508_V53i2qLf1VK29s0cNm8C1WDsOh02eG8n', 'V5bCgAxMTA3Nzc1NTA4AOkoX2w7JDA!', '228205055'),
        )

        cache, _ = Cache.objects.get_or_create()
        cookie = request.POST.get('cookie') or cache.cookie
        tk = request.POST.get('tk') or cache.tk

        cache.cookie = cookie
        cache.tk = tk
        cache.save()

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
            'qzonetoken': '',
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
            'offset': '0',
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

        if cookie:
            headers['cookie'] = cookie
        if tk:
            params['g_tk'] = tk

        count = 0

        for topicId, picKey, t in albums:

            last_len = 99
            for i in range(30):
                print(topicId, picKey)
                params['topicId'] = topicId
                params['picKey'] = picKey
                params['t'] = t

                r = requests.get(photo_url, headers=headers, params=params)
                # print(r.text)
                res = r.text.replace('viewer_Callback(', '')[:-2]

                try:
                    res = json.loads(res)
                except Exception as e:
                    return HttpResponse(str(r) + r.text)

                data = res['data']

                if 'photos' not in data:
                    print(r, r.text)
                    return HttpResponse(str(r) + r.text)

                photos = data['photos']
                print(len(photos))

                if len(photos) <= 1 and last_len <= 1:
                    print('empty')
                    break

                last_len = len(photos)

                for p in photos:
                    url = p['url'].split('?')[0]
                    picKey = p['picKey']
                    print(url)
                    photo, created = Photo.objects.get_or_create(url=url)
                    if created:
                        print('new')
                        photo.save_pic()
                        count += 1

                time.sleep(0.5)

        return HttpResponse(count)

    return render(request, 'fetch.html')

