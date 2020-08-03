import requests
from django.db import models


class Photo(models.Model):
    # http://qungz.photo.store.qq.com/qun-qungz/V53i2qLf1VK29s0cNm8C1WDsOh1Y9vDP/V5bCgAxMTA3Nzc1NTA4OZYnX5bYnwY!/800
    url = models.CharField(max_length=100, blank=True, unique=True)
    hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def target_url(self):
        url = '/get_photo/?url=' + self.url
        return url

    @property
    def brick_url(self):
        assert self.url[-4:] == '/800', self.url
        url = self.url[:-4] + '/200'
        url = '/get_photo/?url=' + url
        return url

    @property
    def key(self):
        return self.url.split('/')[-2]