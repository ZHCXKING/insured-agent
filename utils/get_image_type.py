# %%
import base64
import io
import re
from PIL import Image
# %%
def get_image_type(base64_str):
    clean_b64 = "".join(base64_str.split())
    img_bytes = base64.b64decode(clean_b64)
    img_io = io.BytesIO(img_bytes)
    with Image.open(img_io) as img:
         return Image.MIME.get(img.format), clean_b64