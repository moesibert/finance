from django.contrib.auth.mixins import LoginRequiredMixin
from apps.crypto.models import Transaction, Flow, Account, Asset, Trade, Depot
from apps.crypto.forms import FlowForm, AccountSelectForm, TradeForm, DepotForm, AccountForm, AssetSelectForm, \
    DepotSelectForm, DepotActiveForm, TransactionForm, AssetForm
from apps.core.mixins import CustomAjaxDeleteMixin, AjaxResponseMixin, CustomGetFormUserMixin, \
    GetFormWithDepotAndInitialDataMixin, GetFormWithDepotMixin
from django.shortcuts import get_object_or_404
from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
import json


# mixins
class CustomGetFormMixin:
    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        depot = self.request.user.crypto_depots.get(is_active=True)
        return form_class(depot, **self.get_form_kwargs())


class GetDepotMixin:
    def get_depot(self):
        return self.request.user.crypto_depots.filter(is_active=True).first()


# depot
class AddDepotView(LoginRequiredMixin, CustomGetFormUserMixin, AjaxResponseMixin, generic.CreateView):
    form_class = DepotForm
    model = Depot
    template_name = "symbols/form_snippet.njk"


class EditDepotView(LoginRequiredMixin, CustomGetFormUserMixin, AjaxResponseMixin, generic.UpdateView):
    model = Depot
    form_class = DepotForm
    template_name = "symbols/form_snippet.njk"


class DeleteDepotView(LoginRequiredMixin, CustomGetFormUserMixin, AjaxResponseMixin, generic.FormView):
    model = Depot
    template_name = "symbols/form_snippet.njk"
    form_class = DepotSelectForm

    def form_valid(self, form):
        depot = form.cleaned_data["depot"]
        user = depot.user
        depot.delete()
        if user.crypto_depots.count() <= 0:
            user.save()
        return HttpResponse(json.dumps({"valid": True}), content_type="application/json")


class SetActiveDepotView(LoginRequiredMixin, generic.View):
    http_method_names = ['get', 'head', 'options']

    def get(self, request, pk, *args, **kwargs):
        depot = get_object_or_404(self.request.user.crypto_depots.all(), pk=pk)
        form = DepotActiveForm(data={'is_active': True}, instance=depot)
        if form.is_valid():
            form.save()
        url = '{}?tab=crypto'.format(reverse_lazy('users:settings', args=[self.request.user.pk]))
        return HttpResponseRedirect(url)


# account
class AddAccountView(LoginRequiredMixin, CustomGetFormMixin, AjaxResponseMixin, generic.CreateView):
    form_class = AccountForm
    model = Account
    template_name = "symbols/form_snippet.njk"


class EditAccountView(LoginRequiredMixin, CustomGetFormMixin, AjaxResponseMixin, generic.UpdateView):
    model = Account
    form_class = AccountForm
    template_name = "symbols/form_snippet.njk"


class DeleteAccountView(LoginRequiredMixin, CustomGetFormMixin, AjaxResponseMixin, generic.FormView):
    model = Account
    template_name = "symbols/form_snippet.njk"
    form_class = AccountSelectForm

    def form_valid(self, form):
        account = form.cleaned_data["account"]
        account.delete()
        return HttpResponse(json.dumps({"valid": True}), content_type="application/json")


# asset
class AddAssetView(LoginRequiredMixin, GetDepotMixin, GetFormWithDepotMixin, AjaxResponseMixin, generic.CreateView):
    model = Asset
    template_name = "symbols/form_snippet.njk"
    form_class = AssetForm


class EditAssetView(LoginRequiredMixin, CustomGetFormMixin, AjaxResponseMixin, generic.UpdateView):
    model = Asset
    template_name = "symbols/form_snippet.njk"
    form_class = AssetForm


class DeleteAssetView(LoginRequiredMixin, CustomGetFormMixin, AjaxResponseMixin, generic.FormView):
    model = Asset
    template_name = "symbols/form_snippet.njk"
    form_class = AssetSelectForm

    def form_valid(self, form):
        asset = form.cleaned_data["asset"]
        asset.delete()
        return HttpResponse(json.dumps({"valid": True}), content_type="application/json")


# trade
class AddTradeView(LoginRequiredMixin, GetDepotMixin, GetFormWithDepotAndInitialDataMixin, AjaxResponseMixin,
                   generic.CreateView):
    model = Trade
    form_class = TradeForm
    template_name = "symbols/form_snippet.njk"


class EditTradeView(LoginRequiredMixin, CustomGetFormMixin, AjaxResponseMixin, generic.UpdateView):
    model = Trade
    form_class = TradeForm
    template_name = "symbols/form_snippet.njk"


class DeleteTradeView(LoginRequiredMixin, CustomAjaxDeleteMixin, generic.DeleteView):
    model = Trade
    template_name = "symbols/delete_snippet.njk"


# transaction
class AddTransactionView(LoginRequiredMixin, GetDepotMixin, GetFormWithDepotAndInitialDataMixin, AjaxResponseMixin,
                         generic.CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "symbols/form_snippet.njk"


class EditTransactionView(LoginRequiredMixin, CustomGetFormMixin, AjaxResponseMixin, generic.UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "symbols/form_snippet.njk"


class DeleteTransactionView(LoginRequiredMixin, CustomAjaxDeleteMixin, generic.DeleteView):
    model = Transaction
    template_name = "symbols/delete_snippet.njk"


# flow
class AddFlowView(LoginRequiredMixin, GetDepotMixin, GetFormWithDepotAndInitialDataMixin, AjaxResponseMixin,
                  generic.CreateView):
    model = Flow
    form_class = FlowForm
    template_name = "symbols/form_snippet.njk"


class EditFlowView(LoginRequiredMixin, CustomGetFormMixin, AjaxResponseMixin, generic.UpdateView):
    model = Flow
    form_class = FlowForm
    template_name = "symbols/form_snippet.njk"


class DeleteFlowView(LoginRequiredMixin, CustomAjaxDeleteMixin, generic.DeleteView):
    model = Flow
    template_name = "symbols/delete_snippet.njk"
