from django.db.models.signals import post_save, post_delete
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
from django.db import models

from finance.users.models import StandardUser
from finance.core.models import Timespan as CoreTimespan
from finance.core.models import Depot as CoreDepot

import pandas as pd
import numpy as np
import time


def init_alternative(user):
    pass


class Depot(CoreDepot):
    user = models.ForeignKey(StandardUser, editable=False, related_name="alternative_depots",
                             on_delete=models.CASCADE)

    # getters
    def get_movie(self):
        return self.movies.get(depot=self, alternative=None)


class Alternative(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE, related_name="alternatives")

    class Meta:
        unique_together = ("depot", "name")

    def __str__(self):
        return "{}".format(self.name)

    # getters
    def get_movie(self):
        return self.movies.get(depot=self.depot, alternative=self)


class Value(models.Model):
    alternative = models.ForeignKey(Alternative, related_name="values", on_delete=models.PROTECT)
    date = models.DateTimeField()
    value = models.DecimalField(decimal_places=2, max_digits=15, default=0)

    class Meta:
        unique_together = ("alternative", "date")

    def __str__(self):
        return "{} {} {}".format(self.alternative, self.get_date(), self.value)

    # getters
    def get_date(self):
        return timezone.localtime(self.date).strftime("%d.%m.%Y")


class Flow(models.Model):
    alternative = models.ForeignKey(Alternative, related_name="flows", on_delete=models.PROTECT)
    date = models.DateTimeField()
    flow = models.DecimalField(decimal_places=2, max_digits=15, default=0)

    class Meta:
        unique_together = ("alternative", "date")

    def __str__(self):
        return "{} {} {}".format(self.alternative, self.get_date(), self.flow)

    # getters
    def get_date(self):
        return timezone.localtime(self.date).strftime("%d.%m.%Y")


class Timespan(CoreTimespan):
    depot = models.ForeignKey(Depot, editable=False, related_name="timespans",
                              on_delete=models.CASCADE)

    # getters
    def get_start_date(self):
        return timezone.localtime(self.start_date).strftime("%d.%m.%Y %H:%M") if self.start_date else None

    def get_end_date(self):
        return timezone.localtime(self.end_date).strftime("%d.%m.%Y %H:%M") if self.end_date else None


