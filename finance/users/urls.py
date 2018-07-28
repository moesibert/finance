from django.conf.urls import url

from finance.users.views import views
from finance.users.views import form_views
from django.contrib.auth.decorators import login_required

app_name = "users"


urlpatterns = [
    # PAGE
    # signup/
    url(r"^signup/$", views.SignUpView.as_view(), name="signup"),
    # login/
    url(r"^signin/$", views.SignInView.as_view(), name="signin"),
    # moesibert/
    url(r"^$", login_required(views.SettingsView.as_view()), name="settings"),

    # ADD / EDIT / DELETE
    url(r"^edit-user/(?P<slug>[\w-]+)/$",
        login_required(form_views.EditUserSettingsView.as_view()),
        name="edit_user"),
    url(r"^edit-user-password/(?P<slug>[\w-]+)/$",
        login_required(form_views.EditUserPasswordSettingsView.as_view()),
        name="edit_user_password"),
    url(r"^edit-user-general/(?P<slug>[\w-]+)/$",
        login_required(form_views.EditUserGeneralSettingsView.as_view()),
        name="edit_user_general"),
    url(r"^edit-user-crypto/(?P<slug>[\w-]+)/$",
        login_required(form_views.EditUserCryptoSettingsView.as_view()),
        name="edit_user_crypto"),

    # moesibert/add-banking-depot/
    url(r"^(?P<slug>[0-9a-zA-Z@.+_-]*)/add-banking-depot/$",
        login_required(form_views.SettingsAddBankingDepotView.as_view()),
        name="add_banking_depot"),
    # moesibert/edit-banking-depot/
    url(r"^(?P<slug>[0-9a-zA-Z@.+_-]*)/edit-banking-depot/$",
        login_required(form_views.SettingsEditBankingDepotView.as_view()),
        name="edit_banking_depot"),
    # moesibert/delete-banking-depot/
    url(r"^(?P<slug>[0-9a-zA-Z@.+_-]*)/delete-banking-depot/$",
        login_required(form_views.SettingsDeleteBankingDepotView.as_view()),
        name="delete_banking_depot"),

    # moesibert/add-crypto-depot/
    url(r"^(?P<slug>[0-9a-zA-Z@.+_-]*)/add-crypto-depot/$",
        login_required(form_views.SettingsAddCryptoDepotView.as_view()), name="add_crypto_depot"),
    # moesibert/edit-crypto-depot/
    url(r"^(?P<slug>[0-9a-zA-Z@.+_-]*)/edit-crypto-depot/$",
        login_required(form_views.SettingsEditCryptoDepotView.as_view()),
        name="edit_crypto_depot"),
    # moesibert/delete-crypto-depot/
    url(r"^(?P<slug>[0-9a-zA-Z@.+_-]*)/delete-crypto-depot/$",
        login_required(form_views.SettingsDeleteCryptoDepotView.as_view()),
        name="delete_crypto_depot"),

    # CHANGE STATE / UPDATE
    # moesibert/logout/
    url(r"^logout/$", views.LogoutView.as_view(), name="logout"),

    # moesibert/init-banking/
    url(r"^(?P<slug>[0-9a-zA-Z@.+_-]*)/init-banking/$", views.init_banking, name="init_banking"),
    # moesibert/set-banking-depot-active/
    url(r"^(?P<slug>[0-9a-zA-Z@.+_-]*)/set-banking-depot-active/(?P<pk>\d+)/$",
        login_required(views.set_banking_depot_active),
        name="set_banking_depot_active"),

    # moesibert/init-crypto/
    url(r"^(?P<slug>[0-9a-zA-Z@.+_-]*)/init-crypto/$", views.init_crypto, name="init_crypto"),
    # moesibert/set-crypto-depot-active/
    url(r"^(?P<slug>[0-9a-zA-Z@.+_-]*)/set-crypto-depot-active/(?P<pk>\d+)/$",
        login_required(views.set_crypto_depot_active),
        name="set_crypto_depot_active"),

]
