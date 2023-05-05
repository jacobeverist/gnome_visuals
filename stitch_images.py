from PIL import Image


def merge(im1, im2):
    w = im1.size[0] + im2.size[0]
    h = max(im1.size[1], im2.size[1])
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (im1.size[0], 0))

    return im


def quad_merge(im1, im2, im3, im4):
    w1 = max(im1.size[0], im3.size[0])
    w2 = max(im2.size[0], im4.size[0])
    w = w1 + w2

    h1 = max(im1.size[1], im2.size[1])
    h2 = max(im3.size[1], im4.size[1])
    h = h1 + h2

    # w = max(im1.size[0], im3.size[0]) + max(im2.size[0], im4.size[0])
    # h = max(im1.size[1], im2.size[1]) + max(im3.size[1], im4.size[1])

    # h = im1.size[1] + im3.size[1]
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (w1, 0))
    im.paste(im3, (0, h1))
    im.paste(im4, (w1, h1))

    return im


def stitch_images(filenames, output_str, input_dir="", output_dir="out/"):
    for i in range(int(len(filenames) / 4)):
        im1 = Image.open(input_dir + filenames[i * 4 + 0])
        im2 = Image.open(input_dir + filenames[i * 4 + 1])
        im3 = Image.open(input_dir + filenames[i * 4 + 2])
        im4 = Image.open(input_dir + filenames[i * 4 + 3])

        result_img = quad_merge(im1, im2, im3, im4)

        # shrink it to 1/4
        (width, height) = (result_img.width // 4, result_img.height // 4)
        im_final = result_img.resize((width, height))
        print("saving", output_dir + output_str % (i + 1) )
        im_final.save(output_dir + output_str % (i + 1))


if __name__ == "__main__":
    feature_filenames = [
            "040_0001_2n_equal_binsize_PeriodicScalarEncoder_Features.png",
            "040_0001_2n_equal_period_PeriodicScalarEncoder_Features.png",
            "036_0001_prime_equal_binsize_PeriodicScalarEncoder_Features.png",
            "036_0001_prime_equal_period_PeriodicScalarEncoder_Features.png",

            "040_0002_2n_equal_binsize_PeriodicScalarEncoder_Features.png",
            "040_0002_2n_equal_period_PeriodicScalarEncoder_Features.png",
            "036_0002_prime_equal_binsize_PeriodicScalarEncoder_Features.png",
            "036_0002_prime_equal_period_PeriodicScalarEncoder_Features.png",

            "040_0003_2n_equal_binsize_PeriodicScalarEncoder_Features.png",
            "040_0003_2n_equal_period_PeriodicScalarEncoder_Features.png",
            "036_0003_prime_equal_binsize_PeriodicScalarEncoder_Features.png",
            "036_0003_prime_equal_period_PeriodicScalarEncoder_Features.png",
    ]

    heatmap_filenames = [
            "040_0001_2n_equal_binsize_PeriodicScalarEncoder_Similarity_Matrix_Projected_to_Real_Space.png",
            "040_0001_2n_equal_period_PeriodicScalarEncoder_Similarity_Matrix_Projected_to_Real_Space.png",
            "036_0001_prime_equal_binsize_PeriodicScalarEncoder_Similarity_Matrix_Projected_to_Real_Space.png",
            "036_0001_prime_equal_period_PeriodicScalarEncoder_Similarity_Matrix_Projected_to_Real_Space.png",

            "040_0002_2n_equal_binsize_PeriodicScalarEncoder_Similarity_Matrix_Projected_to_Real_Space.png",
            "040_0002_2n_equal_period_PeriodicScalarEncoder_Similarity_Matrix_Projected_to_Real_Space.png",
            "036_0002_prime_equal_binsize_PeriodicScalarEncoder_Similarity_Matrix_Projected_to_Real_Space.png",
            "036_0002_prime_equal_period_PeriodicScalarEncoder_Similarity_Matrix_Projected_to_Real_Space.png",

            "040_0003_2n_equal_binsize_PeriodicScalarEncoder_Similarity_Matrix_Projected_to_Real_Space.png",
            "040_0003_2n_equal_period_PeriodicScalarEncoder_Similarity_Matrix_Projected_to_Real_Space.png",
            "036_0003_prime_equal_binsize_PeriodicScalarEncoder_Similarity_Matrix_Projected_to_Real_Space.png",
            "036_0003_prime_equal_period_PeriodicScalarEncoder_Similarity_Matrix_Projected_to_Real_Space.png",
    ]

    feature_str = "Features_Compact_PeriodicScalar_w%d.png"
    heatmap_str = "Heatmap_PeriodicScalar_w%d.png"

    stitch_images(heatmap_filenames, heatmap_str)
    stitch_images(feature_filenames, feature_str)
