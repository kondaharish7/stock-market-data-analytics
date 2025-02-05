import boto3

def get_s3_client(aws_session):
    try:
        s3_client = aws_session.client('s3')
        print("Authenticated S3 service")
        return s3_client
    except Exception as auth_err:
        print(auth_err)
        print("Authenticating with Keys")
        s3_client = aws_session.client('s3', aws_access_key_id = access_key, aws_secret_access_key = secret_key)
        return s3_client

def get_glue_client(aws_session):
    try:
        glue_client = aws_session.client('glue')
        print("Authenticated Glue service")
        return glue_client
    except:
        print("Authenticating with Keys")
        glue_client = aws_session.client('glue', aws_access_key_id = access_key, aws_secret_access_key = secret_key)
        return glue_client

    return glue_client

if __name__ == '__main__':
    aws_session = boto3.Session(profile_name='smda-etl')

    s3_client = get_s3_client(aws_session = aws_session)
    try:
        print(s3_client.list_objects(Bucket="stock-market-data-analytics"))
    except Exception as err:
        print(err)

    glue_client = get_glue_client(aws_session = aws_session)
    try:
        for i in glue_client.list_jobs()['JobNames']:
            print(i)
    except Exception as err:
        print(err)
