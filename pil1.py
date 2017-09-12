from PIL import Image, ImageFilter


kitten = Image.open("kitten.jpg")
blurrykitten = kitten.filter(ImageFilter.GaussianBlur)
blurrykitten.save("kitten_blurred.jpg")
blurrykitten.show()