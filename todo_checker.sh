#!/bin/bash

check_file() {
    local file=$1
    local match_pattern=$2

    local file_changes_with_context=$(git diff -U999999999 -p --cached --color=always -- $file)

    # From the diff, get the green lines starting with '+' and including '$match_pattern'
    local matched_additions=$(echo "$file_changes_with_context" | grep -C4 $'^\e\\[32m\+.*'"$match_pattern")

    if [ -n "$matched_additions" ]; then
        echo -e "\n$file additions match '$match_pattern':\n"

        for matched_line in $matched_additions
        do
            echo "$matched_line"
        done

        echo "Not committing, because $file matches $match_pattern"
        exit 1
    fi
}

# Actual hook logic:

MATCH='TODO'
for file in `git diff --cached -p --name-status | cut -c3-`; do
    for match_pattern in $MATCH
    do
        check_file $file $match_pattern
    done
done
exit
