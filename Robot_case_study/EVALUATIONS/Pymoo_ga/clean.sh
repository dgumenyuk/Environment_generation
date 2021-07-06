#!/bin/bash
for filename in ./*.py; do
        echo $filename
        black $filename
done
