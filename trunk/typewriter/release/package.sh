#!/bin/bash
product_version=$1
if [ "x$product_version" == "x" ]; then
  echo "usage: $0 \$product_version"
  exit 1
fi
cd `dirname $0`
svn export .. typewriter/
zip -r typewriter-${product_version}.zip typewriter/
rm -R typewriter/
