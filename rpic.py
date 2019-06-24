#!/usr/bin/env /home/mohh/anaconda3/bin/python
"""Downloads a random image from wallhaven.cc"""
from os import mkdir, path
from shutil import copyfile

import requests
from bs4 import BeautifulSoup


class Wallhaven:
    """Wallhaven image object

    Set the purity filter setting
        SFW             = 100
        Sketchy         = 010
        Both            = 110

    Set the category
        General         = 100
        Manga/Anime     = 010
        People          = 001

        NOTE: Can combine them
    """

    def __init__(self, purity=100, categories=111, sorting="random", order="desc"):
        self.purity = purity
        self.categories = categories
        self.sorting = sorting
        self.order = order
        self.site = "wallhaven.cc"
        self.img_path = "//wallpapers.wallhaven.cc/wallpapers/full/"
        self.img = "wallpaper.jpg"
        self.walls = "wallpaper"
        self.home = path.expanduser("~")
        self.img_folder = path.join(self.home, "Pictures")
        self.local_path = path.join(self.img_folder, self.img)
        self.wallpapers = path.join(self.img_folder, self.walls)
        self.check_dir(self.img_folder)
        self.url = self.construct_url
        self.images = self.get_images()
        self.current = 0

    @staticmethod
    def check_dir(folder):
        """
        Verifies directory structure

        Checks to see if a certain directory exist and creates it if it doesn't
        """
        if not path.exists(folder):
            mkdir(folder)

    @property
    def construct_url(self):
        """
        Constructs a proper url

        With the properties that were set for the object
        """
        url = (
            f"https://{self.site}/search?"
            f"categories={self.categories}&"
            f"purity={self.purity}&sorting="
            f"{self.sorting}&order={self.order}"
        )
        return url

    @staticmethod
    def download_image(image_loc, url):
        """
        Downloads the image

        Retrieves the image and saves it to the path provided
        """
        with open(image_loc, "wb") as image:
            response = requests.get(url, stream=True)

            if not response.ok:
                print(response)

            for block in response.iter_content(1024):
                if not block:
                    break

                image.write(block)

    @staticmethod
    def get(url):
        """
        Retrieves the webpage

        And creates a BeautifulSoup object from it
        """
        try:
            response = requests.get(url)
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            return soup
        except requests.exceptions.ConnectionError:
            print("Not able to establish a connection with the server.")
            exit(1)

    def get_images(self):
        """
        Extract image urls

        From the soup object and creates a list of them
        """
        imgs = []
        soup = self.get(self.url)
        previews = soup.find_all("a", class_="preview")

        for link in previews:
            imgs.append(link["href"])

        return imgs

    def next(self):
        """
        Retrieves the next image

        Parses the full image url from the image page and downloads it
        """
        if self.current <= len(self.images) - 1:
            soup = self.get(self.images[self.current])
            img_tag = soup.find("img", {"id": "wallpaper"})

            src = img_tag["src"]
            alt = img_tag["alt"]

            self.download_image(self.local_path, src)
            print(f"Retrieved: {alt}")

            save = input("Backup the image (y/[n])? ")
            if "y" in save.lower():
                img_name = src.split("/")[-1]
                wallpaper = path.join(self.wallpapers, img_name)
                copyfile(self.local_path, wallpaper)

            self.current += 1

        else:
            # at the end of the list of images, get a new batch
            self.current = 0
            self.images = self.get_images()
            self.next()


def main():
    """
    Main entry point to the program
    """
    keepem_coming = True

    haven = Wallhaven()
    haven.next()

    while keepem_coming:
        answer = input("Would you like a different image([y]/n)? ")
        if "n" in answer.lower():
            keepem_coming = False
        else:
            haven.next()


if __name__ == "__main__":
    main()
