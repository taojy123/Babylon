import requests
from django.db import models
from django.core.files.base import ContentFile
from django.utils.html import format_html


class Photo(models.Model):
    # https://h5.qzone.qq.com/groupphoto/index?inqq=3&groupId=1107775508&type=102&uri=share
    # http://qungz.photo.store.qq.com/qun-qungz/V53i2qLf1VK29s0cNm8C1WDsOh1Y9vDP/V5bCgAxMTA3Nzc1NTA4OZYnX5bYnwY!/800
    url = models.CharField(max_length=250, blank=True, unique=True)
    hidden = models.BooleanField(default=False)
    pic = models.FileField(upload_to='babylon', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.key

    @property
    def target_url(self):
        if self.pic:
            return self.pic.url
        url = '/get_photo/?url=' + self.url
        return url

    @property
    def brick_url(self):
        if self.pic:
            return self.pic.url + '?imageView2/2/w/200'
        url = self.url[:-4] + '/200'
        url = '/get_photo/?url=' + url
        return url

    @property
    def key(self):
        return self.url.split('/')[-2]

    @property
    def brick_tag(self):
        return format_html('<img src="%s" height="100" />' % self.brick_url)

    def save_pic(self, force=False):
        if not force and self.pic:
            print('pic exists skip')
            return
        r = requests.get(self.url)
        f = ContentFile(r.content, name='%d.jpg' % self.id)
        print(f)
        self.pic = f
        self.save()


class Cache(models.Model):
    cookie = models.TextField(blank=True)
    tk = models.TextField(blank=True)


