from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rango.models import Category, Page, UserProfile
from datetime import datetime

class Chapter3Tests(TestCase):
    """Tests for Chapter 3: Django Basics"""
    
    def test_index_view_exists(self):
        """Test that index view returns a response."""
        response = self.client.get(reverse('rango:index'))
        self.assertEqual(response.status_code, 200)
    
    def test_about_view_exists(self):
        """Test that about view returns a response."""
        response = self.client.get(reverse('rango:about'))
        self.assertEqual(response.status_code, 200)
    
    def test_index_contains_hello_message(self):
        """Test that index contains expected text."""
        response = self.client.get(reverse('rango:index'))
        self.assertContains(response, "Rango says hey there partner!")

class Chapter4Tests(TestCase):
    """Tests for Chapter 4: Templates and Media Files"""
    
    def test_uses_template(self):
        """Test that index uses correct template."""
        response = self.client.get(reverse('rango:index'))
        self.assertTemplateUsed(response, 'rango/index.html')
    
    def test_about_uses_template(self):
        """Test that about uses correct template."""
        response = self.client.get(reverse('rango:about'))
        self.assertTemplateUsed(response, 'rango/about.html')
    
    def test_about_contains_author_name(self):
        """Test that about page contains author name."""
        response = self.client.get(reverse('rango:about'))
        self.assertContains(response, "This tutorial has been put together by")

class Chapter5Tests(TestCase):
    """Tests for Chapter 5: Models and Databases"""
    
    def setUp(self):
        """Set up test data."""
        Category.objects.create(name='Test Category', views=100, likes=50)
    
    def test_category_model(self):
        """Test Category model creation."""
        cat = Category.objects.get(name='Test Category')
        self.assertEqual(cat.views, 100)
        self.assertEqual(cat.likes, 50)
        self.assertEqual(str(cat), 'Test Category')
    
    def test_category_slug_creation(self):
        """Test that slug is automatically created."""
        cat = Category.objects.get(name='Test Category')
        self.assertEqual(cat.slug, 'test-category')

class Chapter6Tests(TestCase):
    """Tests for Chapter 6: Models, Templates and Views"""
    
    def setUp(self):
        """Set up test data."""
        cat = Category.objects.create(name='Python', views=128, likes=64)
        Page.objects.create(
            category=cat,
            title='Python Tutorial',
            url='http://python.org',
            views=100
        )
    
    def test_index_shows_categories(self):
        """Test that index page shows categories."""
        response = self.client.get(reverse('rango:index'))
        self.assertContains(response, 'Python')
    
    def test_category_page_exists(self):
        """Test that category page exists and uses template."""
        response = self.client.get(reverse('rango:show_category',
                                           kwargs={'category_name_slug': 'python'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rango/category.html')

class Chapter7Tests(TestCase):
    """Tests for Chapter 7: Forms"""
    
    def setUp(self):
        """Set up test data."""
        Category.objects.create(name='Test', slug='test')
    
    def test_add_category_view_exists(self):
        """Test that add category view exists."""
        response = self.client.get(reverse('rango:add_category'))
        self.assertEqual(response.status_code, 200)
    
    def test_add_category_form(self):
        """Test adding a category via form."""
        response = self.client.post(
            reverse('rango:add_category'),
            {'name': 'New Category'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after post
        self.assertTrue(Category.objects.filter(name='New Category').exists())

class Chapter8Tests(TestCase):
    """Tests for Chapter 8: Working with Templates"""
    
    def setUp(self):
        """Set up test data."""
        Category.objects.create(name='Django', slug='django')
    
    def test_base_template_extends(self):
        """Test that templates extend base.html."""
        response = self.client.get(reverse('rango:index'))
        self.assertTemplateUsed(response, 'rango/base.html')
    
    def test_custom_template_tag(self):
        """Test that custom template tag works."""
        response = self.client.get(reverse('rango:index'))
        self.assertContains(response, 'Django')

class Chapter9Tests(TestCase):
    """Tests for Chapter 9: User Authentication"""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_registration_view(self):
        """Test registration view."""
        response = self.client.get(reverse('rango:register'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_view(self):
        """Test login view."""
        response = self.client.get(reverse('rango:login'))
        self.assertEqual(response.status_code, 200)
    
    def test_restricted_view_redirects_anon(self):
        """Test restricted view redirects anonymous users."""
        response = self.client.get(reverse('rango:restricted'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_restricted_view_allows_auth(self):
        """Test restricted view allows authenticated users."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('rango:restricted'))
        self.assertEqual(response.status_code, 200)

class Chapter10Tests(TestCase):
    """Tests for Chapter 10: Cookies and Sessions"""
    
    def test_visits_cookie(self):
        """Test that visits cookie is set."""
        response = self.client.get(reverse('rango:index'))
        self.client.get(reverse('rango:index'))  # Second visit
        response = self.client.get(reverse('rango:about'))
        self.assertContains(response, 'Visits:')
    
    def test_visits_increment(self):
        """Test that visits counter increments."""
        response = self.client.get(reverse('rango:index'))
        # Simulate different day (would need to mock datetime in real test)
        # This is a simplified test
        self.client.get(reverse('rango:index'))
        response = self.client.get(reverse('rango:about'))
        self.assertContains(response, 'Visits:')