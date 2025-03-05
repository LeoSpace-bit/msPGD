will install docker and minio/minio
pip install -r requirements.txt
docker-compose up -d

rm -rf construction_materials.db migrations/

flask db init
flask db migrate -m "Add relationships"
flask db upgrade

python seed.py # тестовые данные (перепроверить доступность картинок)
python app.py
http://localhost:5000/product/1
