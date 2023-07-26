sudo su
wget https://downloads.mitmproxy.org/9.0.1/mitmproxy-9.0.1-linux.tar.gz 
mkdir ~/bin/
tar xvf mitmproxy-9.0.1-linux.tar.gz --directory ~/bin/
mitmproxy -s /tmp/mock_server.py --no-http2 --listen-port 5000 --set block_global=false