#!/bin/bash
if [ ! -d $1 ]; then
    exit 3
fi

[ -z "$(ls $1)" ]
