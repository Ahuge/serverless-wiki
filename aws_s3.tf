resource "aws_s3_bucket" "SERVERLESS_WIKI_BUCKET" {
  # TODO make bucket name configurable (as they're global)
  bucket = "tmp-serverless-wiki-test"
  acl = "public-read"
  policy = <<POLICY
{
  "Version":"2012-10-17",
  "Statement":[{
	"Sid":"PublicReadGetObject",
        "Effect":"Allow",
	  "Principal": "*",
      "Action":["s3:GetObject"],
      "Resource":["arn:aws:s3:::tmp-serverless-wiki-test/*"
      ]
    }
  ]
}
POLICY
  website {
    index_document = "index.html"
  }
}

resource "aws_iam_user" "SERVERLESS_WIKI_IAM_USER" {
  name = "serverless-wiki"
}

resource "aws_iam_access_key" "SERVERLESS_WIKI_ACCESS_KEY" {
  user = "${aws_iam_user.SERVERLESS_WIKI_IAM_USER.name}"
}

resource "aws_iam_user_policy" "SERVERLESS_WIKI_UPDATE_FILES_POLICY" {
  name = "test"
  user = "${aws_iam_user.SERVERLESS_WIKI_IAM_USER.name}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:*"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::${aws_s3_bucket.SERVERLESS_WIKI_BUCKET.bucket}",
        "arn:aws:s3:::${aws_s3_bucket.SERVERLESS_WIKI_BUCKET.bucket}/*"
      ]
    }
  ]
}
EOF
}


output "secret" {
  value = "${aws_iam_access_key.SERVERLESS_WIKI_ACCESS_KEY.encrypted_secret}"
}
