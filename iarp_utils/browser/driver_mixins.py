import os


class FirefoxPrintToPDFMixin:

    def get_driver_options(self):
        opts = super().get_driver_options()

        # Print to PDF options
        opts.set_preference("print.printer_Mozilla_Save_to_PDF.print_to_file", True)
        opts.set_preference("print_printer", "Mozilla Save to PDF")
        opts.set_preference("print.always_print_silent", True)

        return opts


class FirefoxDisableGeoLocationAbilitiesMixin:

    def get_driver_options(self):
        opts = super().get_driver_options()

        opts.set_preference("geo.enabled", False)
        opts.set_preference("geo.provider.use_corelocation", False)
        opts.set_preference("geo.prompt.testing", False)
        opts.set_preference("geo.prompt.testing.allow", False)

        return opts


class FirefoxDisableGeckodriverLogMixin:

    def get_driver_service(self, *args, **kwargs):
        kwargs.setdefault('log_path', os.devnull)
        return super().get_driver_service(*args, **kwargs)
