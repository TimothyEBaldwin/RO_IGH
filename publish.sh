#!/bin/sh

set -xe

./igh_mirror

for i in BCM2835 BCM2835Pico Batch1to6 BonusBin BuildHost Disc IOMDHAL OMAP3 OMAP4 OMAP5 PlingSystem S3C Titanium Tungsten iMx6 All
do
  (
    cd "repositories/Products/${i}.git"
    git push git@github.com:TimothyEBaldwin/RO_All_Commits.git "all-commits:$i"
  )
done
