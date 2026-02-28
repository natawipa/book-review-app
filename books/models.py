from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import bcrypt


class Book(models.Model):
    """
    Book model to store book information from Google Books API or manual entry
    """
    title = models.CharField(max_length=500, help_text="Book title")
    author = models.CharField(max_length=500, help_text="Book author(s)")
    description = models.TextField(blank=True, null=True, help_text="Book description")
    genre = models.CharField(max_length=200, blank=True, null=True, help_text="Book genre/categories")
    isbn = models.CharField(max_length=13, unique=True, help_text="ISBN-10 or ISBN-13")
    thumbnail_url = models.URLField(blank=True, null=True, help_text="Book cover thumbnail URL")
    published_date = models.CharField(max_length=20, blank=True, null=True, help_text="Publication date")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.author}"

    def get_average_rating(self):
        """Calculate average rating from all reviews"""
        reviews = self.reviews.all()
        if not reviews:
            return 0
        total = sum(review.rating for review in reviews)
        return round(total / len(reviews), 1)

    def get_review_count(self):
        """Get total number of reviews"""
        return self.reviews.count()


class Review(models.Model):
    """
    Review model for both authenticated users and anonymous reviews
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, 
                           help_text="Authenticated user (null for anonymous)")
    nickname = models.CharField(max_length=50, blank=True, null=True, 
                              help_text="Nickname for anonymous reviews")
    password_hash = models.CharField(max_length=60, blank=True, null=True, 
                                   help_text="Hashed password for anonymous review deletion")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    review_text = models.TextField(help_text="Review content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        reviewer = self.user.username if self.user else self.nickname
        return f"Review by {reviewer} for {self.book.title}"

    def set_password(self, raw_password):
        """Hash and set password for anonymous review"""
        if raw_password:
            salt = bcrypt.gensalt()
            self.password_hash = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, raw_password):
        """Check password for anonymous review deletion"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def is_anonymous(self):
        """Check if this is an anonymous review"""
        return self.user is None

    def get_reviewer_name(self):
        """Get the display name of the reviewer"""
        return self.user.username if self.user else (self.nickname or "Anonymous")


class Favorite(models.Model):
    """
    Favorite books for authenticated users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'book']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} favorited {self.book.title}"
