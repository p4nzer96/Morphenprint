import os
import sys
import base64
import json
import requests


def get_verifinger_minutiae(img_path):
    """ Get the minutiae from Verifinger.
    :param img_path: Path to the image.
    :return: The minutiae.
    """
    with open(img_path, "rb") as f:
        im_bytes = f.read()  

    img_base64 = base64.b64encode(im_bytes).decode("utf8")

    # create the request data
    data = {
        'image': img_base64
    }
    data = json.dumps(data)

    # send the request
    url = "http://141.44.30.186:5001/api/verifinger/minutiae"
    headers = {'Content-Type': 'application/json'}
    
    try:
        # get the response
        r = requests.post(url, data=json.dumps(data), headers=headers)
        print(r)

        # parse the response
        result = r.json()
        print(result)
    except:
        print("Couldn't execute the fingerprints: " + img_path)


def main():
    if (len(sys.argv) < 2):
        print('Usage: python '+sys.argv[0]+ ' <img_path>')
        print('\img_path: This is the path to the image.')
        sys.exit(0)
    
    # parse command line parameters
    img_path = sys.argv[1]

    get_verifinger_minutiae(img_path)


if __name__ == '__main__':
    main()