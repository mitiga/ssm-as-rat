mkdir /tmp/ssm_pg # A workdir where we place files we need
cd /tmp/ssm_pg
mkdir -p binds/varlib # A folder which will override /var/lib/amazon/ssm/ on the new namespace
mkdir -p binds/logs # A folder to override /var/log/amazon/ssm
mkdir -p binds/conf # A folder which will override /etc/amazon/ssm on the new namespace

cp -r /etc/amazon/ssm/* ./binds/conf/

# Copy some binaries to avoid orphan worker detection, which causes current execution to fail
cp `which ssm-agent-worker` .
cp `which ssm-session-worker` .

cp ./binds/conf/seelog.xml.template ./binds/conf/seelog.xml

# Enable container mode to avoid setgroup issues
# Note: This is some very ugly editing, you might need to debug this if the default config changes, sorry about that
export CONFIG_FILE=./binds/conf/amazon-ssm-agent.json
cp ./binds/conf/amazon-ssm-agent.json.template $CONFIG_FILE

# Add the "ContainerMode" to the config file (and also add a ',' to the previous line)
sed -i 's/"LongRunningWorkerMonitorIntervalSeconds": 60/"LongRunningWorkerMonitorIntervalSeconds": 60,\n        "ContainerMode": true/' $CONFIG_FILE

# Remove the closing bracket from the config file
head -n -1 < $CONFIG_FILE > $CONFIG_FILE.tmp

# Add the "Identities" section to the config file
echo -ne "    ,\"Identity\": {\n        \"ConsumptionOrder\": [\"OnPrem\", \"EC2\"]\n    }\n}" >> $CONFIG_FILE.tmp
mv $CONFIG_FILE.tmp $CONFIG_FILE

# unshare time - create a new user namespace, make ourselves root in it, and a new filesystem namespace
unshare -rm

mount --bind /tmp/ssm_pg/binds/varlib /var/lib/amazon/ssm # Bind over the existing VM
mount --bind /tmp/ssm_pg/binds/logs /var/log/amazon/ssm # Bind over log directory
mount --bind /tmp/ssm_pg/binds/conf /etc/amazon/ssm # Bind over configuration directory

# Register for the new account
export ACC_CODE="<ACTIVATION_CODE>"
export ACC_ID="<ACTIVATION_ID>"
export ACC_REGION="<REGION>"
amazon-ssm-agent -register -code "$ACC_CODE" -id "$ACC_ID" -region "$ACC_REGION"

# Launch ssm manager
amazon-ssm-agent &
