from urllib import response
from simple_image_download import simple_image_download as simple

response = simple.simple_image_download

keywords = ['AH-64 Apache', 'A380', 'KT-1']

for keyword in keywords:
    response().download(keyword, 100)