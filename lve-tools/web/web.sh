cd /lve/lve-tools
python -m pip install -e ".[web]"
cd /lve/lve-tools/web 
rm -rf /var/www/html
ln -s /lve/lve-tools/web/build /var/www/html
python make.py
if [ "$HOT" = "1" ]; then PORT=80 python live.py; else nginx -g "daemon off;"; fi