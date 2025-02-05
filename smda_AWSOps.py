import boto3

def get_s3_client():
    try:
        aws_session = boto3.Session(profile_name='smda-etl')
        s3_client = aws_session.client('s3')
        print("Authenticated S3 service using Profile")
        return s3_client
    except Exception as auth_err:
        try:
            print("Authenticating with Credentials")
            aws_session = boto3.Session()
            s3_client = aws_session.client('s3')
            print("Authenticated S3 service")
            return s3_client
        except Exception as auth_err1:
            print(auth_err1)
            print("Authenticating with Keys")
            s3_client = aws_session.client('s3', aws_access_key_id = access_key, aws_secret_access_key = secret_key)
            print("Authenticated S3 service using Keys")
            return s3_client

def get_glue_client():
    try:
        aws_session = boto3.Session(profile_name='smda-etl')
        glue_client = aws_session.client('glue')
        print("Authenticated Glue service using Profile")
        return s3glue_client_client
    except Exception as auth_err:
        try:
            print("Authenticating with Profile")
            aws_session = boto3.Session()
            glue_client = aws_session.client('glue')
            print("Authenticated Glue service")
            return glue_client
        except Exception as auth_err1:
            print(auth_err1)
            print("Authenticating with Keys")
            glue_client = aws_session.client('glue', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
            print("Authenticated Glue service using keys")
            return glue_client

    # try:
    #     glue_client = aws_session.client('glue')
    #     print("Authenticated Glue service")
    #     return glue_client
    # except:
    #     print("Authenticating with Keys")
    #     glue_client = aws_session.client('glue', aws_access_key_id = access_key, aws_secret_access_key = secret_key)
    #     return glue_client
    #
    # return glue_client

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
