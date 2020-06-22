import glob
import io
import os
from dataclasses import dataclass, field
from typing import List, Tuple

import requests
import wx  # type: ignore
from pubsub import pub  # type: ignore

from rpic import Wallhaven

WH = Wallhaven()


@dataclass
class ImagePanel(wx.Panel):

    parent: wx.Frame
    max_size: int = 300
    images: List[str] = field(default_factory=list)
    current_image: int = 0
    total_images: int = 0

    def __post_init__(self) -> None:
        """Class initializer"""
        super().__init__(self.parent)
        self.layout()

        pub.subscribe(self.update_image_via_pubsub, "update")

        self.slideshow_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_next, self.slideshow_timer)

    def get_image(self, url: str) -> None:
        """Retrieve the image from the given url

        Args:
            url (str): the hyperlink to the image
        """
        soup = WH.get(url)
        img_tag = soup.find("img", {"id": "wallpaper"})

        src = img_tag["src"]
        alt = img_tag["alt"]

        WH.download_image(WH.local_path, src)
        self.image_label.SetLabel("Image Saved!")
        WH.save(src)
        self.Layout()

    def layout(self) -> None:
        """Sets up the interface layout"""
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        img = wx.Image(self.max_size, self.max_size)
        self.image_ctrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img))

        self.main_sizer.Add(self.image_ctrl, 0, wx.ALL | wx.CENTER, 5)
        self.image_label = wx.StaticText(self, label="")
        self.main_sizer.Add(self.image_label, 0, wx.ALL | wx.CENTER, 5)

        btn_data = [
            ("Previous", btn_sizer, self.on_previous),
            ("Slide Show", btn_sizer, self.on_slideshow),
            ("Next", btn_sizer, self.on_next),
        ]
        for data in btn_data:
            label, sizer, handler = data
            self.btn_builder(label, sizer, handler)

        self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.SetSizer(self.main_sizer)

    def btn_builder(self, label, sizer, handler) -> None:
        """Button builder

        Args:
            label (str): The string for the button's label
            sizer (wx.BoxSizer): The WxPython sizer to use
            handler (wx.EVT_BUTTON): The button event to bind to the button
        """
        btn = wx.Button(self, label=label)
        btn.Bind(wx.EVT_BUTTON, handler)
        sizer.Add(btn, 0, wx.ALL | wx.CENTER, 5)

    def on_next(self, event: wx.EVT_BUTTON) -> None:
        """Displays a preview of the next image

        Args:
            event (wx.EVT_BUTTON): Next button click
        """
        if not self.images:
            return

        if self.current_image == self.total_images - 1:
            self.current_image = 0
        else:
            self.current_image += 1

        self.update_image(self.images[self.current_image])

    def on_previous(self, event: wx.EVT_BUTTON) -> None:
        """Displays a preview of the previous iamge

        Args:
            event (wx.EVT_BUTTON): Previous button click
        """
        if not self.images:
            return

        if self.current_image == 0:
            self.current_image = self.total_images - 1
        else:
            self.current_image -= 1

        self.update_image(self.images[self.current_image])

    def on_slideshow(self, event: wx.EVT_BUTTON) -> None:
        """Start a slideshow the the available images

        Args:
            event (wx.EVT_BUTTON): Start slideshow button
        """
        btn = event.GetEventObject()
        label = btn.GetLabel()
        if label == "Slide Show":
            self.slideshow_timer.Start(3000)
            btn.SetLabel("Stop")
        else:
            self.slideshow_timer.Stop()
            btn.SetLabel("Slide Show")

    def reset(self) -> None:
        """Reset the interface"""
        img = wx.Image(self.max_size, self.max_size)
        bmp = wx.Bitmap(img)
        self.image_ctrl.SetBitmap(bmp)
        self.current_image = 0
        self.images = []

    def update_image(self, url: str) -> None:
        """Update the current image being shown

        Args:
            url (str): They hyperlink location to the current image
        """
        thumbnail_url = "https://th.wallhaven.cc/small"
        image_id = url.rsplit("/", 1)[1]
        image_author_id = image_id[:2]
        th = f"{thumbnail_url}/{image_author_id}/{image_id}.jpg"
        content = requests.get(th).content
        io_bytes = io.BytesIO(content)
        img = wx.Image(io_bytes).ConvertToBitmap()

        self.image_ctrl.SetBitmap(wx.Bitmap(img))
        self.image_label.SetLabel("")
        self.Refresh()

    def update_image_via_pubsub(self, images):
        """Update the image attributes

        Args:
            images (list): List of image paths
        """
        self.images = images
        self.total_images = len(self.images)
        self.update_image(self.images[0])


@dataclass
class MainFrame(wx.Frame):
    def __post_init__(self) -> None:
        """Class initializer"""
        super().__init__(None, title="Wallpaper Viewer", size=(310, 310))
        self.panel = ImagePanel(self)
        self.create_toolbar()
        self.on_reload()
        self.Show()

    def create_toolbar(self):
        """Create a toolbar"""
        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((16, 16))

        reload_ico = wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_TOOLBAR, (16, 16))
        reload_tool = self.toolbar.AddTool(wx.ID_ANY, "open", reload_ico, "Reload")
        self.Bind(wx.EVT_MENU, self.on_reload, reload_tool)

        save_ico = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, (16, 16))
        save_tool = self.toolbar.AddTool(wx.ID_ANY, "save", save_ico, "Save Image")
        self.Bind(wx.EVT_MENU, self.on_save, save_tool)

        self.toolbar.Realize()

    def on_save(self, event):
        """On Save event handler

        Args:
            event (wx.EVT_BUTTON): Save button event handler
        """
        img = self.panel.images[self.panel.current_image]
        self.panel.get_image(img)

    def on_reload(self, event=None):
        """On Reload event handler

        Args:
            event (wx.EVT_BUTTON, optional): Reload event handler. Defaults to None.
        """
        images = WH.get_images()
        if images:
            pub.sendMessage("update", images=images)
        else:
            self.panel.reset()


if __name__ == "__main__":
    app = wx.App(redirect=False)
    frame = MainFrame()
    app.MainLoop()
