apt update -y
apt upgrade -y
apt install -y apt-transport-https gnupg2
apt-add-repository -y universe
apt update -y

#------ Apache ------
apt-get install -y apache2
a2enmod proxy proxy_ajp proxy_http rewrite deflate headers proxy_balancer proxy_connect proxy_html

#------ Jitsi -------
curl https://download.jitsi.org/jitsi-key.gpg.key | sudo sh -c 'gpg --dearmor > /usr/share/keyrings/jitsi-keyring.gpg'
echo 'deb [signed-by=/usr/share/keyrings/jitsi-keyring.gpg] https://download.jitsi.org stable/' | sudo tee /etc/apt/sources.list.d/jitsi-stable.list > /dev/null
apt update -y
echo "jitsi-videobridge jitsi-videobridge/jvb-hostname string jitsi" | debconf-set-selections
echo "jitsi-meet jitsi-meet/cert-choice select Self-signed certificate will be generated" | debconf-set-selections
export DEBIAN_FRONTEND=noninteractive
apt install -y jitsi-meet
