#!/bin/bash

# This script checks if the tmux session defined by 'tmux_name' is still
# running and if not it starts the detached tmux session
# with the 'start_command' command.


now="$(date)"
tmux_name="sholibo"
scriptpath="$( cd "$(dirname "$0")" ; pwd -P )"
start_command="cd ${scriptpath}; python3 sholis_bot.py"

cd "${scriptpath}"

# log the date
touch log.txt
echo  "${now}" >> log.txt

tmux has-session -t ${tmux_name} &>/dev/null

if [ "$?" != "0" ]; then
    # log the action and start the process
    echo -e "Start ${tmux_name}\n\n" >> log.txt
    # create the new session
    tmux new-session -d -s "${tmux_name}"
    tmux send-keys -t "${tmux_name}" "${start_command}" C-m   #C-m is enter
else
    echo -e "Tmux is still running\n\n" >> log.txt
fi

