#!/bin/sh

# Help function
help()
{
   # Display help
   echo "Check if rasa and actions server are running, start them if necessary"
   echo
   echo "Syntax: /bin/bash rasa_healthy_check.sh [-h] path_to_logs"
   echo "Args:"
   echo "path_to_logs   Absolute path to logs directory."
   echo "Options:"
   echo "h     Print help."
   
   echo
}

# Process the input options.
# Get the options
while getopts ":h" option; do
   case $option in
      h) # display help
         help
         exit;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

eval "$(conda shell.bash hook)"
conda activate dagfinn

process_actions="rasa run actions"
process_server="rasa run"

# Log files
now=$(date +"%d%m%Y-%H%M")
path=$1
actions_logs="${path}/actions-${now}.log"
rasa_logs="${path}/rasa-${now}.log"

# Check if actions server is running
if ! ps ax | grep -v grep | grep "$process_actions"
then 
    rasa run actions > "$actions_logs" 2>&1 &
fi

# Check if rasa server is running
if ! ps ax | grep -v grep | grep -v "$process_actions" | grep "$process_server"
then 
    rasa run > "$rasa_logs" 2>&1 &
fi

conda deactivate