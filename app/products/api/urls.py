from django.urls import path
from . import views

app_name = "products-api"

urlpatterns = [
    # path('list/', views.product_list_view, name="list"),
    # path('create/', views.product_create_view, name="create"),
    # path('detail/<id>/', views.product_detail_view, name="detail"),
    # path('update/<id>/', views.product_update_view, name="update"),
    # path('delete/<id>/', views.product_delete_view, name="delete"),

    path('list/', views.ProductListView.as_view(), name='list'),
    path('create/', views.ProductCreateView.as_view(), name='create'),
    path('detail/<id>/', views.ProductDetailView.as_view(), name='detail'),
    path('update/<id>/', views.ProductUpdateView.as_view(), name='update'),
    path('delete/<id>/', views.ProductDeleteView.as_view(), name='delete'),
]