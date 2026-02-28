from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('add-isbn/', views.add_book_by_isbn, name='add_book_by_isbn'),
    
    # Search
    path('search/', views.search_books, name='search_books'),
    
    # Reviews
    path('book/<int:book_id>/review/', views.submit_review, name='submit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('review/<int:review_id>/delete-anonymous/', views.delete_anonymous_review, name='delete_anonymous_review'),
    
    # Favorites
    path('book/<int:book_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('my-favorites/', views.user_favorites, name='user_favorites'),
    path('my-reviews/', views.user_reviews, name='user_reviews'),
    
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin
    path('admin/reviews/', views.admin_reviews, name='admin_reviews'),
    path('admin/review/<int:review_id>/delete/', views.admin_delete_review, name='admin_delete_review'),
]