#!/bin/bash


git clone https://github.com/Ahuge/serverless-wiki source
mkdir target

# generate.sh
export CODE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

[[ -d source ]] || exit "Please set SOURCE to the source git directory"
[[ -d target ]] || exit "Please set TARGET to the target git directory"

cp -r ${CODE}/website/resources/* target
cp -r source/users target

# And convert $SOURCE/pages/*.md to $TARGET/*.html :)
for file in `cd source; find . -name "*.md"`; do
  mkdir -p target/`dirname ${file}`
  echo "Processing source/$file into target/${file%md}html"
  python ./convert_page.py < source/${file} > target/${file%md}html
done
# end generate.sh

ls -alFh target

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# deploy
python ./deploy.py
