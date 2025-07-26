import boto3

class ObjectAlreadyExistsException(Exception):
    pass

def check_object_exists(client, bucket, key):
    output = client.list_objects_v2(Bucket=bucket, Prefix=key)
    if 'Contents' in output:
        for obj in output['Contents']:
            if obj['Key'] == key:
                return True
    return False

def on_create(client, event):
    props = event["resource_properties"]
    bucket, key, body = props["bucket"], props["key"], props["body"]
    if check_object_exists(client, bucket, key):
        raise Exception(f"Object {key} already exists in bucket {bucket}.")
    client.put_object(Bucket=bucket, Key=key, Body=body)
    return

def on_update(client, event):
    event_prev = event["tf"]["prev_input"]
    try:
        props = event["resource_properties"]
        props_prev = event_prev["resource_properties"]
        bucket, key, body = props["bucket"], props["key"], props["body"]
        bucket_prev, key_prev, body_prev = props_prev["bucket"], props_prev["key"], props_prev["body"]
        physical_id_updated = f"{bucket}/{key}"
        physical_id_prev = f"{bucket_prev}/{key_prev}"
        if physical_id_updated != physical_id_prev and check_object_exists(client, bucket, key):
            raise ObjectAlreadyExistsException(f"Object {key} already exists in bucket {bucket}.")
        client.put_object(Bucket=bucket, Key=key, Body=body)
        if physical_id_updated != physical_id_prev:
            client.delete_object(Bucket=bucket_prev, Key=key_prev)
    except ObjectAlreadyExistsException as e:
        print(e)
        raise e
    except Exception as e:
        print(e)
        if physical_id_updated != physical_id_prev:
            client.put_object(Bucket=bucket_prev, Key=key_prev, Body=body_prev)
        raise e
    return

def on_delete(client, event):
    props = event["resource_properties"]
    bucket, key = props["bucket"], props["key"]
    client.delete_object(Bucket=bucket, Key=key)
    return

def lambda_handler(event, context):
    action = event["tf"]["action"]
    handlers = {
        "create": on_create,
        "update": on_update,
        "delete": on_delete
    }
    client = boto3.client("s3")
    handlers[action](client, event)