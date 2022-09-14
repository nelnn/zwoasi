import requests

def upload_image(upload_url:str, auth_token_key:str, location_name: str, image_path: str):
    try:
        # Disable 'requests' warnings
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        # Request to upload image
        with open(image_path, "rb") as image_file:
            response = requests.post(upload_url, headers={'Authorization': 'Bearer ' + auth_token_key}, data={"location": location_name}, files={"image": image_file}, timeout=5, verify=False)
        # Response status from server
        if response.status_code == 200:
            print("[File upload] Uploaded Successful")
        elif response.status_code == 401:
            print("[File upload] Unauthorized, please check the auth_token_key")
        else:
            print("[File upload] Failed")
      
    except requests.Timeout:
        print("[File Upload] Timeout")
    except requests.ConnectionError:
        print("[File Upload] Connection Error")
    except Exception as e:
        print("[File Upload] Unknown Error", e)
