# LinkSafe

LinkSafe is a lightweight Django URL shortener that creates clean, shareable links with optional **time-based** and **click-based** expiration rules. It includes a polished UI, click tracking, and full Docker support.

## Features
- Short auto-generated links (6-character ID)
- Time expiry & click-limit expiry
- Click tracking with auto-expiration logic
- Modern, responsive UI
- Copy-to-clipboard share card
- Docker-ready for simple deployment

## Run Locally
pip install -r requirements.txt  
python manage.py migrate  
python manage.py runserver  

## Run with Docker
docker build -t linksafe .  
docker run -p 80:80 \
  -e DJANGO_SECRET_KEY="dev-key" \
  -e DJANGO_DEBUG=True \
  linksafe  

## Environment Variables
- `DJANGO_SECRET_KEY`

## Project Structure
linksafe/  
├── app/                # models, forms, views, templates  
├── linksafe/           # settings, urls, wsgi  
├── Dockerfile  
├── requirements.txt  
└── README.md  
<img width="1347" height="602" alt="image" src="https://github.com/user-attachments/assets/3a157d76-eaa0-45c1-aeb0-d73bc00c5225" />

## License
MIT License.
