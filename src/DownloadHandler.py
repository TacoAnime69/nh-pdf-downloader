from re import findall, sub
from PIL import Image
from lxml import html
from sys import platform
from zipfile import ZipFile
from collections import defaultdict
import requests, os, shutil, datetime, threading

class DownloadHandler:
    def __init__(self, id_num, file_type: str):
        self.id_num = id_num
        self.file_type = file_type
        page = requests.get(f'https://nhentai.net/g/{self.id_num}/')
        tree = html.fromstring(page.content)
        try:
            # If the page doesn't exist, the following will throw an error
            title = str(tree.xpath('//div[@id="info"]/h1/span[@class="pretty"]/text()')[0])
            try:
                title += str(tree.xpath('//div[@id="info"]/h1/span[@class="after"]/text()')[0])
            except:
                pass
            self._title = title
            self._pages = int(
                len(tree.xpath('//div[@class="thumb-container"]')))
            self._valid = True
            # self._valid = False # DEBUG ONLY
        except:
            self._valid = False
        return

    def save_image(self, at_page, destination):
        curr_page = f"https://nhentai.net/g/{self.id_num}/{at_page}/"
        page = requests.get(curr_page)
        tree = html.fromstring(page.content)
        img_link = tree.xpath('//section[@id="image-container"]/a/img/@src')
        # Save image to temp folder
        img_file = os.path.join(destination, f"{at_page}.png")
        temp_img = open(img_file, 'wb')
        temp_img.write(requests.get(img_link[0]).content)
        temp_img.close()
        if self.file_type != 'pdf':  # If the Doujin is to be saved as a CBx file
            Image.open(img_file).save(os.path.join(destination, f"{at_page}.png"))
            img_file = f"{at_page}.png"
        return img_file

    @property
    def title(self):
        return self._title

    @property
    def valid(self):
        return self._valid

    @property
    def pages(self):
        return self._pages
