"""Downloads a random image from wallhaven.cc"""
import requests

from os import path, mkdir, system
from shutil import copyfile

from bs4 import BeautifulSoup


class Wallhaven(object):
    """Wallhaven image object

    Set the purity filter setting
        SFW			    = 100
        Sketchy			= 010
        Both			= 110

    Set the category
        General		    = 100
        Manga/Anime	    = 010
        People          = 001

        NOTE: Can combine them
    """
    SITE = 'wallhaven.cc'
    IMG = 'wallpaper.jpg'
    WALLS = 'wallpaper'
    HOME = path.expanduser('~')
    IMG_FOLDER = path.join(HOME, 'Pictures')
    IMG_PATH = path.join(IMG_FOLDER, IMG)
    WALLPAPERS = path.join(IMG_FOLDER, WALLS)

    def __init__(self, purity=100, categories=111, sorting='random', order='desc'):
        self.purity = purity
        self.categories = categories
        self.sorting = sorting
        self.order = order
        self.url = self.construct_url
        self.img_path = '//wallpapers.wallhaven.cc/wallpapers/full/'
        self.images = self.get_images()
        self.current = 0
        self.check_dir(self.IMG_FOLDER)

    @staticmethod
    def check_dir(folder):
        """Checks to see if a certain directory exist and creates it if it doesn't"""
        if not path.exists(folder):
            mkdir(folder)

    @property
    def construct_url(self):
        """Takes the properties that were set for the object and constructs a proper url with them"""
        url = f'https://alpha.{self.SITE}/search?categories={self.categories}&purity={self.purity}&sorting=' \
              f'{self.sorting}&order={self.order}'
        return url

    @staticmethod
    def get(url):
        """Retrieves the webpage and creates a BeautifulSoup object from it"""
        r = requests.get(url)
        html = r.text

        soup = BeautifulSoup(html, 'html.parser')
        return soup

    def get_images(self):
        """Extract the image urls from the soup object and creates a list of them"""
        imgs = []
        soup = self.get(self.url)
        previews = soup.find_all('a', class_='preview')

        for link in previews:
            imgs.append(link['href'])
        return imgs

    def next(self):
        """Parses the full image url from the image page and downloads it"""
        if self.current <= len(self.images) - 1:
            soup = self.get(self.images[self.current])
            img_tags = soup.find_all('img')

            for img in img_tags:
                if self.img_path in img['src']:
                    src = 'https:' + img['src']
                    alt = img['alt']

                    # TODO: Figure out a pythonic way of downloading the image
                    cmd = f'curl -s -o {self.IMG_PATH} {src}'
                    system(cmd)

                    print(f'Retrieved: {alt}')
                    save = input('Would you like to backup the image (y/n)? ')
                    if 'y' in save.lower():
                        img_name = src.split('/')[-1]
                        wallpaper = path.join(self.WALLPAPERS, img_name)
                        copyfile(self.IMG_PATH, wallpaper)

                    self.current += 1

        else:
            # at the end of the list of images, get a new batch
            self.current = 0
            self.images = self.get_images()
            self.next()


def main():
    """Main entry point to the program"""
    keepem_coming = True

    haven = Wallhaven()
    haven.next()

    while keepem_coming:
        answer = input('Would you like a different image(y/n)? ')
        if 'y' in answer.lower():
            haven.next()
        else:
            keepem_coming = False


if __name__ == '__main__':
    main()
