# Backend script

## Check is rasa is running
Syntax to run the script:
```bash
/bin/bash rasa_healthy_check.sh [-h] path_to_logs
```

A cron job can be created to check the servers status periodically. 

Example of cron job to check status every five mintues, you need to specify the paths to dagfinn repository (**PATH_TO_DAGFINN**) and to the logs folder (**PATH_TO_LOGS**).
```
*/5 * * * * cd PATH_TO_DAGFINN && /bin/bash scripts/backend/rasa_healthy_check.sh PATH_TO_LOGS
```

## How to kill the server
Procedure to follow to kill rasa and actions servers

1. Stop cron job running `rasa_healthy_check.sh` if there is one.
2. Kill actions server using its PID with this command:
```bash
kill `ps ax | grep -v grep | grep "rasa run actions" | awk '{print $1}'`
```
3. Kill rasa server using its PID with this command:
```bash
kill `ps ax | grep -v grep | grep -v "rasa run actions" | grep "rasa run" | awk '{print $1}'`
```