import httpx
import asyncio
import os
from shutil import copyfile


class PicHandler:
    def __init__(self):
        self.default_image_path = os.path.join("res", "nocam.jpg")
        self.timeout = 10  # Timeout after 10 seconds

    async def download_image(self, client, ip, username, password, filename):
        try:
            url = f"http://{ip}/cgi-bin/snapshot.cgi?channel=1"
            auth = httpx.DigestAuth(username, password)  # Digest Authentication
            response = await client.get(url, auth=auth, timeout=self.timeout)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
            else:
                self.save_default_image(filename)
        except Exception:
            self.save_default_image(filename)

    def save_default_image(self, filename):
        try:
            copyfile(self.default_image_path, filename)
        except Exception:
            pass

    async def download_images(self, ip1, username1, password1, filename1, ip2, username2, password2, filename2):
        async with httpx.AsyncClient() as client:
            tasks = [
                asyncio.create_task(self.download_image(client, ip1, username1, password1, filename1)),
                asyncio.create_task(self.download_image(client, ip2, username2, password2, filename2))
            ]
            # Wait for tasks and handle exceptions
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            
            # Cancel pending tasks if any
            for task in pending:
                task.cancel()

            # Reraise exceptions, if any
            for task in done:
                if task.exception():
                    raise task.exception()



