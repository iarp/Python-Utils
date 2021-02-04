from PIL import Image


def create_thumbnail(infile, outfile, width, height):
    """
    Args:
        infile: Name of file to open and create thumbnail from
        outfile: Name of the thumbnail file
        width: How wide?
        height: How tall?
    """
    thumb = width, height
    img = Image.open(infile)
    width, height = img.size

    if width > height:
        delta = width - height
        left = int(delta / 2)
        upper = 0
        right = height + left
        lower = height
    else:
        delta = height - width
        left = 0
        upper = int(delta / 2)
        right = width
        lower = width + upper

    img = img.crop((left, upper, right, lower))
    img.thumbnail(thumb, Image.ANTIALIAS)
    img.save(outfile)


def create_width_proportional_thumbnail(infile, outfile, width):
    img = Image.open(infile)
    wpercent = (width / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((width, hsize), Image.ANTIALIAS)
    img.save(outfile)
