"""
Input:  { "s3_key": "ThanosBlinkit.jpeg", "words_to_find": "THOR,HULK,..." }

Environment variable required:
  S3_BUCKET_NAME = your-s3-bucket-name
"""

import json, base64, os
import boto3

s3      = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime")

S3_BUCKET    = os.environ.get("S3_BUCKET_NAME", "word-search-puzzles")
OCR_MODEL    = "amazon.nova-pro-v1:0"
DEFAULT_WORDS = (
)


def get_media_type(key):
    k = key.lower()
    if k.endswith(".png"):  return "png"
    if k.endswith(".gif"):  return "gif"
    if k.endswith(".webp"): return "webp"
    return "jpeg"


def lambda_handler(event, context):
    print("EVENT:", json.dumps(event, default=str))

    # Bedrock Flows Lambda nodes send inputs in event["node"]["inputs"] list
    node_inputs = {inp["name"]: inp.get("value", "")
                   for inp in event.get("node", {}).get("inputs", [])}

    # Get the raw value (Bedrock passes the full JSON string as the value)
    raw = (node_inputs.get("s3_key") or
           event.get("s3_key") or
           event.get("document") or "")

    # Parse the JSON string to extract individual fields
    if isinstance(raw, str) and raw.strip().startswith("{"):
        try:
            data = json.loads(raw)
        except Exception:
            data = event
    else:
        data = event

    s3_key        = data.get("s3_key", "").strip()
    words_to_find = data.get("words_to_find", DEFAULT_WORDS).strip()

    if not s3_key:
        return "ERROR: s3_key is required."

    mtype = get_media_type(s3_key)

    try:
        body = {
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": mtype,
                            "source": {
                                "s3Location": {
                                    "uri": f"s3://{S3_BUCKET}/{s3_key}"
                                }
                            }
                        }
                    },
                    {"text": (
                    )}
                ]
            }],
            "inferenceConfig": {"maxTokens": 4096, "temperature": 0.0}
        }
        resp     = bedrock.invoke_model(modelId=OCR_MODEL, body=json.dumps(body),
                                        contentType="application/json", accept="application/json")
        ocr_text = json.loads(resp["body"].read())["output"]["message"]["content"][0]["text"]
        print("OCR_TEXT_LEN:", len(ocr_text))
        print("OCR_ROWS_COUNT:", ocr_text.count("ROW"))
        print("OCR_TEXT_SAMPLE:", ocr_text[:300])
    except Exception as e:
        return f"ERROR: OCR failed: {e}"

    import re as _re
    row_matches = _re.findall(r'ROW\d+:\s*([A-Z ]+)', ocr_text.upper())
    if row_matches:
        grid_rows = [r.strip() for r in row_matches if r.strip()]
    elif "|" in ocr_text:
        grid_rows = [r.strip() for r in ocr_text.split("|") if r.strip()]
    else:
        grid_rows = [r.strip() for r in ocr_text.split("\n") if r.strip()]
    print("GRID_ROWS_COUNT:", len(grid_rows))
    grid_pipe = " | ".join(grid_rows)
    return (
        f"WORDS:{words_to_find}\n"
        f"GRID:{grid_pipe}"
    )
