import ads.forms
import ads.models
import ads.utils
import payments.models


class AdMixin(object):

    def get_contact_form_data(self):
        user = self.request.user

        data = dict(
            phone_number=user.phone_number,
            email=user.email,
            full_name=user.get_full_name(),
        )

        contact_detail = ads.models.ContactDetail.objects.filter(ad__user=user).last()
        if contact_detail:
            data = dict(
                phone_number=contact_detail.phone_number,
                email=contact_detail.email,
                full_name=contact_detail.full_name,
            )

        return data

    def validate_request(self, request):
        errors = dict()

        instance = None
        if hasattr(self, 'object'):
            instance = self.object

        form_data = self.prepare_form_data(request)
        form = self.form(form_data, instance=instance)
        if not form.is_valid():
            errors.update(form.errors)

        if instance:
            instance = ads.models.ContactDetail.objects.filter(ad=instance.pk).first()

        contact_form_data = self.prepare_contact_form_data(request)
        contact_form = self.contact_form(contact_form_data, instance=instance)
        if not contact_form.is_valid():
            errors.update(contact_form.errors)

        return form, contact_form, errors

    @staticmethod
    def prepare_form_data(request):
        form_data = dict(
            is_seller_private=request.POST.get('is_seller_private') == 'True'
        )

        keys = ['category', 'city', 'state', 'price', 'currency', 'title', 'description']
        form_data.update({key: request.POST.get(key) for key in keys})

        return form_data

    @staticmethod
    def prepare_contact_form_data(request):
        keys = ['email', 'full_name', 'phone_number']
        return {key: request.POST.get(key) for key in keys}

    @staticmethod
    def ad_payment(request, ad, return_url=True):
        premium_days = request.POST.get('premium_days')

        if premium_days:
            payment = payments.models.Payment.objects.create(
                cost=int(premium_days) * ads.utils.get_kwd_for_one_day(),
                premium_days=premium_days,
                user=request.user,
                ad=ad,
            )
            return payment.get_absolute_url() if return_url else payment

    def create_subcategories(self, request, ad):
        subcategories = {
            'cars': self.handle_cars,
            'mobile': self.handle_mobile,
            'real estate': self.handle_real_estate,
        }

        category = ad.category.name.lower()
        if category in subcategories:
            subcategories[category](request, ad)

    def handle_cars(self, request, ad):
        make = request.POST.get('make')
        model = request.POST.get('model')
        if model and make and model.isnumeric() and make.isnumeric():
            try:
                car_ad = ad.carad
            except ads.models.CarAd.DoesNotExist:
                car_ad = ads.models.CarAd(ad=ad)

            car_ad_form = ads.forms.CarAdForm(request.POST, instance=car_ad)
            if car_ad_form.is_valid():
                car_ad = car_ad_form.save(commit=False)
                car_ad.make = ads.models.CarMakeCategory.objects.filter(pk=int(make)).first()
                car_ad.model = ads.models.CarModelCategory.objects.filter(pk=int(model)).first()
                car_ad.save()
            else:
                car_ad.make = ads.models.CarMakeCategory.objects.filter(pk=int(make)).first()
                car_ad.model = ads.models.CarModelCategory.objects.filter(pk=int(model)).first()
                car_ad.save()

        self.delete_rest_of_related(ads.models.CarAd, ad)

    def handle_mobile(self, request, ad):
        brand = request.POST.get('brand')
        model = request.POST.get('model')

        if model and brand and model.isnumeric() and brand.isnumeric():
            try:
                mobile_ad = ad.mobilead
            except ads.models.MobileAd.DoesNotExist:
                mobile_ad = ads.models.MobileAd(ad=ad)

            mobile_ad.brand = ads.models.MobileBrandCategory.objects.filter(pk=int(brand)).first()
            mobile_ad.model = ads.models.MobileModelCategory.objects.filter(pk=int(model)).first()
            mobile_ad.save()

        self.delete_rest_of_related(ads.models.MobileAd, ad)

    def handle_real_estate(self, request, ad):
        purpose = request.POST.get('purpose')

        try:
            estate_ad = ad.realestatead
        except ads.models.RealEstateAd.DoesNotExist:
            estate_ad = ads.models.RealEstateAd(ad=ad)

        estate_ad_form = ads.forms.RealEstateAdForm(request.POST, instance=estate_ad)
        if estate_ad_form.is_valid():
            estate_ad = estate_ad_form.save(commit=False)
            if purpose in [c[0] for c in ads.models.RealEstateAd.CHOICES]:
                estate_ad.purpose = purpose
            estate_ad.save()
        else:
            estate_ad.purpose = purpose
            estate_ad.save()

        self.delete_rest_of_related(ads.models.RealEstateAd, ad)

    @staticmethod
    def delete_rest_of_related(current, ad):
        subcategories = [
            ads.models.CarAd, ads.models.MobileAd, ads.models.RealEstateAd,
        ]

        for sub in subcategories:
            if not sub == current:
                sub.objects.filter(ad=ad).delete()


class RelatedDataMixin(object):
    @staticmethod
    def get_related_data(ad):
        related = ad.get_related_object()
        if related:
            fields = {k: v for k, v in vars(related).items() if not k.startswith('_')}

            if isinstance(related, ads.models.CarAd):
                fields['make_name'] = getattr(related.make, 'name', None)
                fields['model_name'] = getattr(related.model, 'name', None)
                fields['mileage'] = related.mileage
                fields['year'] = related.year
                fields['body_style'] = related.body_style
            if isinstance(related, ads.models.RealEstateAd):
                fields['purpose'] = related.purpose
                fields['bedrooms'] = related.bedrooms
                fields['bathrooms'] = related.bathrooms
                fields['estate_type'] = related.estate_type
            if isinstance(related, ads.models.MobileAd):
                fields['brand_name'] = getattr(related.brand, 'name', None)
                fields['model_name'] = getattr(related.model, 'name', None)

            return fields

        return None
