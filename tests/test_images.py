import io
from PIL import Image
import unittest

from iarp_utils.images import create_thumbnail, create_width_proportional_thumbnail


class TestImages(unittest.TestCase):

    def test_create_thumbnail(self):
        tmp = io.BytesIO()
        Image.new("RGBA", (400, 400)).save(tmp, format='PNG')

        outfile = io.BytesIO()
        outfile.name = 'test.png'

        wanted_width = 200
        wanted_height = 200

        create_thumbnail(tmp, outfile, wanted_width, wanted_height)

        width, height = Image.open(outfile).size
        self.assertEqual(wanted_width, width)
        self.assertEqual(wanted_height, height)

    def test_create_thumbnail_with_greater_width(self):
        tmp = io.BytesIO()
        Image.new("RGBA", (800, 400)).save(tmp, format='PNG')

        outfile = io.BytesIO()
        outfile.name = 'test.png'

        create_thumbnail(tmp, outfile, 600, 200)

        width, height = Image.open(outfile).size
        self.assertEqual(200, width)
        self.assertEqual(200, height)

    def test_create_width_proportional_thumbnail(self):
        tmp = io.BytesIO()
        Image.new("RGBA", (1200, 400)).save(tmp, format='PNG')

        outfile = io.BytesIO()
        outfile.name = 'test.png'

        wanted_width = 400
        expected_height = 133

        create_width_proportional_thumbnail(tmp, outfile, wanted_width)

        width, height = Image.open(outfile).size
        self.assertEqual(wanted_width, width)
        self.assertEqual(expected_height, height)
