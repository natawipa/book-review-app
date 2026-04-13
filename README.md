# Read and Rate

A full-stack web application for discovering, reviewing, and sharing Japanese books. Users can search books by title, author, or ISBN, add new books using Google Books API, and post reviews either as authenticated users or anonymously.

## Features

### Core Features

- **Book Search**: Search by title, author, or ISBN
- **Google Books Integration**: Automatically fetch book details for new ISBNs
- **Review System**: 5-star rating system with text reviews
- **Dual User System**: Both registered and anonymous users can post reviews
- **Favorites**: Registered users can save favorite books
- **Admin Moderation**: Staff can moderate all reviews

### User Roles

- **Guest Users**: Search, view books, post anonymous reviews (with password protection)
- **Registered Users**: All guest features plus review management, favorites, profile
- **Administrators**: Full content moderation and management

## Tech Stack

- **Backend**: Django 5.2.5 (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **External API**: Google Books API
- **Authentication**: Django built-in system
- **Security**: bcrypt for anonymous review passwords, CSRF protection

## Requirements

- Python 3.8+
- pip (Python package manager)
- Internet connection (for Google Books API)

## Quick Start

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd /Users/natawipa/readandrate

# Install dependencies (already done if following this guide)
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Apply migrations (already done if following this guide)
python manage.py migrate

# Create superuser (already done if following this guide)
python manage.py createsuperuser
```

### 3. Run Development Server

```bash
# Start the development server
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000) to access the application.

### 4. Admin Access

Visit [http://localhost:8000/admin](http://localhost:8000/admin) and login with:

- Username: `admin`
- Password: (the password you set during superuser creation)

## Usage Guide

### Adding Books

1. **By ISBN**: Click "Add Book" and enter a valid ISBN-10 or ISBN-13
2. **Manual**: Use Django admin to manually add books
3. **API Integration**: The system automatically fetches book details from Google Books API

### Writing Reviews

**For Guests (Anonymous)**:

1. Navigate to any book page
2. Fill in nickname and password (for future deletion)
3. Select rating and write review
4. Submit review

**For Registered Users**:

1. Login to your account
2. Navigate to any book page
3. Select rating and write review (no password needed)
4. Submit review

### Managing Reviews

- **Anonymous users**: Use the password you set to delete your reviews
- **Registered users**: Delete/edit reviews from book pages or user profile
- **Administrators**: Moderate all reviews via admin panel or staff interface

## Project Structure

```
readandrate/
├── books/                  # Main Django app
│   ├── models.py          # Book, Review, Favorite models
│   ├── views.py           # All application views
│   ├── urls.py            # URL routing
│   ├── admin.py           # Django admin configuration
│   └── migrations/        # Database migrations
├── templates/             # HTML templates
│   ├── base.html          # Base template with Bootstrap
│   ├── books/             # Book-related templates
│   └── registration/      # Authentication templates
├── static/                # Static files (CSS, JS)
├── readandrate/           # Django project settings
└── requirements.txt       # Python dependencies
```

## Configuration

### Environment Variables (Production)

```python
# In settings.py for production
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'readandrate_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Google Books API

The application uses Google Books API without authentication for basic book lookups. For production with high usage, consider:

1. Getting a Google Books API key
2. Adding rate limiting
3. Implementing caching for API responses

## Troubleshooting

### Common Issues

**1. Migration Errors**

```bash
# Reset migrations if needed
python manage.py migrate books zero
python manage.py makemigrations books
python manage.py migrate
```

**2. Static Files Not Loading**

```bash
# Collect static files for production
python manage.py collectstatic
```

**3. Google Books API Issues**

- Check internet connection
- Verify ISBN format (10 or 13 digits)
- Some books may not be available in Google Books

**4. bcrypt Installation Issues**

```bash
# On some systems, you might need
pip install bcrypt --no-binary :all:
```

## Security Features

- **CSRF Protection**: Enabled for all forms
- **Password Hashing**: bcrypt for anonymous review passwords
- **Input Validation**: Server-side validation for all inputs
- **SQL Injection Protection**: Django ORM prevents raw SQL vulnerabilities
- **XSS Protection**: Template auto-escaping enabled

## API Endpoints

### Book Operations

- `GET /`: Homepage with search
- `GET /book/<id>/`: Book detail page
- `POST /book/<id>/review/`: Submit review
- `POST /add-isbn/`: Add book by ISBN

### User Operations

- `POST /register/`: User registration
- `POST /login/`: User login
- `POST /logout/`: User logout
- `GET /my-reviews/`: User's reviews
- `GET /my-favorites/`: User's favorites

### Ajax Endpoints

- `GET /search/`: Book search API
- `POST /book/<id>/toggle-favorite/`: Toggle favorite status

---

**ReadAndRate** - Happy Reading!
