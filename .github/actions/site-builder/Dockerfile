
FROM python:3

LABEL "com.github.actions.name"="Site Builder"
LABEL "com.github.actions.description"="Builds your site"
LABEL "com.github.actions.icon"="code"
LABEL "com.github.actions.color"="blue"

# LABEL "repository"="https://github.com/lgeiger/black-action"
# LABEL "homepage"="https://github.com/lgeiger/black-action"
# LABEL "maintainer"="Lukas Geiger <lukas.geiger94@gmail.com>"

RUN apt-get update && apt-get install -y git
# RUN apt-get install -y jq
RUN pip install boto3

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]