from apiclient.discovery import build
import urllib.request
import numpy as np
from PIL import Image


def Google_Image_Get(query, i, Directory, safe_search):
    with open('GoogleDeveloperkey.txt', 'r') as f:
        k = f.read()
    with open('GoogleSearchEngineID.txt', 'r') as f:
        cx = f.read()
    service = build("customsearch", "v1",
                    developerKey=k)
    safe = 'active' if safe_search else 'off'
    res = service.cse().list(
        q=query,
        cx=cx,
        searchType='image',
        num='1',
        start=str(i),
        # imgColorType='gray',
        safe=safe
    ).execute()
    # Download the file from `url` and save it locally under `file_name`:
    try:
        urllib.request.urlretrieve(res['items'][0]['link'], '{0}/{1}.png'.format(Directory, query))
        return True
    except urllib.error.HTTPError:
        return False


def Image_Transform(imagepath, threshold):
    img = Image.open(imagepath)  # open colour image
    width, height = img.size
    # if height > width:
    #     img = img.transpose(Image.ROTATE_270)
    if width > 500:
        reshapefactor = 500 / width
        new_width = int(width * reshapefactor)
        new_height = int(height * reshapefactor)
        if new_height > 300:
            reshapefactor2 = 300 / new_height
            new_height = int(new_height * reshapefactor2)
            new_width = int(new_width * reshapefactor2)
        img = img.resize((new_width, new_height), Image.ANTIALIAS)
    img_array = np.array(img)
    img_array[np.where(img_array > threshold)] = 255
    image = Image.fromarray(np.uint8(img_array))
    image = image.convert('1')
    image.save(imagepath + '.mono.png')
