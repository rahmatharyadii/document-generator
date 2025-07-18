from PIL import Image

image = Image.open("flowElastic.jpg")
image.save("flowElastic_fixed.jpg", dpi=(96, 96))  # atau dpi=(300, 300)
