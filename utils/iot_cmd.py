from config import iot_project_id, iot_device_id, iot_api_host
from utils import hw
import json
import requests
import base64
import logging
logger = logging.getLogger(__name__)


def _send_hw_cmd_(service_id, command_name, paras):
    logger.info(f'Send command: <{service_id}-{command_name}>')
    url = f'https://{iot_api_host}/v5/iot/{iot_project_id}/devices/{iot_device_id}/commands'
    header = {
        'X-Auth-Token': hw.get_token()
    }
    data = {
        "service_id": service_id,
        "command_name": command_name,
        "paras": paras
    }
    response = requests.post(url=url, headers=header, data=json.dumps(data))

    if command_name == 'CAPTURE':
        response = json.loads(response.content.decode('utf-8'))
        logger.debug(response)

        response_paras = response['response']['paras']
        with open('tmp.jpeg', 'wb') as f:
            img_bytes = base64.b64decode(response_paras['pic'])
            f.write(img_bytes + b'\xff\xd9')
            logger.info('Save img to tmp.jpeg')


def _get_hw_shadow_prop_(service_id) -> dict:
    """
    format:
    {
      "event_time": "20220710T130738Z",
      "properties": {
        "value": <float>,
        ...
      }
    }
    """
    logger.info(f'Query properties: {service_id}')
    url = f"https://{iot_api_host}/v5/iot/{iot_project_id}/devices/{iot_device_id}/shadow"
    header = {'X-Auth-Token': hw.get_token()}
    params = {'service_id': service_id}
    response = requests.get(url=url, headers=header, params=params)
    response = response.content.decode('utf-8')
    response = json.loads(response)
    for shadow in response['shadow']:
        if shadow['service_id'] == service_id:
            response = shadow['reported']
            break
    return response


def power_on(device_id, oid):
    _send_hw_cmd_("Pile", "POWER", {"ID": device_id, "ON": 1, "ORDER": oid})


def power_on_delay(device_id, oid, timeout):
    _send_hw_cmd_("Pile", "POWER_DELAY", {"ID": device_id, "ON": 1, "ORDER": oid, "TIMEOUT": timeout})


def power_off(device_id, oid):
    _send_hw_cmd_("Pile", "POWER", {"ID": device_id, "ON": 0, "ORDER": oid})


def lock_open(device_id):
    _send_hw_cmd_("Pile", "LOCK_OPEN", {"ID": device_id})


def book(device_id):
    _send_hw_cmd_("Pile", "BOOK", {"ID": device_id})


def video_on():
    _send_hw_cmd_("Monitor", "CAM", {})


def detect_wheel() -> bytes:
    return _send_hw_cmd_("Monitor", "CAPTURE", {})


def get_energy() -> dict:
    return _get_hw_shadow_prop_("Energy")
