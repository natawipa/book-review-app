import requests
import re
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from .models import Book, Review, Favorite
import json


def home(request):
    """
    Homepage with search functionality
    """
    query = request.GET.get('q', '').strip()
    books = []
    
    if query:
        # Search books by title, author, or ISBN
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        ).distinct()
    
    # Get recent books if no search query
    if not query:
        books = Book.objects.all()[:12]
    
    return render(request, 'books/home.html', {
        'books': books,
        'query': query,
        'title': 'Read and Rate - Book Reviews'
    })


def book_detail(request, book_id):
    """
    Display book details and reviews
    """
    book = get_object_or_404(Book, id=book_id)
    reviews = book.reviews.all()
    
    # Check if user has favorited this book
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, book=book).exists()
    
    return render(request, 'books/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'is_favorited': is_favorited,
        'title': f"{book.title} - Read and Rate"
    })


def search_books(request):
    """
    AJAX endpoint for book search
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'books': []})
    
    books = Book.objects.filter(
        Q(title__icontains=query) |
        Q(author__icontains=query) |
        Q(isbn__icontains=query)
    ).values('id', 'title', 'author', 'thumbnail_url')[:10]
    
    return JsonResponse({'books': list(books)})


def validate_isbn(isbn):
    """
    Validate ISBN format (10 or 13 digits)
    """
    # Remove any hyphens or spaces
    clean_isbn = re.sub(r'[-\s]', '', isbn)
    
    # Check if it's 10 or 13 digits
    if not clean_isbn.isdigit():
        return None
    
    if len(clean_isbn) == 10 or len(clean_isbn) == 13:
        return clean_isbn
    
    return None


def fetch_book_from_google_api(isbn):
    """
    Fetch book information from Google Books API
    """
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('totalItems', 0) == 0:
            return None
            
        item = data['items'][0]
        volume_info = item.get('volumeInfo', {})
        
        # Extract book information
        book_data = {
            'title': volume_info.get('title', 'Unknown Title'),
            'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
            'description': volume_info.get('description', ''),
            'genre': ', '.join(volume_info.get('categories', [])),
            'isbn': isbn,
            'thumbnail_url': volume_info.get('imageLinks', {}).get('thumbnail', ''),
            'published_date': volume_info.get('publishedDate', ''),
        }
        
        return book_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Google Books API: {e}")
        return None
    except Exception as e:
        print(f"Error parsing Google Books data: {e}")
        return None


def add_book_by_isbn(request):
    """
    Add book by ISBN using Google Books API
    """
    if request.method == 'POST':
        isbn = request.POST.get('isbn', '').strip()
        
        # Validate ISBN
        clean_isbn = validate_isbn(isbn)
        if not clean_isbn:
            messages.error(request, "Invalid ISBN format. Please enter a valid 10 or 13 digit ISBN.")
            return render(request, 'books/add_isbn.html')
        
        # Check local database first to avoid unnecessary API calls
        book = Book.objects.filter(isbn=clean_isbn).first()
        if book:
            messages.info(request, f"Book '{book.title}' already exists in our database!")
            return redirect('book_detail', book_id=book.id)
        
        # Fetch from Google Books API
        book_data = fetch_book_from_google_api(clean_isbn)
        if not book_data:
            messages.error(request, "Book not found in Google Books database. Please try a different ISBN.")
            return render(request, 'books/add_isbn.html')
        
        # Create book record
        try:
            book = Book.objects.create(**book_data)
            messages.success(request, f"Book '{book.title}' has been successfully added!")
            return redirect('book_detail', book_id=book.id)
        except Exception as e:
            messages.error(request, f"Error saving book: {e}")
            return render(request, 'books/add_isbn.html')
    
    return render(request, 'books/add_isbn.html', {
        'title': 'Add Book by ISBN - Read and Rate'
    })


def submit_review(request, book_id):
    """
    Submit a review for a book
    """
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text', '').strip()
        
        # Validate input
        if not rating or not review_text:
            messages.error(request, "Both rating and review text are required.")
            return redirect('book_detail', book_id=book_id)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                messages.error(request, "Rating must be between 1 and 5.")
                return redirect('book_detail', book_id=book_id)
        except ValueError:
            messages.error(request, "Invalid rating.")
            return redirect('book_detail', book_id=book_id)
        
        # Create review
        if request.user.is_authenticated:
            # Check if user already reviewed this book
            if Review.objects.filter(user=request.user, book=book).exists():
                messages.error(request, "You have already reviewed this book.")
                return redirect('book_detail', book_id=book_id)
            
            # Create authenticated user review
            Review.objects.create(
                book=book,
                user=request.user,
                rating=rating,
                review_text=review_text
            )
            messages.success(request, "Your review has been submitted successfully!")
            
        else:
            # Anonymous review
            nickname = request.POST.get('nickname', '').strip()
            password = request.POST.get('password', '').strip()
            
            if not nickname or not password:
                messages.error(request, "Nickname and password are required for anonymous reviews.")
                return redirect('book_detail', book_id=book_id)
            
            review = Review(
                book=book,
                nickname=nickname,
                rating=rating,
                review_text=review_text
            )
            review.set_password(password)
            review.save()
            messages.success(request, "Your anonymous review has been submitted successfully!")
        
        return redirect('book_detail', book_id=book_id)
    
    return redirect('book_detail', book_id=book_id)


@login_required
def delete_review(request, review_id):
    """
    Delete a review (authenticated users only)
    """
    review = get_object_or_404(Review, id=review_id)
    
    # Check permission
    if review.user != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to delete this review.")
        return redirect('book_detail', book_id=review.book.id)
    
    if request.method == 'POST':
        book_id = review.book.id
        review.delete()
        messages.success(request, "Review deleted successfully.")
        return redirect('book_detail', book_id=book_id)
    
    return render(request, 'books/delete_review.html', {
        'review': review,
        'title': 'Delete Review - Read and Rate'
    })


def delete_anonymous_review(request, review_id):
    """
    Delete anonymous review with password verification
    """
    review = get_object_or_404(Review, id=review_id)
    
    if not review.is_anonymous():
        messages.error(request, "This is not an anonymous review.")
        return redirect('book_detail', book_id=review.book.id)
    
    if request.method == 'POST':
        password = request.POST.get('password', '')
        
        if review.check_password(password):
            book_id = review.book.id
            review.delete()
            messages.success(request, "Anonymous review deleted successfully.")
            return redirect('book_detail', book_id=book_id)
        else:
            messages.error(request, "Incorrect password.")
    
    return render(request, 'books/delete_anonymous_review.html', {
        'review': review,
        'title': 'Delete Review - Read and Rate'
    })


@login_required
def toggle_favorite(request, book_id):
    """
    Toggle favorite status for a book
    """
    book = get_object_or_404(Book, id=book_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, book=book)
    
    if not created:
        favorite.delete()
        is_favorited = False
        message = f"Removed '{book.title}' from favorites."
    else:
        is_favorited = True
        message = f"Added '{book.title}' to favorites."
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_favorited': is_favorited,
            'message': message
        })
    
    messages.success(request, message)
    return redirect('book_detail', book_id=book_id)


@login_required
def user_favorites(request):
    """
    Display user's favorite books
    """
    favorites = Favorite.objects.filter(user=request.user).select_related('book')
    return render(request, 'books/user_favorites.html', {
        'favorites': favorites,
        'title': 'My Favorites - Read and Rate'
    })


@login_required
def user_reviews(request):
    """
    Display user's reviews
    """
    reviews = Review.objects.filter(user=request.user).select_related('book')
    return render(request, 'books/user_reviews.html', {
        'reviews': reviews,
        'title': 'My Reviews - Read and Rate'
    })


# Authentication views
def register_view(request):
    """
    User registration
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            # Auto login after registration
            user = authenticate(username=form.cleaned_data['username'],
                              password=form.cleaned_data['password1'])
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'title': 'Register - Read and Rate'
    })


def login_view(request):
    """
    User login
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {
        'form': form,
        'title': 'Login - Read and Rate'
    })


def logout_view(request):
    """
    User logout
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# Admin views
@staff_member_required
def admin_reviews(request):
    """
    Admin view to moderate reviews
    """
    reviews = Review.objects.all().select_related('book', 'user')
    return render(request, 'books/admin_reviews.html', {
        'reviews': reviews,
        'title': 'Moderate Reviews - Admin'
    })


@staff_member_required
def admin_delete_review(request, review_id):
    """
    Admin delete any review
    """
    review = get_object_or_404(Review, id=review_id)
    
    if request.method == 'POST':
        book_id = review.book.id
        review.delete()
        messages.success(request, "Review deleted by admin.")
        return redirect('admin_reviews')
    
    return render(request, 'books/admin_delete_review.html', {
        'review': review,
        'title': 'Delete Review - Admin'
    })
