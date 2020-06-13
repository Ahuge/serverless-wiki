from cryptography.fernet import Fernet
import os
import re
import sys

import bcrypt
import boto3
from dulwich import client as _mod_client
from dulwich.contrib.paramiko_vendor import ParamikoSSHVendor

from app import templating

SECRET_PATH = "/serverless-wiki/id_rsa"

secrets_manager = boto3.client("secretsmanager")


class MyParamikoSSHVendor(ParamikoSSHVendor):
    def __init__(self, **kwargs):
        super(MyParamikoSSHVendor, self).__init__(**kwargs)
        path = "/tmp/id_rsa"
        print("Downloading SSH key from secrets manager:  {}".format(SECRET_PATH))
        rsa_data = secrets_manager.get_secret_value(SecretId=SECRET_PATH)
        with open(path, "wb") as fh:
            fh.write(rsa_data.get("SecretString").encode("utf-8"))
        self.kwargs = {
            "key_filename": path
        }


_mod_client.get_ssh_vendor = MyParamikoSSHVendor

from dulwich import porcelain
from pyhocon import ConfigFactory


name_pattern = re.compile("^[a-zA-Z0-9_]+$")

s3 = boto3.resource("s3")
bucket = s3.Bucket(os.environ.get("BUCKET_NAME"))


def valid_name(name):
    return name_pattern.match(name)


def fetch_source():
    if not os.path.isdir("/tmp/source/.git"):
        print("cloning")
        porcelain.clone(os.environ["SOURCE_GIT_URL"], "/tmp/source")

    os.system("cd {folder}; git checkout {branch}".format(folder="/tmp/source", branch="dev"))

    print("pulling {}".format(os.environ.get("SOURCE_GIT_URL")))
    porcelain.pull("/tmp/source", os.environ["SOURCE_GIT_URL"], "dev")
    print("updated")


def get_user(username):
    try:
        return ConfigFactory.parse_file("/tmp/source/users/%s.hocon" % username)
    except IOError:
        return None


def update_storage(page, html):
    print("putting object")
    bucket.put_object(Key=page + ".html", Body=html, ContentType="text/html")
    print("put object")


def update_git(page, new_md, username, user):
    for name in os.listdir("/tmp/source"):
        print(name)
    print("-----")
    for name in os.listdir("/tmp/source/website/pages"):
        print(name)
    filename = "/tmp/source/website/pages/%s.md" % page

    with open(filename, "w") as text_file:
        text_file.write(new_md)

    porcelain.add("/tmp/source", filename)
    print("adding {}".format(filename))

    author = "Alex Hughes <alex@archpt.io>"
    committer = "{} <{}}@serverless-wiki.lambda.aws>".format(user.get_string("full_name"), username)
    print("committing")
    commit_message = "Page {} updated".format(page)
    porcelain.commit("/tmp/source", commit_message, author=author, committer=committer)
    print("pushing")
    porcelain.push("/tmp/source", os.environ["SOURCE_GIT_URL"], "dev")
    print("pushed")


def error(status, body):
    return {
        "statusCode": status,
        "body": body,
        "headers": {
            "Access-Control-Allow-Origin": "*",
        }
    }


def handler(event, context):
    username = event["queryStringParameters"]["user"]
    auth = event["queryStringParameters"]["auth"]
    page = event["queryStringParameters"]["page"]

    if not valid_name(username):
        return error("400", "Invalid user")
    if not valid_name(page):
        return error("400", "Invalid page")

    fetch_source()
    user = get_user(username)

    if not user:
        return error("401", "Unknown user")

    print("checking bcrypt hash")
    if not bcrypt.checkpw((os.environ["NONCE"] + auth).encode("utf-8"), user.get_string("password_hash").encode("utf-8")):
        return error(401, "Invalid password")

    print("applying template")
    apiId = event["requestContext"]["apiId"]
    new_html = templating.apply_template(event["body"], "https://" + apiId + ".execute-api." + os.environ["AWS_REGION"] + ".amazonaws.com/{stage}".format(stage=os.environ.get("STAGE")))

    update_git(page, event["body"], username, user)
    update_storage(page, new_html)

    return {
        "statusCode": 200,
        "body": new_html,
        "headers": {
            "Content-Type": "text/html",
            "Access-Control-Allow-Origin": "*",
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            'Access-Control-Allow-Headers': 'Content-Type',
        },
    }
