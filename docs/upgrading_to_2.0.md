# Upgrading to v2.0

The following guide seeks to alleviate potential issues when upgrading from `django-wm<2.0` to `django-wm>=2.0`.

⚠ **Breaking change** ⚠

Prior versions of `django-wm` omitted [migration files] for the `mentions` app that this package provides. This was an oversight: when running `manage.py makemigrations`, one or more migration files would be generated within the `django-wm` package installation. This can cause issues when/if `django-wm` is upgraded with changes to its concrete models.

Starting in **v2.0.1**, migrations for `mentions` app's _concrete_ models - models that are NOT [abstract base classes] - will be included with the package distribution. This way, new changes to those concrete models can be smoothly migrated in any environment that uses `django-wm`.

The following models are affected by the change:

- `mentions.HCard`
- `mentions.OutgoingWebmentionStatus`
- `mentions.SimpleMention`
- `mentions.Webmention`

**Notes**:

- **Database tables created by mentions models in v1.3.1 are identical to those created with v2.0.1**. Any database environment with up-to-date model migrations as of **v1.3.1** should be able to upgrade to **v2.0** with no impacts on data or database schemas.
- **Model _mixins_ are not affected**. Mixins are [abstract base classes], and do not generate migrations in the `mentions` app under any circumstances.
- **Models that inherit from mixins are also not affected**. You do not need to generate new migrations for your own apps if you inherit from these mixin classes.

## Manually upgrading migrations in a running application

If you are uncertain if your app will be adversely affected by this change, you may take the following steps to safely migrate your existing environment to `django-wm>=2.0`. This is a one-time process for the upgrade to **v2.0+**. All future upgrades for `django-wm` do not need to follow this same process.

⚠ **DO NOT** upgrade the `django-wm` package yet! You will need the generated migration files from your _current_ installation in order to follow this guide.

### Short version

- Backup any existing migrations for the `mentions` app from _inside_ the Python environment where `django-wm` is installed.
- Upgrade `django-wm`, then remove its migration files (don't run `manage.py migrate`).
- Replace your _old_ migrations, then run `manage.py makemigrations` to generate changes between your old migrations and the new code in `django-wm` package.
- Use `migrate mentions zero --fake` to remove the records of your _old_ migrations from your `django_migrations` database table.
- Uninstall then reinstall the `django-wm` package, resetting migrations back to the versions from this package (instead of those generated by your app).
- Use `migration mentions --fake` to reset the `django_migrations` records in your database.

### Long version

1. Navigate to the Python installation or virtual environment where `django-wm` is installed, and locate the `lib/site-packages/mentions` directory (where the installed code for this package resides). From there, copy the `migrations` directory and its contents to a safe location _outside_ the Python virtual environment.

   - The migration files here will be ones your Django project generated using the `makemigrations` command in **v1.3.1** and below.

2. Upgrade `django-wm` using `pip install --upgrade django-wm` (preferably, specify the version with `django-wm==2.0.1`).

   - This will install the _new_ migration file(s) introduced in **v2.0+**.

3. Again, navigate to `lib/site-packages/mentions` in the Python virtual environment. This time, _remove_ the `migrations` directory entirely.
4. Move your _old_ migration files (from Step 1) _back_ to `lib/site-packages/mentions` within your Python virtual environment.

   - Running `manage.py showmigrations mentions` from your Django project should show a list of your _old_ migration files.

5. From your Django project, run `manage.py makemigrations mentions`

   - This may create new migration files in the `mentions` app. These will cover the differences between your _old_ migrations and any new changes introduced in **v2.0+**.

6. Run `manage.py migrate`

   - Now your database should match the expected schema for `django-wm>=2.0`.

7. Run `manage.py migrate mentions zero --fake`

   - With `--fake`, your database schema remains unchanged. Only the `django_migrations` table is altered, adding or removing records of migrations that have been applied in that database.
   - `zero` removes records for all migrations for the app, making Django believe the `mentions` app has never been migrated before.
   - ⚠ **Don't forget that `--fake` flag, or it will DROP the tables for your models!**

8. Use `pip uninstall django-wm` to completely remove the package, then `pip install django-wm` to reinstall it.

   - This deletes your _old_ migration files and replaces them with the _new_ one(s) from PyPI.
   - If you specified a version (as is recommended) in Step 2, you should specify the same version now!

9. Run `manage.py migrate mentions --fake`

   - Similar to Step 7, this "fakes" the migrations for `mentions` back up to the latest available, adding records back to the `django_migrations` table.
   - ⚠ This assumes that **all** prior steps have been followed, so that the state of your database exactly matches the state of the migration file(s) included with your new `django-wm` installation. If, for any reason, the newly-installed `mention` migrations do not match your new database schema, you may end up with broken migrations, a mismatched schema, or data loss.

🎉 That's it! You are now ready to use and upgrade `django-wm` safely in the future, along with any migration files for new changes to its own concrete models. 😊

[migration files]: https://docs.djangoproject.com/en/4.0/topics/migrations/
[abstract base classes]: https://docs.djangoproject.com/en/4.0/topics/db/models/#abstract-base-classes
