import glob
import hashlib
import os
import requests
import shutil
import time
import zipfile

from .strings import random_character_generator


class ZipFileWithPermissions(zipfile.ZipFile):
    """ Custom ZipFile class for handling file permissions.

        https://stackoverflow.com/questions/39296101/python-zipfile-removes-execute-permissions-from-binaries

        "Python zipfile removes execute permissions from binaries":
        The reason for this can be found in the _extract_member() method in zipfile.py,
        it only calls shutil.copyfileobj() which will write the output file without any execute bits.
    """
    def _extract_member(self, member, targetpath, pwd):
        if not isinstance(member, zipfile.ZipInfo):
            member = self.getinfo(member)

        target_path = super()._extract_member(member, targetpath, pwd)

        attr = member.external_attr >> 16
        if attr != 0:
            os.chmod(target_path, attr)
        return target_path


def generate_file_hash(opened_file, func=hashlib.md5):
    hasher = func()
    opened_file.seek(0)
    while True:
        buf = opened_file.read(104857600)
        if not buf:
            break
        hasher.update(buf)
    output = hasher.hexdigest()
    opened_file.seek(0)
    return output


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
    with ZipFileWithPermissions(zip_file) as zf:
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

    Change the unique filename pattern by supplying filename_format::

        {filename} - The files name.
        {value} - What value are we on attempting to make a unique filename.
        {extension} - The files extension.

        Default: {filename}_{value}.{extension}

    Examples:

        >>> unique_file_exists('/tmp', 'mypdf', 'pdf')
        /tmp/mypdf.pdf

        Assuming /tmp/mypdf.pdf exists:
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


def get_mime_types_as_str(joiner=','):
    """ Returns comma separated list of mime types for use in browser downloads.

    List from https://www.freeformatter.com/mime-types-list.html
    """
    return joiner.join(MIME_TYPES_LIST)


