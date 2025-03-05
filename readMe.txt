will install docker and minio/minio
pip install -r requirements.txt
docker-compose up -d
python seed.py # тестовые данные (перепроверить доступность картинок)
python app.py
http://localhost:5000/product/1
