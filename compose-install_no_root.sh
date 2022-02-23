# /bin/bash
mkdir -p $HOME/bin && \
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o $HOME/bin/docker-compose && \
chmod +x $HOME/bin/docker-compose &&
echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc && \
bash