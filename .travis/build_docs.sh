#! /bin/bash

echo $(if [[ "$TRAVIS_BRANCH" == "develop" || "$TRAVIS_BRANCH" == "main" ]];
then echo "$TRAVIS_BRANCH"; elif [[ ! -z "$TRAVIS_TAG" ]]; then echo "tags/$TRAVIS_TAG";
else echo "branches/$(echo $TRAVIS_BRANCH | tr / _ | tr - .)"; fi) | tee /tmp/output_location
docker build -f Dockerfile.docs -t docs_image --build-arg img_tag=$(echo ${TRAVIS_BRANCH} | tr / _) .
docker cp $(docker create docs_image):/root/build/doc/_build/html /tmp/build.html
git checkout gh-pages
rm -rf dripline-cpp
git clean -d -f -x
ls
rsync -av --delete /tmp/build.html/ ./$(cat /tmp/output_location)
tree -L 3
git add $(cat /tmp/output_location)
git status
git diff --cached --quiet; export HAVE_STAGED_FILES=$?
echo $HAVE_STAGED_FILES
if [[ "$HAVE_STAGED_FILES" != "0" ]]; then
    git commit -m "build docs for ${TRAVIS_BRANCH}"
    git remote -v
    git remote set-url origin "git@github.com:${TRAVIS_REPO_SLUG}"
    git remote -v
    git push
else
    echo "No documentation updates to push"
fi
