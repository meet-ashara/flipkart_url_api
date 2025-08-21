import re
import json

def extract_json_data(html_text: str):
    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});\s*</script>', html_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            return {}
    return {}

def get(data, keys):
    try:
        for key in keys:
            data = data[key]
        return data
    except:
        return 'N/A'
