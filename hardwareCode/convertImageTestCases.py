def test_insert_one_and_retrieve():
    import convertImage
    convertImage.store_image("captured_images/test.jpg") 
    convertImage.retrieve_image(1, "captured_images/output_image.jpg")