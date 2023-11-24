cd /lve/lve-tools
python -m pip install --cache-dir /pipcache -e ".[web]"
cd /lve/lve-tools/web 
rm -rf /var/www/html
ln -s /lve/lve-tools/web/build /var/www/html
python make.py
if [ "$HOT" = "1" ]; then 
    echo "Serving with hot reload on port 80"
    PORT=80 python live.py; 
else 
    echo "Serving with nginx on port 80"
    nginx -g "daemon off;"; 
fi