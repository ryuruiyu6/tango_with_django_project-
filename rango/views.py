from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from .forms import UserRegistrationForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('rango:index')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'rango/register.html', {'form': form})


def index(request):
    """Main page view showing top categories and pages."""
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only-- or all if less than 5.
    category_list = Category.objects.order_by('-likes')[:5]
    
    # Query the database for a list of ALL pages currently stored.
    # Order the pages by the number of views in descending order.
    # Retrieve the top 5 only-- or all if less than 5.
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    
    # Handle visitor cookies
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session.get('visits', 1)
    
    response = render(request, 'rango/index.html', context=context_dict)
    return response

def about(request):
    """About page view."""
    visitor_cookie_handler(request)
    context_dict = {
        'yourname': 'Rui Yu',  # Your name
        'visits': request.session.get('visits', 1)
    }
    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    """Display a specific category and its pages."""
    context_dict = {}
    
    try:
        # Can we find a category name slug with the given name?
        category = Category.objects.get(slug=category_name_slug)
        
        # Retrieve all of the associated pages.
        pages = Page.objects.filter(category=category)
        
        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        context_dict['category'] = None
        context_dict['pages'] = None
    
    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    """Add a new category (logged in users only)."""
    form = CategoryForm()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)
            # Now that the category is saved, redirect the user back to the index view.
            return redirect('/rango/')
        else:
            # The supplied form contained errors - print them to the terminal.
            print(form.errors)
    
    # Will handle the bad form, new form, or no form supplied cases.
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    """Add a new page to a category (logged in users only)."""
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    # You cannot add a page to a Category that does not exist...
    if category is None:
        return redirect('/rango/')
    
    form = PageForm()
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                
                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)
    
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    """Handle user registration."""
    registered = False
    
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    context_dict = {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered
    }
    
    return render(request, 'rango/register.html', context=context_dict)

def user_login(request):
    """Handle user login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
    """Restricted page - only visible to logged in users."""
    return render(request, 'rango/restricted.html')

@login_required
def user_logout(request):
    """Handle user logout."""
    logout(request)
    return redirect(reverse('rango:index'))

# Helper functions for cookies
def get_server_side_cookie(request, cookie, default_val=None):
    """Get a cookie from the server-side session."""
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    """Handle visitor cookie for tracking visits."""
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,
                                              'last_visit',
                                              str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')
    
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    
    request.session['visits'] = visits