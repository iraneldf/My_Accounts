from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordChangeView, LoginView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from AlacenenesPyme import settings
from apps.account.forms import RegisterUserForm, UpdateUserForm, UpdateProfileForm

UserModel = get_user_model()


def create_mail(to, subject, template_name, context):
    from django.template.loader import get_template
    template = get_template(template_name)
    content = template.render(context)

    from django.core.mail import EmailMultiAlternatives
    message = EmailMultiAlternatives(
        subject=subject,
        body='',
        from_email=settings.EMAIL_HOST_USER,
        to=[to],
        cc=[]
    )
    message.attach_alternative(content, 'text/html')
    return message


class MyLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('alarmas')
        return super().dispatch(request, *args, **kwargs)


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Su contraseña ha sido cambiada con éxito"
    success_url = reverse_lazy('informacion')


class ChangePasswordViewRoot(SuccessMessageMixin, PasswordChangeView):
    form_class = SetPasswordForm
    template_name = 'users/change_passwordRoot.html'
    success_message = "La contraseña ha sido cambiada con éxito"

    def get_form_kwargs(self):
        user = get_object_or_404(UserModel, pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['user'] = user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.get_form_kwargs()['user']

        return context

    def get_success_url(self):
        return reverse('DetailsRoot', kwargs={'pk': self.get_form_kwargs()['user'].pk})


def get_host_url(request) -> str:
    if request.get_host().__contains__("127.0.0.1") or request.get_host().__contains__(
            "localhost"):
        host = 'http://'
    else:
        host = 'https://'
    # host += request.get_host() + '/'
    return host


def register(request):
    if request.user.is_authenticated:
        print('Already authenticated')
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            form = RegisterUserForm(request.POST)
            # RegisterUserForm is created from User model, all model field restrictions are checked to considerate it
            # a valid form
            if form.is_valid():
                print('Valid form')
                # Save user to database but with is_active = False
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                # Send confirmation email
                current_site = get_current_site(request)
                subject = 'Activa tu ' + current_site.domain + ' cuenta'
                to_email = form.cleaned_data.get('email')

                mail = create_mail(to_email, subject, 'registration/confirmation_mail.html', {
                    'host': get_host_url(request),
                    "domain": current_site.domain,
                    "user": user,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user)

                })
                mail.send(fail_silently=False)

                # Redirect user to login

                messages.success(request,
                                 'Por favor confirma su email para completar el registro antes de iniciar sesión.')
                return HttpResponseRedirect(reverse('login'))
            else:
                print('Invalid form: %s' % form.errors.as_data())
                print(type(form.errors.as_data()))
                if form.errors:
                    messages.info(request, 'Errores en el formulario')
                    for key, values in form.errors.as_data().items():
                        print("Bad value: %s - %s" % (key, values))
                        if key == 'username':
                            messages.info(request, 'Error input fields')
                            break
                        else:
                            for error_value in values:
                                print(error_value)
                                # print(type(error_value))
                                messages.info(request, '%s' % error_value.message)

                # return HttpResponseRedirect(reverse('usersAuth:register'))
                return render(request, 'registration/register.html',
                              {'form': form, 'messages': messages.get_messages(request)})
        else:
            form = RegisterUserForm()

            context = {'form': form}
            return render(request, 'registration/register.html', context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        # Redirect user to login
        messages.success(request, 'Su email se ha confirmado, puede proceder a autenticarse')
        return HttpResponseRedirect(reverse('login'))
    else:
        # from rest_framework import status
        return render(request, 'registration/fail_confirmation.html',
                      {'message': 'El link de activación es invalido o ha expirado'},
                      # status=status.HTTP_403_FORBIDDEN
                      )


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Sus datos han sido editados con éxito')
            return redirect(to='informacion')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'users/userUpdate.html',
                  {'empresa': request.user, 'user_form': user_form, 'profile_form': profile_form})


def profileRoot(request, pk):
    user = get_object_or_404(UserModel, pk=pk)

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Los datos de la empresa han sido editados con éxito')
            return HttpResponseRedirect(reverse('DetailsRoot', kwargs={'pk': user.pk}))
    else:
        user_form = UpdateUserForm(instance=user)
        profile_form = UpdateProfileForm(instance=user.profile)

    return render(request, 'users/userUpdate.html', {
        'empresa': user,
        'user_form': user_form,
        'profile_form': profile_form,
    })


class MyPasswordResetView(PasswordResetView):
    email_template_name = "registration/password_reset_mail_personalizado.html"
    html_email_template_name = "registration/password_reset_mail_personalizado.html"
    subject_template_name = "registration/password_reset_subject.txt"

    template_name = "registration/password_reset_form.html"


class CustomPasswordResetView(PasswordResetView):
    email_template_name = "registration/password_reset_mail_personalizado.html"
