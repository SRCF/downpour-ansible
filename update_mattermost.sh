#!/bin/sh

VERSION=$1
SHA256SUM=`curl -L https://releases.mattermost.com/$VERSION/mattermost-team-$VERSION-linux-amd64.tar.gz | sha256sum`

sed -i "s/mattermost_version.*/mattermost_version: $VERSION/" main.yml
sed -i "s/mattermost_checksum.*/mattermost_checksum: sha256:$SHA256SUM/" main.yml
