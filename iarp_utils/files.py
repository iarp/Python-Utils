import glob
import os
import requests
import shutil
import time
import zipfile

from .strings import random_character_generator


def download_file(url: str, path_to_file):
    """ Download a file from a remote HTTP server.

    Examples:

        >>> download_file('https://www.google.ca', '/tmp/google_index.html')

    Args:
        url: URL to the file
        path_to_file: filename to save to locally
    """
    with requests.get(url, stream=True) as response, open(path_to_file, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)


def extract_zip_single_file(zip_file: str, file_to_extract: str, folder_to_extract_to: str, delete_zip_on_finish=True,
                            max_attempts=10, max_wait_in_seconds=30, log=None, **kwargs):
    """ Extracts a single file from a zip file.

    Examples:

        >>> extract_zip_single_file('/tmp/tmp.zip', 'driver.so', '/etc/my-app')

        # If the zip has a password
        >>> extract_zip_single_file('/tmp/tmp.zip', 'driver.so', '/etc/my-app', pwd='12345')

        >>> log = logging.getLogger('myLogger')
        >>> extract_zip_single_file('/tmp/tmp.zip', 'driver.so', '/etc/my-app', log=log)
        # if an extract failure happens, the following gets logged
        Unzip {file_to_extract} to {folder_to_extract_to} failed {attempt}/{max_attempts}.

    Args:
        zip_file: Path to the zip file
        file_to_extract: File within the zip file to extract
        folder_to_extract_to: Where to extract the file to
        delete_zip_on_finish: Remove the zip when done?
        max_attempts: How many times do we try reading the zip file if something has a lock on it?
        max_wait_in_seconds: How many seconds to we wait between attempts?
        log: If using logging, supply the logger here
        **kwargs: passed into zipfile.extract, namely for passworded zip files
    """
    # If another process happens to be running and is locked onto the zip file,
    # it'll raise PermissionError. Retry every 30 seconds for 10 attempts.
    with zipfile.ZipFile(zip_file) as zf:
        attempt = 0
        while attempt <= max_attempts:
            attempt += 1

            try:
                zf.extract(file_to_extract, folder_to_extract_to, **kwargs)
                break
            except PermissionError:
                if log:
                    log.exception(f'Unzip {file_to_extract} to {folder_to_extract_to} failed {attempt}/{max_attempts}.')
                time.sleep(max_wait_in_seconds)

    if delete_zip_on_finish:
        os.remove(zip_file)


def unique_file_exists(folder, filename, extension, filename_format="{filename}_{value}.{extension}", **kwargs):
    """ Ensures the file path given does not exist, returns a path to a file that does not exist.

    Example of a matching filename: test_#.pdf where # is however many iterations
        had to occur to find the unique name

    Change the unique filename pattern by supplying filename_format:
        {filename} - The files name.
        {value} - What value are we on attempting to make a unique filename.
        {extension} - The files extension.

        Default: {filename}_{value}.{extension}

    Examples:

        >>> unique_file_exists('/tmp', 'mypdf', 'pdf')
        /tmp/mypdf.pdf

        # Assuming /tmp/mypdf.pdf exists:
        >>> unique_file_exists('/tmp', 'mypdf', 'pdf')
        /tmp/mypdf_1.pdf

    Args:
        folder: Where to save the file
        filename: The name of the file without extension
        extension: The extension
        filename_format: If the file exists, this is the format for the new name.

    Returns:
        string containing valid filepath.
    """

    def get_appended_value(counter, use_counter=True, generator=random_character_generator, length=5):
        if use_counter:
            return counter
        return generator(length=length)

    path = os.path.join(folder, f"{filename}.{extension}")
    if not os.path.isfile(path):
        return path

    counter = 0
    while True:
        counter += 1

        new_filename = filename_format.format(
            filename=filename,
            value=get_appended_value(counter=counter, **kwargs),
            extension=extension,
        )

        path = os.path.join(folder, new_filename)
        if not os.path.isfile(path):
            return path


def wait_for_downloaded_file(glob_path, read_mode="rb", checks=10, max_wait_in_seconds=10):
    """ Checks the glob_path param for matching files and ensures they are not locked

    This is most useful when using selenium on a site that forces downloads
        rather than supplying a url to download from. It waits for the download
        to finish and then returns True.

    Examples:

        >>> wait_for_downloaded_file('/tmp/*.pdf')

    Args:
        glob_path: Path to check... C:/Apps/*.pdf
        read_mode: Default is rb
        checks: How many times to check
        max_wait_in_seconds: How many seconds to wait in between checks

    Returns:
        bool indicating a file was found
    """
    for c in range(checks + 1):

        time.sleep(max_wait_in_seconds)

        try:
            if [open(file, read_mode) for file in glob.glob(glob_path)]:
                return True
        except IOError:

            # Last iteration, just raise the error.
            if c == checks:
                raise

    return False
