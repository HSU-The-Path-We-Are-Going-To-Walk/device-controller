import httpx
from config import DEVICE_IP, USERNAME, PASSWORD, TARGET_EMAIL

# 시스코 디바이스에서 Webex 화상통화 발신
def call_from_device():
    url = f"https://{DEVICE_IP}/putxml"
    headers = {"Content-Type": "text/xml"}
    payload = f"""
    <Command>
      <Dial>
        <Number>{TARGET_EMAIL}</Number>
      </Dial>
    </Command>
    """
    response = httpx.post(url, auth=(USERNAME, PASSWORD), data=payload, headers=headers, verify=False)
    print("시스코 디바이스에서 Webex 화상통화 발신:", response.status_code)