class Movie(models.Model):
    update_needed = models.BooleanField(default=True)
    depot = models.ForeignKey(Depot, blank=True, null=True, related_name="movies",
                              on_delete=models.CASCADE)
    alternative = models.ForeignKey(Alternative, blank=True, null=True, related_name="movies", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("depot", "alternative")

    def __str__(self):
        text = "{} {}".format(self.depot, self.alternative).replace(" None", "")
        return text

    # getters
    def get_df(self, timespan=None):
        if timespan and timespan.start_date and timespan.end_date:
            pictures = self.pictures.filter(d__gte=timespan.start_date,
                                            d__lte=timespan.end_date)
        else:
            pictures = self.pictures
        pictures = pictures.order_by("d")
        pictures = pictures.values("d", "p", "v", "g", "cr", "ttwr", "ca", "cs")
        df = pd.DataFrame(list(pictures), dtype=np.float64)
        if df.empty:
            df = pd.DataFrame(columns=["d", "p", "v", "g", "cr", "ttwr", "ca", "cs"])
        return df

    def get_data(self, timespan=None):
        if timespan and timespan.start_date and timespan.end_date:
            pictures = self.pictures.filter(d__gte=timespan.start_date,
                                            d__lte=timespan.end_date)
        else:
            pictures = Picture.objects.filter(movie=self)
        pictures = pictures.order_by("d")
        data = dict()
        data["d"] = (pictures.values_list("d", flat=True))
        data["p"] = (pictures.values_list("p", flat=True))
        data["v"] = (pictures.values_list("v", flat=True))
        data["g"] = (pictures.values_list("g", flat=True))
        data["cr"] = (pictures.values_list("cr", flat=True))
        data["ttwr"] = (pictures.values_list("ttwr", flat=True))
        data["ca"] = (pictures.values_list("ca", flat=True))
        data["cs"] = (pictures.values_list("cs", flat=True))
        return data

    def get_values(self, user, keys, timespan=None):
        # user in args for query optimization and ease
        data = dict()
        start_picture = None
        end_picture = None
        if timespan and timespan.start_date:
            data["start_date"] = timespan.start_date.strftime(user.date_format)
            try:
                start_picture = self.pictures.filter(d__lt=timespan.start_date).latest("d")
            except ObjectDoesNotExist:
                pass
        if timespan and timespan.end_date:
            data["end_date"] = timespan.end_date.strftime(user.date_format)
            try:
                end_picture = self.pictures.filter(d__lte=timespan.end_date).latest("d")
            except ObjectDoesNotExist:
                pass
        else:
            try:
                end_picture = self.pictures.latest("d")
            except ObjectDoesNotExist:
                pass

        for key in keys:
            if start_picture and end_picture:
                data[key] = getattr(end_picture, key) - getattr(start_picture, key)
            elif end_picture:
                data[key] = getattr(end_picture, key)
            else:
                data[key] = 0
            if user.rounded_numbers:
                data[key] = round(data[key], 2)
                if data[key] == 0.00:
                    data[key] = "x"

        return data

    # init
    @staticmethod
    def init_movies(sender, instance, **kwargs):
        if sender is Alternative:
            depot = instance.depot
            Movie.objects.get_or_create(depot=depot, alternative=instance)
        elif sender is Depot:
            depot = instance
            Movie.objects.get_or_create(depot=depot, alternative=None)

    @staticmethod
    def init_update(sender, instance, **kwargs):
        if sender is (Value or Flow):
            q1 = Q(alternative=instance.alternative)
            q2 = Q(depot=instance.alternative.depot, alternative=None)
            movies = Movie.objects.filter(q1 | q2)
            movies.update(update_needed=True)

    # update
    def update(self):
        if self.alternative:
            df = self.calc_alternative()
        elif not self.alternative:
            df = self.calc_depot()
        else:
            raise Exception("Depot or alternative must be defined in a movie.")

        old_df = self.get_df()
        old_df.rename(columns={"d": "date", "v": "value", "cs": "current_sum", "g": "gain", "cr": "current_return",
                               "ttwr": "true_time_weighted_return", "p": "price", "ca": "current_amount"}, inplace=True)
        old_df.set_index("date", inplace=True)
        if self.alternative:
            old_df = old_df[["value", "current_sum", "gain", "current_return", "true_time_weighted_return"]]
        elif not self.alternative:
            old_df = old_df[["value", "current_sum", "gain", "current_return", "true_time_weighted_return"]]

        if old_df.equals(df[:len(old_df)]):
            df = df[len(old_df):]
        else:
            self.pictures.all().delete()

        pictures = list()
        if self.alternative:
            for index, row in df.iterrows():
                picture = Picture(
                    movie=self,
                    d=index,
                    v=row["value"],
                    cs=row["current_sum"],
                    g=row["gain"],
                    cr=row["current_return"],
                    p=row["price"],
                    ca=row["current_amount"]
                )
                pictures.append(picture)
        elif not self.alternative:
            for index, row in df.iterrows():
                picture = Picture(
                    movie=self,
                    d=index,
                    v=row["value"],
                    cs=row["current_sum"],
                    g=row["gain"],
                    cr=row["current_return"],
                    ttwr=row["true_time_weighted_return"]
                )
                pictures.append(picture)
        Picture.objects.bulk_create(pictures)

        self.update_needed = False
        self.save()

    @staticmethod
    def na_to_na_sum(df, column_name):
        column = df.columns.get_loc(column_name)
        for i in range(0, len(df)):
            if pd.isna(df.iloc[i, column]):
                notna_sum = 0
                for k in range(i - 1, -1, -1):
                    if pd.notna(df.iloc[k, column]):
                        notna_sum += df.iloc[k, column]
                    else:
                        break
                df.loc[df.index[i], "helper"] = notna_sum
        df.iloc[:, column] = df.loc[:, "helper"]
        df.drop(["helper"], axis=1, inplace=True)

    def calc_alternative(self):
        # values
        values = Value.objects.filter(alternative=self.alternative)
        values = values.values("date", "value")
        values_df = pd.DataFrame(list(values), dtype=np.float64).set_index("date")
        # flows
        flows = Flow.objects.filter(alternative=self.alternative)
        flows = flows.values("date", "flow")
        flows_df = pd.DataFrame(list(flows), dtype=np.float64).set_index("date")
        # df
        df = pd.concat([values_df, flows_df], sort=False)
        df.sort_index(inplace=True)
        # add flows into the value row
        Movie.na_to_na_sum(df, "flow")
        df = df.loc[pd.notna(df.loc[:, "value"])]
        if not df.empty:
            df = pd.concat([df, df.iloc[0:1]])
            df.sort_index(inplace=True)
            df.iloc[0, df.columns.get_loc("value")] = df.iloc[0, df.columns.get_loc("flow")]
            df.iloc[1, df.columns.get_loc("flow")] = 0
        # cs
        df.loc[:, "cs"] = df.loc[:, "flow"].rolling(window=len(df.loc[:, "flow"]), min_periods=1).sum()
        # g
        df.loc[:, "g"] = df.loc[:, "value"] - df.loc[:, "cs"]
        # cr
        df.loc[:, "cr"] = (df.loc[:, "value"] - df.loc[:, "cs"]) / df.loc[:, "cs"]
        # ttwr
        df.loc[:, "ttwr"] = df.loc[:, "value"] / (df.loc[:, "value"].shift(1) + df.loc[:, "flow"])
        df.loc[:, "ttwr"].fillna(1, inplace=True)
        df.loc[:, "ttwr"] = df.loc[:, "ttwr"].cumprod()
        df.loc[:, "ttwr"] = df.loc[:, "ttwr"] - 1
        # return
        return df

    def calc_depot(self):
        df = pd.DataFrame(columns=["value", "current_sum", "date"], dtype=np.float64)
        # alternatives
        alternatives = list()
        for alternative in self.depot.alternatives.all():
            movie = alternative.get_movie(self.depot)
            alternative_df = movie.get_df()
            alternative_df = alternative_df.loc[:, ["v", "d", "f"]]
            alternative_df.rename(columns={"v": alternative.name + "__v", "d": "date", "f": alternative.name + "__f"},
                                  inplace=True)
            alternatives.append(alternative.name)
            df = pd.concat([df, alternative_df], ignore_index=True, sort=False)
        # all together
        df.loc[:, "date"] = df.loc[:, "date"].dt.normalize()
        df.set_index("date", inplace=True)
        df.sort_index(inplace=True)
        df.ffill(inplace=True)
        df = df[~df.index.duplicated(keep="last")]
        # sum it up
        df.loc[:, "v"] = df.loc[:, [name + "__v" for name in alternatives]].sum(axis=1, skipna=True)
        df.loc[:, "f"] = df[:, [name + "__f" for name in alternatives]].sum(axis=1, skipna=True)
        # add flows into the value row
        Movie.na_to_na_sum(df, "flow")
        df = df.loc[pd.notna(df.loc[:, "value"])]
        if not df.empty:
            df = pd.concat([df, df.iloc[0:1]])
            df.sort_index(inplace=True)
            df.iloc[0, df.columns.get_loc("value")] = df.iloc[0, df.columns.get_loc("flow")]
            df.iloc[1, df.columns.get_loc("flow")] = 0
        # cs
        df.loc[:, "cs"] = df.loc[:, "flow"].rolling(window=len(df.loc[:, "flow"]), min_periods=1).sum()
        # g
        df.loc[:, "g"] = df.loc[:, "value"] - df.loc[:, "cs"]
        # cr
        df.loc[:, "cr"] = (df.loc[:, "value"] - df.loc[:, "cs"]) / df.loc[:, "cs"]
        # ttwr
        df.loc[:, "ttwr"] = df.loc[:, "value"] / (df.loc[:, "value"].shift(1) + df.loc[:, "flow"])
        df.loc[:, "ttwr"].fillna(1, inplace=True)
        df.loc[:, "ttwr"] = df.loc[:, "ttwr"].cumprod()
        df.loc[:, "ttwr"] = df.loc[:, "ttwr"] - 1
        # return
        return df


class Picture(models.Model):
    movie = models.ForeignKey(Movie, related_name="pictures", on_delete=models.CASCADE)
    d = models.DateTimeField()

    v = models.DecimalField(blank=True, null=True, max_digits=18, decimal_places=3)
    f = models.DecimalField(blank=True, null=True, max_digits=18, decimal_places=3)
    g = models.DecimalField(blank=True, null=True, max_digits=18, decimal_places=3)
    cr = models.DecimalField(blank=True, null=True, max_digits=18, decimal_places=3)
    ttwr = models.DecimalField(blank=True, null=True, max_digits=18, decimal_places=3)
    cs = models.DecimalField(blank=True, null=True, max_digits=18, decimal_places=3)


post_save.connect(Movie.init_update, sender=Value)
post_delete.connect(Movie.init_update, sender=Value)
post_save.connect(Movie.init_update, sender=Flow)
post_delete.connect(Movie.init_update, sender=Flow)
post_save.connect(Movie.init_movies, sender=Alternative)
post_save.connect(Movie.init_movies, sender=Depot)
