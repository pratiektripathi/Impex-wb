import asyncio
import aiohttp
import os
from shutil import copyfile

class PicHandler:
    def __init__(self):
        self.default_image_path = os.path.join("res", "nocam.jpg")
        self.timeout = aiohttp.ClientTimeout(total=10)  # Timeout after 10 seconds

    async def download_image(self, session, url, filename):
        try:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    with open(filename, 'wb') as f:
                        f.write(await response.read())
                else:
                    self.save_default_image(filename)
        except Exception:
            self.save_default_image(filename)

    def save_default_image(self, filename):
        try:
            copyfile(self.default_image_path, filename)
        except Exception:
            pass

    async def download_images(self, url1, filename1, url2, filename2):
        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.create_task(self.download_image(session, url1, filename1)),
                asyncio.create_task(self.download_image(session, url2, filename2))
            ]
            # Use asyncio.wait to return as soon as the first task is done
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            
            # Cancel pending tasks if any
            for task in pending:
                task.cancel()

            # Reraise exceptions, if any
            for task in done:
                if task.exception():
                    raise task.exception()
