#!/usr/bin/env python

# Deploy your statically generated site. For now only implemented for uploading to s3,
# would be nice to also support scp, rsync, gh-pages, etc.

import os

import boto3

s3 = boto3.resource("s3")

bucket = s3.Bucket(os.environ.get("BUCKET_NAME"))
top = "target"

types = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript; charset=UTF-8",
    ".hocon": "application/hocon",
}

print("Uploading to {}".format(os.environ.get("BUCKET_NAME")))
for root, _, files in os.walk(top):
    reldir = os.path.relpath(root, top)
    for file in files:
        if reldir == ".":
            target = file
        else:
            target = os.path.join(reldir, file)

        document_type = types[os.path.splitext(file)[1]]
        print("Storing {filename} to {directory} as {doc_type}".format(
          filename=file,
          directory=target,
          doc_type=document_type
        ))

        bucket.put_object(
          Key=target,
          Body=open(os.path.join(root, file), "rb"),
          ContentType=document_type
        )
