# NaiveBay Back

REST API for NaiveBay, an online auction site. The web front end is in [Drakit0/NaiveBay](https://github.com/Drakit0/NaiveBay).

Built for the course Desarrollo de Aplicaciones y Servicios (Comillas ICAI, January to May 2025).

## What it does

Users register, log in and publish auctions. Other users bid on them, rate them from 1 to 5 and leave comments. The API is documented with OpenAPI (drf-spectacular).

Implemented:

- Registration, login with JWT (access and refresh tokens), logout with refresh token blacklisting, profile view and update, password change.
- Categories (create, update and delete are staff only).
- Auctions with title, description, starting price, stock, brand, category, closing date and either an image URL or an uploaded image. At least one of the two is required.
- Auction listing with pagination (5 per page) and filters: `search` (at least 3 characters, matched on title and description), `category`, `min_price`, `max_price`, `min_rating`, `max_rating` and `state` (`open` or `closed`).
- Bids: a bid must exceed the current highest bid, or reach the starting price if there is none. Bids on closed auctions are rejected.
- One rating per user and auction. Ratings and comments cannot be created, changed or deleted once the auction is closed. The average rating is computed from the ratings.
- Comments per auction, editable by their author or staff.
- Per-user lists: my auctions, my bids, my ratings, my comments.

## Stack

Python 3, Django 5.2, Django REST Framework, djangorestframework-simplejwt, drf-spectacular, django-cors-headers, dj-database-url, Pillow, gunicorn. PostgreSQL in deployment, SQLite if no database URL is set.

## Run locally

```bash
cd naiveBayBack
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then edit the values
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API is served at `http://127.0.0.1:8000/api/`. Swagger UI is at `/api/schema/swagger-ui/` and the Django admin at `/admin/`.

## Environment variables

| Name | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django secret key. Required. |
| `DJANGO_DEBUG` | `True` to enable debug mode. Defaults to `False`. |
| `DJANGO_ALLOWED_HOSTS` | Comma separated host names. Defaults to `localhost,127.0.0.1,0.0.0.0`. |
| `DATABASE_URL` | Database URL, for example a PostgreSQL URL. Defaults to a local SQLite file. |

Variables are read from the environment or from a `.env` file in `naiveBayBack/`.

## Main endpoints

- `POST /api/users/register/`, `POST /api/users/login/`, `POST /api/token/refresh/`, `POST /api/users/log-out/`
- `GET|PATCH|DELETE /api/users/profile/`, `POST /api/users/change-password/`
- `GET /api/users/myAuctions/`, `myBids/`, `myRatings/`, `myComments/`
- `GET|POST /api/auctions/`, `GET|PUT|PATCH|DELETE /api/auctions/<id>/`
- `GET|POST /api/auctions/<id>/bids/`, `/api/auctions/<id>/bids/<bid_id>/`
- `/api/auctions/<id>/rating/`
- `GET|POST /api/auctions/<id>/comments/`, `/api/auctions/<id>/comments/<comment_id>/`
- `GET|POST /api/auctions/categories/`

## Authors

- Pablo Tuñón Laguna
- Sergio Jiménez Romero

## Licence

MIT, see `LICENSE`.
