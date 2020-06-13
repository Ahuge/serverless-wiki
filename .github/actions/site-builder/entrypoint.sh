#!/bin/bash


git clone https://github.com/Ahuge/serverless-wiki source
mkdir target

export MARKDOWN_SOURCE_ROOT="./source/website/pages"

# generate.sh
[[ -d source ]] || exit "Please set SOURCE to the source git directory"
[[ -d target ]] || exit "Please set TARGET to the target git directory"

cp -r ./source/website/resources/* target
cp -r ./source/users target

# And convert $SOURCE/pages/*.md to $TARGET/*.html :)

for file in `cd ${MARKDOWN_SOURCE_ROOT}; find . -name "*.md"`; do
  mkdir -p target/`dirname ${file}`
  echo "Processing ${MARKDOWN_SOURCE_ROOT}/$file into target/${file%md}html"
  python ./source/.github/actions/site-builder/convert_page.py < ${MARKDOWN_SOURCE_ROOT}/${file} > target/${file%md}html
done
# end generate.sh

ls -alFh target

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# deploy
python ./source/.github/actions/site-builder/deploy.py
