from PIL import Image
import os


source_dir = "figures/examples/periodic_scalar_encoder_examples/v2"
target_dir = "figures/examples/periodic_scalar_encoder_examples/v3"


source_list = os.listdir(source_dir)

for filename in source_list:
    if filename.endswith(".png"):

        print(source_dir + "/" + filename)
        print(target_dir + "/" + filename)

        with Image.open(source_dir + "/" + filename) as im:

            (width, height) = (im.width // 4, im.height // 4)
            im_resized = im.resize((width, height))

            im_resized.save(target_dir + "/" + filename)


