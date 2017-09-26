from PIL import Image, ImageFilter


kitten = Image.open("test.jpeg")
blurrykitten = kitten.filter(ImageFilter.GaussianBlur)
blurrykitten.save("test_blurred.jpeg")
blurrykitten.show()