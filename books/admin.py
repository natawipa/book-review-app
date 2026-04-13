from django.contrib import admin
from .models import Book, Review, Favorite


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'genre', 'published_date', 'get_review_count', 'created_at']
    list_filter = ['genre', 'published_date', 'created_at']
    search_fields = ['title', 'author', 'isbn', 'description']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'isbn', 'description')
        }),
        ('Categories & Publication', {
            'fields': ('genre', 'published_date', 'thumbnail_url')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_review_count(self, obj):
        return obj.get_review_count()
    get_review_count.short_description = 'Reviews'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['book', 'get_reviewer_name', 'rating', 'is_anonymous', 'created_at', 'updated_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['book__title', 'user__username', 'nickname', 'review_text']
    readonly_fields = ['created_at', 'updated_at', 'password_hash']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('book', 'rating', 'review_text')
        }),
        ('Reviewer Information', {
            'fields': ('user', 'nickname'),
            'description': 'Either user (for authenticated) or nickname (for anonymous) will be filled'
        }),
        ('Security', {
            'fields': ('password_hash',),
            'classes': ('collapse',),
            'description': 'Password hash for anonymous review deletion'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_anonymous(self, obj):
        return obj.is_anonymous()
    is_anonymous.boolean = True
    is_anonymous.short_description = 'Anonymous'
    
    def get_reviewer_name(self, obj):
        return obj.get_reviewer_name()
    get_reviewer_name.short_description = 'Reviewer'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'book__title', 'book__author']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


# Customize admin site headers
admin.site.site_header = "Read and Rate Admin"
admin.site.site_title = "Read and Rate Admin Portal"
admin.site.index_title = "Welcome to Read and Rate Administration"