MIME_TYPES_LIST = [
    "application/andrew-inset",
    "application/applixware",
    "application/atom+xml",
    "application/atomcat+xml",
    "application/atomsvc+xml",
    "application/ccxml+xml,",
    "application/cdmi-capability",
    "application/cdmi-container",
    "application/cdmi-domain",
    "application/cdmi-object",
    "application/cdmi-queue",
    "application/cu-seeme",
    "application/davmount+xml",
    "application/dssc+der",
    "application/dssc+xml",
    "application/ecmascript",
    "application/emma+xml",
    "application/epub+zip",
    "application/exi",
    "application/font-tdpfr",
    "application/force-download",
    "application/hyperstudio",
    "application/ipfix",
    "application/java-archive",
    "application/java-serialized-object",
    "application/java-vm",
    "application/javascript",
    "application/json",
    "application/mac-binhex40",
    "application/mac-compactpro",
    "application/mads+xml",
    "application/marc",
    "application/marcxml+xml",
    "application/mathematica",
    "application/mathml+xml",
    "application/mbox",
    "application/mediaservercontrol+xml",
    "application/metalink4+xml",
    "application/mets+xml",
    "application/mods+xml",
    "application/mp21",
    "application/mp4",
    "application/msword",
    "application/mxf",
    "application/octet-stream",
    "application/oda",
    "application/oebps-package+xml",
    "application/ogg",
    "application/onenote",
    "application/patch-ops-error+xml",
    "application/pdf",
    "application/pgp-encrypted",
    "application/pgp-signature",
    "application/pics-rules",
    "application/pkcs10",
    "application/pkcs7-mime",
    "application/pkcs7-signature",
    "application/pkcs8",
    "application/pkix-attr-cert",
    "application/pkix-cert",
    "application/pkix-crl",
    "application/pkix-pkipath",
    "application/pkixcmp",
    "application/pls+xml",
    "application/postscript",
    "application/prs.cww",
    "application/pskc+xml",
    "application/rdf+xml",
    "application/reginfo+xml",
    "application/relax-ng-compact-syntax",
    "application/resource-lists+xml",
    "application/resource-lists-diff+xml",
    "application/rls-services+xml",
    "application/rsd+xml",
    "application/rss+xml",
    "application/rtf",
    "application/sbml+xml",
    "application/scvp-cv-request",
    "application/scvp-cv-response",
    "application/scvp-vp-request",
    "application/scvp-vp-response",
    "application/sdp",
    "application/set-payment-initiation",
    "application/set-registration-initiation",
    "application/shf+xml",
    "application/smil+xml",
    "application/sparql-query",
    "application/sparql-results+xml",
    "application/srgs",
    "application/srgs+xml",
    "application/sru+xml",
    "application/ssml+xml",
    "application/tei+xml",
    "application/thraud+xml",
    "application/timestamped-data",
    "application/vnd.3gpp.pic-bw-large",
    "application/vnd.3gpp.pic-bw-small",
    "application/vnd.3gpp.pic-bw-var",
    "application/vnd.3gpp2.tcap",
    "application/vnd.3m.post-it-notes",
    "application/vnd.accpac.simply.aso",
    "application/vnd.accpac.simply.imp",
    "application/vnd.acucobol",
    "application/vnd.acucorp",
    "application/vnd.adobe.air-application-installer-package+zip",
    "application/vnd.adobe.fxp",
    "application/vnd.adobe.xdp+xml",
    "application/vnd.adobe.xfdf",
    "application/vnd.ahead.space",
    "application/vnd.airzip.filesecure.azf",
    "application/vnd.airzip.filesecure.azs",
    "application/vnd.amazon.ebook",
    "application/vnd.americandynamics.acc",
    "application/vnd.amiga.ami",
    "application/vnd.android.package-archive",
    "application/vnd.anser-web-certificate-issue-initiation",
    "application/vnd.anser-web-funds-transfer-initiation",
    "application/vnd.antix.game-component",
    "application/vnd.apple.installer+xml",
    "application/vnd.apple.mpegurl",
    "application/vnd.aristanetworks.swi",
    "application/vnd.audiograph",
    "application/vnd.blueice.multipass",
    "application/vnd.bmi",
    "application/vnd.businessobjects",
    "application/vnd.chemdraw+xml",
    "application/vnd.chipnuts.karaoke-mmd",
    "application/vnd.cinderella",
    "application/vnd.claymore",
    "application/vnd.cloanto.rp9",
    "application/vnd.clonk.c4group",
    "application/vnd.cluetrust.cartomobile-config",
    "application/vnd.cluetrust.cartomobile-config-pkg",
    "application/vnd.commonspace",
    "application/vnd.contact.cmsg",
    "application/vnd.cosmocaller",
    "application/vnd.crick.clicker",
    "application/vnd.crick.clicker.keyboard",
    "application/vnd.crick.clicker.palette",
    "application/vnd.crick.clicker.template",
    "application/vnd.crick.clicker.wordbank",
    "application/vnd.criticaltools.wbs+xml",
    "application/vnd.ctc-posml",
    "application/vnd.cups-ppd",
    "application/vnd.curl.car",
    "application/vnd.curl.pcurl",
    "application/vnd.data-vision.rdz",
    "application/vnd.denovo.fcselayout-link",
    "application/vnd.dna",
    "application/vnd.dolby.mlp",
    "application/vnd.dpgraph",
    "application/vnd.dreamfactory",
    "application/vnd.dvb.ait",
    "application/vnd.dvb.service",
    "application/vnd.dynageo",
    "application/vnd.ecowin.chart",
    "application/vnd.enliven",
    "application/vnd.epson.esf",
    "application/vnd.epson.msf",
    "application/vnd.epson.quickanime",
    "application/vnd.epson.salt",
    "application/vnd.epson.ssf",
    "application/vnd.eszigno3+xml",
    "application/vnd.ezpix-album",
    "application/vnd.ezpix-package",
    "application/vnd.fdf",
    "application/vnd.fdsn.seed",
    "application/vnd.flographit",
    "application/vnd.fluxtime.clip",
    "application/vnd.framemaker",
    "application/vnd.frogans.fnc",
    "application/vnd.frogans.ltf",
    "application/vnd.fsc.weblaunch",
    "application/vnd.fujitsu.oasys",
    "application/vnd.fujitsu.oasys2",
    "application/vnd.fujitsu.oasys3",
    "application/vnd.fujitsu.oasysgp",
    "application/vnd.fujitsu.oasysprs",
    "application/vnd.fujixerox.ddd",
    "application/vnd.fujixerox.docuworks",
    "application/vnd.fujixerox.docuworks.binder",
    "application/vnd.fuzzysheet",
    "application/vnd.genomatix.tuxedo",
    "application/vnd.geogebra.file",
    "application/vnd.geogebra.tool",
    "application/vnd.geometry-explorer",
    "application/vnd.geonext",
    "application/vnd.geoplan",
    "application/vnd.geospace",
    "application/vnd.gmx",
    "application/vnd.google-earth.kml+xml",
    "application/vnd.google-earth.kmz",
    "application/vnd.grafeq",
    "application/vnd.groove-account",
    "application/vnd.groove-help",
    "application/vnd.groove-identity-message",
    "application/vnd.groove-injector",
    "application/vnd.groove-tool-message",
    "application/vnd.groove-tool-template",
    "application/vnd.groove-vcard",
    "application/vnd.hal+xml",
    "application/vnd.handheld-entertainment+xml",
    "application/vnd.hbci",
    "application/vnd.hhe.lesson-player",
    "application/vnd.hp-hpgl",
    "application/vnd.hp-hpid",
    "application/vnd.hp-hps",
    "application/vnd.hp-jlyt",
    "application/vnd.hp-pcl",
    "application/vnd.hp-pclxl",
    "application/vnd.hydrostatix.sof-data",
    "application/vnd.hzn-3d-crossword",
    "application/vnd.ibm.minipay",
    "application/vnd.ibm.modcap",
    "application/vnd.ibm.rights-management",
    "application/vnd.ibm.secure-container",
    "application/vnd.iccprofile",
    "application/vnd.igloader",
    "application/vnd.immervision-ivp",
    "application/vnd.immervision-ivu",
    "application/vnd.insors.igm",
    "application/vnd.intercon.formnet",
    "application/vnd.intergeo",
    "application/vnd.intu.qbo",
    "application/vnd.intu.qfx",
    "application/vnd.ipunplugged.rcprofile",
    "application/vnd.irepository.package+xml",
    "application/vnd.is-xpr",
    "application/vnd.isac.fcs",
    "application/vnd.jam",
    "application/vnd.jcp.javame.midlet-rms",
    "application/vnd.jisp",
    "application/vnd.joost.joda-archive",
    "application/vnd.kahootz",
    "application/vnd.kde.karbon",
    "application/vnd.kde.kchart",
    "application/vnd.kde.kformula",
    "application/vnd.kde.kivio",
    "application/vnd.kde.kontour",
    "application/vnd.kde.kpresenter",
    "application/vnd.kde.kspread",
    "application/vnd.kde.kword",
    "application/vnd.kenameaapp",
    "application/vnd.kidspiration",
    "application/vnd.kinar",
    "application/vnd.koan",
    "application/vnd.kodak-descriptor",
    "application/vnd.las.las+xml",
    "application/vnd.llamagraphics.life-balance.desktop",
    "application/vnd.llamagraphics.life-balance.exchange+xml",
    "application/vnd.lotus-1-2-3",
    "application/vnd.lotus-approach",
    "application/vnd.lotus-freelance",
    "application/vnd.lotus-notes",
    "application/vnd.lotus-organizer",
    "application/vnd.lotus-screencam",
    "application/vnd.lotus-wordpro",
    "application/vnd.macports.portpkg",
    "application/vnd.mcd",
    "application/vnd.medcalcdata",
    "application/vnd.mediastation.cdkey",
    "application/vnd.mfer",
    "application/vnd.mfmp",
    "application/vnd.micrografx.flo",
    "application/vnd.micrografx.igx",
    "application/vnd.mif",
    "application/vnd.mobius.daf",
    "application/vnd.mobius.dis",
    "application/vnd.mobius.mbk",
    "application/vnd.mobius.mqy",
    "application/vnd.mobius.msl",
    "application/vnd.mobius.plc",
    "application/vnd.mobius.txf",
    "application/vnd.mophun.application",
    "application/vnd.mophun.certificate",
    "application/vnd.mozilla.xul+xml",
    "application/vnd.ms-artgalry",
    "application/vnd.ms-cab-compressed",
    "application/vnd.ms-excel",
    "application/vnd.ms-excel.addin.macroenabled.12",
    "application/vnd.ms-excel.sheet.binary.macroenabled.12",
    "application/vnd.ms-excel.sheet.macroenabled.12",
    "application/vnd.ms-excel.template.macroenabled.12",
    "application/vnd.ms-fontobject",
    "application/vnd.ms-htmlhelp",
    "application/vnd.ms-ims",
    "application/vnd.ms-lrm",
    "application/vnd.ms-officetheme",
    "application/vnd.ms-pki.seccat",
    "application/vnd.ms-pki.stl",
    "application/vnd.ms-powerpoint",
    "application/vnd.ms-powerpoint.addin.macroenabled.12",
    "application/vnd.ms-powerpoint.presentation.macroenabled.12",
    "application/vnd.ms-powerpoint.slide.macroenabled.12",
    "application/vnd.ms-powerpoint.slideshow.macroenabled.12",
    "application/vnd.ms-powerpoint.template.macroenabled.12",
    "application/vnd.ms-project",
    "application/vnd.ms-word.document.macroenabled.12",
    "application/vnd.ms-word.template.macroenabled.12",
    "application/vnd.ms-works",
    "application/vnd.ms-wpl",
    "application/vnd.ms-xpsdocument",
    "application/vnd.mseq",
    "application/vnd.musician",
    "application/vnd.muvee.style",
    "application/vnd.neurolanguage.nlu",
    "application/vnd.noblenet-directory",
    "application/vnd.noblenet-sealer",
    "application/vnd.noblenet-web",
    "application/vnd.nokia.n-gage.data",
    "application/vnd.nokia.n-gage.symbian.install",
    "application/vnd.nokia.radio-preset",
    "application/vnd.nokia.radio-presets",
    "application/vnd.novadigm.edm",
    "application/vnd.novadigm.edx",
    "application/vnd.novadigm.ext",
    "application/vnd.oasis.opendocument.chart",
    "application/vnd.oasis.opendocument.chart-template",
    "application/vnd.oasis.opendocument.database",
    "application/vnd.oasis.opendocument.formula",
    "application/vnd.oasis.opendocument.formula-template",
    "application/vnd.oasis.opendocument.graphics",
    "application/vnd.oasis.opendocument.graphics-template",
    "application/vnd.oasis.opendocument.image",
    "application/vnd.oasis.opendocument.image-template",
    "application/vnd.oasis.opendocument.presentation",
    "application/vnd.oasis.opendocument.presentation-template",
    "application/vnd.oasis.opendocument.spreadsheet",
    "application/vnd.oasis.opendocument.spreadsheet-template",
    "application/vnd.oasis.opendocument.text",
    "application/vnd.oasis.opendocument.text-master",
    "application/vnd.oasis.opendocument.text-template",
    "application/vnd.oasis.opendocument.text-web",
    "application/vnd.olpc-sugar",
    "application/vnd.oma.dd2+xml",
    "application/vnd.openofficeorg.extension",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.presentationml.slide",
    "application/vnd.openxmlformats-officedocument.presentationml.slideshow",
    "application/vnd.openxmlformats-officedocument.presentationml.template",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformates-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
    "application/vnd.osgeo.mapguide.package",
    "application/vnd.osgi.dp",
    "application/vnd.palm",
    "application/vnd.pawaafile",
    "application/vnd.pg.format",
    "application/vnd.pg.osasli",
    "application/vnd.picsel",
    "application/vnd.pmi.widget",
    "application/vnd.pocketlearn",
    "application/vnd.powerbuilder6",
    "application/vnd.previewsystems.box",
    "application/vnd.proteus.magazine",
    "application/vnd.publishare-delta-tree",
    "application/vnd.pvi.ptid1",
    "application/vnd.quark.quarkxpress",
    "application/vnd.realvnc.bed",
    "application/vnd.recordare.musicxml",
    "application/vnd.recordare.musicxml+xml",
    "application/vnd.rig.cryptonote",
    "application/vnd.rim.cod",
    "application/vnd.rn-realmedia",
    "application/vnd.route66.link66+xml",
    "application/vnd.sailingtracker.track",
    "application/vnd.seemail",
    "application/vnd.sema",
    "application/vnd.semd",
    "application/vnd.semf",
    "application/vnd.shana.informed.formdata",
    "application/vnd.shana.informed.formtemplate",
    "application/vnd.shana.informed.interchange",
    "application/vnd.shana.informed.package",
    "application/vnd.simtech-mindmapper",
    "application/vnd.smaf",
    "application/vnd.smart.teacher",
    "application/vnd.solent.sdkm+xml",
    "application/vnd.spotfire.dxp",
    "application/vnd.spotfire.sfs",
    "application/vnd.spreadsheet-openxml",
    "application/vnd.stardivision.calc",
    "application/vnd.stardivision.draw",
    "application/vnd.stardivision.impress",
    "application/vnd.stardivision.math",
    "application/vnd.stardivision.writer",
    "application/vnd.stardivision.writer-global",
    "application/vnd.stepmania.stepchart",
    "application/vnd.sun.xml.calc",
    "application/vnd.sun.xml.calc.template",
    "application/vnd.sun.xml.draw",
    "application/vnd.sun.xml.draw.template",
    "application/vnd.sun.xml.impress",
    "application/vnd.sun.xml.impress.template",
    "application/vnd.sun.xml.math",
    "application/vnd.sun.xml.writer",
    "application/vnd.sun.xml.writer.global",
    "application/vnd.sun.xml.writer.template",
    "application/vnd.sus-calendar",
    "application/vnd.svd",
    "application/vnd.symbian.install",
    "application/vnd.syncml+xml",
    "application/vnd.syncml.dm+wbxml",
    "application/vnd.syncml.dm+xml",
    "application/vnd.tao.intent-module-archive",
    "application/vnd.tmobile-livetv",
    "application/vnd.trid.tpt",
    "application/vnd.triscape.mxs",
    "application/vnd.trueapp",
    "application/vnd.ufdl",
    "application/vnd.uiq.theme",
    "application/vnd.umajin",
    "application/vnd.unity",
    "application/vnd.uoml+xml",
    "application/vnd.vcx",
    "application/vnd.visio",
    "application/vnd.visio2013",
    "application/vnd.visionary",
    "application/vnd.vsf",
    "application/vnd.wap.wbxml",
    "application/vnd.wap.wmlc",
    "application/vnd.wap.wmlscriptc",
    "application/vnd.webturbo",
    "application/vnd.wolfram.player",
    "application/vnd.wordperfect",
    "application/vnd.wqd",
    "application/vnd.wt.stf",
    "application/vnd.xara",
    "application/vnd.xfdl",
    "application/vnd.yamaha.hv-dic",
    "application/vnd.yamaha.hv-script",
    "application/vnd.yamaha.hv-voice",
    "application/vnd.yamaha.openscoreformat",
    "application/vnd.yamaha.openscoreformat.osfpvg+xml",
    "application/vnd.yamaha.smaf-audio",
    "application/vnd.yamaha.smaf-phrase",
    "application/vnd.yellowriver-custom-menu",
    "application/vnd.zul",
    "application/vnd.zzazz.deck+xml",
    "application/voicexml+xml",
    "application/widget",
    "application/winhlp",
    "application/wsdl+xml",
    "application/wspolicy+xml",
    "application/x-7z-compressed",
    "application/x-abiword",
    "application/x-ace-compressed",
    "application/x-apple-diskimage",
    "application/x-authorware-bin",
    "application/x-authorware-map",
    "application/x-authorware-seg",
    "application/x-bcpio",
    "application/x-bittorrent",
    "application/x-bzip",
    "application/x-bzip2",
    "application/x-cdlink",
    "application/x-chat",
    "application/x-chess-pgn",
    "application/x-cpio",
    "application/x-csh",
    "application/x-debian-package",
    "application/x-director",
    "application/x-doom",
    "application/x-dtbncx+xml",
    "application/x-dtbook+xml",
    "application/x-dtbresource+xml",
    "application/x-dvi",
    "application/x-font-bdf",
    "application/x-font-ghostscript",
    "application/x-font-linux-psf",
    "application/x-font-otf",
    "application/x-font-pcf",
    "application/x-font-snf",
    "application/x-font-ttf",
    "application/x-font-type1",
    "application/x-font-woff",
    "application/x-futuresplash",
    "application/x-gnumeric",
    "application/x-gtar",
    "application/x-hdf",
    "application/x-java-jnlp-file",
    "application/x-latex",
    "application/x-mobipocket-ebook",
    "application/x-ms-application",
    "application/x-ms-wmd",
    "application/x-ms-wmz",
    "application/x-ms-xbap",
    "application/x-msaccess",
    "application/x-msbinder",
    "application/x-mscardfile",
    "application/x-msclip",
    "application/x-msdownload",
    "application/x-msmediaview",
    "application/x-msmetafile",
    "application/x-msmoney",
    "application/x-mspublisher",
    "application/x-msschedule",
    "application/x-msterminal",
    "application/x-mswrite",
    "application/x-netcdf",
    "application/x-pkcs12",
    "application/x-pkcs7-certificates",
    "application/x-pkcs7-certreqresp",
    "application/x-rar-compressed",
    "application/x-sh",
    "application/x-shar",
    "application/x-shockwave-flash",
    "application/x-silverlight-app",
    "application/x-stuffit",
    "application/x-stuffitx",
    "application/x-sv4cpio",
    "application/x-sv4crc",
    "application/x-tar",
    "application/x-tcl",
    "application/x-tex",
    "application/x-tex-tfm",
    "application/x-texinfo",
    "application/x-ustar",
    "application/x-wais-source",
    "application/x-x509-ca-cert",
    "application/x-xfig",
    "application/x-xpinstall",
    "application/xcap-diff+xml",
    "application/xenc+xml",
    "application/xhtml+xml",
    "application/xls",
    "application/xlsx",
    "application/xml",
    "application/xml-dtd",
    "application/xop+xml",
    "application/xslt+xml",
    "application/xspf+xml",
    "application/xv+xml",
    "application/yang",
    "application/yin+xml",
    "application/zip",
    "audio/adpcm",
    "audio/basic",
    "audio/midi",
    "audio/mp4",
    "audio/mpeg",
    "audio/ogg",
    "audio/vnd.dece.audio",
    "audio/vnd.digital-winds",
    "audio/vnd.dra",
    "audio/vnd.dts",
    "audio/vnd.dts.hd",
    "audio/vnd.lucent.voice",
    "audio/vnd.ms-playready.media.pya",
    "audio/vnd.nuera.ecelp4800",
    "audio/vnd.nuera.ecelp7470",
    "audio/vnd.nuera.ecelp9600",
    "audio/vnd.rip",
    "audio/webm",
    "audio/x-aac",
    "audio/x-aiff",
    "audio/x-mpegurl",
    "audio/x-ms-wax",
    "audio/x-ms-wma",
    "audio/x-pn-realaudio",
    "audio/x-pn-realaudio-plugin",
    "audio/x-wav",
    "chemical/x-cdx",
    "chemical/x-cif",
    "chemical/x-cmdf",
    "chemical/x-cml",
    "chemical/x-csml",
    "chemical/x-xyz",
    "image/bmp",
    "image/cgm",
    "image/g3fax",
    "image/gif",
    "image/ief",
    "image/jpeg",
    "image/ktx",
    "image/pjpeg",
    "image/png",
    "image/prs.btif",
    "image/svg+xml",
    "image/tiff",
    "image/vnd.adobe.photoshop",
    "image/vnd.dece.graphic",
    "image/vnd.djvu",
    "image/vnd.dvb.subtitle",
    "image/vnd.dwg",
    "image/vnd.dxf",
    "image/vnd.fastbidsheet",
    "image/vnd.fpx",
    "image/vnd.fst",
    "image/vnd.fujixerox.edmics-mmr",
    "image/vnd.fujixerox.edmics-rlc",
    "image/vnd.ms-modi",
    "image/vnd.net-fpx",
    "image/vnd.wap.wbmp",
    "image/vnd.xiff",
    "image/webp",
    "image/x-citrix-jpeg",
    "image/x-citrix-png",
    "image/x-cmu-raster",
    "image/x-cmx",
    "image/x-freehand",
    "image/x-icon",
    "image/x-pcx",
    "image/x-pict",
    "image/x-png",
    "image/x-portable-anymap",
    "image/x-portable-bitmap",
    "image/x-portable-graymap",
    "image/x-portable-pixmap",
    "image/x-rgb",
    "image/x-xbitmap",
    "image/x-xpixmap",
    "image/x-xwindowdump",
    "message/rfc822",
    "model/iges",
    "model/mesh",
    "model/vnd.collada+xml",
    "model/vnd.dwf",
    "model/vnd.gdl",
    "model/vnd.gtw",
    "model/vnd.mts",
    "model/vnd.vtu",
    "model/vrml",
    "text/calendar",
    "text/css",
    "text/csv",
    "text/html",
    "text/n3",
    "text/plain",
    "text/plain-bas",
    "text/prs.lines.tag",
    "text/richtext",
    "text/sgml",
    "text/tab-separated-values",
    "text/troff",
    "text/turtle",
    "text/uri-list",
    "text/vnd.curl",
    "text/vnd.curl.dcurl",
    "text/vnd.curl.mcurl",
    "text/vnd.curl.scurl",
    "text/vnd.fly",
    "text/vnd.fmi.flexstor",
    "text/vnd.graphviz",
    "text/vnd.in3d.3dml",
    "text/vnd.in3d.spot",
    "text/vnd.sun.j2me.app-descriptor",
    "text/vnd.wap.wml",
    "text/vnd.wap.wmlscript",
    "text/x-asm",
    "text/x-c",
    "text/x-fortran",
    "text/x-java-source,java",
    "text/x-pascal",
    "text/x-setext",
    "text/x-uuencode",
    "text/x-vcalendar",
    "text/x-vcard",
    "text/yaml",
    "video/3gpp",
    "video/3gpp2",
    "video/h261",
    "video/h263",
    "video/h264",
    "video/jpeg",
    "video/jpm",
    "video/mj2",
    "video/mp4",
    "video/mpeg",
    "video/ogg",
    "video/quicktime",
    "video/vnd.dece.hd",
    "video/vnd.dece.mobile",
    "video/vnd.dece.pd",
    "video/vnd.dece.sd",
    "video/vnd.dece.video",
    "video/vnd.fvt",
    "video/vnd.mpegurl",
    "video/vnd.ms-playready.media.pyv",
    "video/vnd.uvvu.mp4",
    "video/vnd.vivo",
    "video/webm",
    "video/x-f4v",
    "video/x-fli",
    "video/x-flv",
    "video/x-m4v",
    "video/x-ms-asf",
    "video/x-ms-wm",
    "video/x-ms-wmv",
    "video/x-ms-wmx",
    "video/x-ms-wvx",
    "video/x-msvideo",
    "video/x-sgi-movie",
    "x-conference/x-cooltalk",
]
