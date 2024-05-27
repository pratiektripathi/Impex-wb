import asyncio
import aiohttp
import os
from shutil import copyfile

class PicHandler:
    def __init__(self):
        self.default_image_path = os.path.join("res", "nocam.jpg")

    async def download_image(self, session, url, filename):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(filename, 'wb') as f:
                        f.write(await response.read())
                    
                else:
                    
                    self.save_default_image(filename)
        except Exception as e:
            self.save_default_image(filename)

    def save_default_image(self, filename):
        try:
            copyfile(self.default_image_path, filename)
            
        except Exception as e:
            pass

    async def download_images(self, url1, filename1, url2, filename2):
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.download_image(session, url1, filename1),
                self.download_image(session, url2, filename2)
            ]
            await asyncio.gather(*tasks)

# No main execution block; class is ready to be used in another script

    